"""DawaTrace backend: FastAPI app wiring the simulated-SMS intake, the
deterministic reconciliation engine, the Claude explain/escalate step, the
audit trail and the dashboard's static frontend together.

Run with:  python3 -m backend.app   (or: uvicorn backend.app:app --reload)
"""
import datetime
import os

from dotenv import load_dotenv

load_dotenv()  # ANTHROPIC_API_KEY lives in .env (gitignored) - see README for setup

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import store
from .claude_agent import explicar_e_decidir
from .reconcile import ParseError, compute_confidence, compute_gap, decide_status, parse_sms
from .seed_data import seed

WEB_DIR = os.path.join(os.path.dirname(__file__), "..", "web")

app = FastAPI(title="DawaTrace")


@app.on_event("startup")
def _startup():
    store.init_db()
    pairs = seed()
    if pairs:
        for clinic_id, drug_code in pairs:
            _reconcile_and_maybe_alert(clinic_id, drug_code)


class SmsIn(BaseModel):
    sender: str  # "clinic" | "warehouse" - who the simulator box represents
    clinic_id: str
    text: str


def _label(drug_row):
    return f"{drug_row['name']} {drug_row['dosage']}"


def _evidence_lines(events):
    out = []
    for e in events:
        who = "Clinic" if e["kind"] == "REC" else "Warehouse"
        out.append(f"[{e['ts'][:16].replace('T', ' ')}] {e['raw_text']}  ({who})")
    return out


@app.post("/api/sms")
def receive_sms(payload: SmsIn):
    expected_kind = "REC" if payload.sender == "clinic" else "DESP"
    try:
        kind, qty, drug_code, dosage = parse_sms(payload.text)
    except ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if kind != expected_kind:
        raise HTTPException(
            status_code=400,
            detail=f"Uma mensagem do {payload.sender} tem de começar por {expected_kind}, não {kind}.",
        )

    drugs = {d["code"]: d for d in store.list_drugs()}
    if drug_code not in drugs or drugs[drug_code]["dosage"] != dosage:
        raise HTTPException(
            status_code=400,
            detail=f"Medicamento/dosagem desconhecido: {drug_code} {dosage}. "
                   f"Conhecidos: {', '.join(f'{d['code']} {d['dosage']}' for d in drugs.values())}.",
        )
    clinics = {c["id"]: c for c in store.list_clinics()}
    if payload.clinic_id not in clinics:
        raise HTTPException(status_code=400, detail=f"Clínica desconhecida: {payload.clinic_id}")

    event_id = store.insert_event(kind, payload.clinic_id, drug_code, qty, payload.text.strip())

    alert = _reconcile_and_maybe_alert(payload.clinic_id, drug_code)
    return {"event_id": event_id, "parsed": {"kind": kind, "qty": qty, "drug": drug_code, "dosage": dosage},
            "alert": alert}


def _reconcile_and_maybe_alert(clinic_id, drug_code):
    totals = store.totals_for(clinic_id, drug_code)
    desp_total, rec_total = totals["DESP"], totals["REC"]
    gap, ratio = compute_gap(desp_total, rec_total)

    events = store.evidence_events(clinic_id, drug_code, limit=20)
    n_desp = sum(1 for e in events if e["kind"] == "DESP")
    n_rec = sum(1 for e in events if e["kind"] == "REC")

    hours_between = None
    desp_ts = [e["ts"] for e in events if e["kind"] == "DESP"]
    rec_ts = [e["ts"] for e in events if e["kind"] == "REC"]
    if desp_ts and rec_ts:
        d = datetime.datetime.fromisoformat(max(desp_ts))
        r = datetime.datetime.fromisoformat(max(rec_ts))
        hours_between = abs((d - r).total_seconds()) / 3600.0

    confidence = compute_confidence(desp_total, rec_total, ratio, n_desp, n_rec, hours_between)
    status = decide_status(confidence)

    if status == "ok":
        return {"status": "ok", "gap": gap, "confidence": confidence}

    clinics = {c["id"]: c for c in store.list_clinics()}
    drugs = {d["code"]: d for d in store.list_drugs()}
    clinic_name = clinics[clinic_id]["name"]
    drug_label = _label(drugs[drug_code])

    decision = explicar_e_decidir(
        clinic_name, drug_label, desp_total, rec_total, gap, confidence, status,
        _evidence_lines(events),
    )

    final_status = "escalated" if decision.get("escalar") else "flagged"
    alert_id = store.insert_alert(
        clinic_id, drug_code, desp_total, rec_total, gap, confidence, final_status,
        decision.get("explicacao", ""), decision.get("motivo", ""),
        [e["id"] for e in events],
    )
    return {
        "status": final_status, "alert_id": alert_id, "gap": gap, "confidence": confidence,
        "clinic_name": clinic_name, "drug_label": drug_label,
        "explanation": decision.get("explicacao"), "reason": decision.get("motivo"),
        "model_fallback": decision.get("fallback", False),
    }


@app.get("/api/alerts")
def api_alerts():
    return store.list_alerts()


@app.get("/api/events")
def api_events():
    return store.list_events()


@app.get("/api/clinics")
def api_clinics():
    return store.list_clinics()


@app.get("/api/drugs")
def api_drugs():
    return store.list_drugs()


# --- static frontend --------------------------------------------------------
app.mount("/assets", StaticFiles(directory=WEB_DIR), name="assets")


@app.get("/")
def index():
    return FileResponse(os.path.join(WEB_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="0.0.0.0", port=8420, reload=False)
