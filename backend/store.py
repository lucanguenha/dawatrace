"""SQLite persistence + audit log for DawaTrace.

Everything that happens (a simulated SMS arriving, a reconciliation
calculation, an alert being raised, the agent's escalate/no-escalate
decision) is written here as an immutable event row. The dashboard reads
this table directly to build the "audit trail" the brief asks for -
there is no separate log format to keep in sync.
"""
import datetime
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dawatrace.db")


def _now():
    return datetime.datetime.now(datetime.UTC).isoformat()


@contextmanager
def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS clinics (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS drugs (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                dosage TEXT NOT NULL
            );

            -- Every simulated SMS: a REC (clinic reports what it received) or
            -- a DESP (warehouse reports what it dispatched). This table alone
            -- is the full audit trail of raw inputs.
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                kind TEXT NOT NULL CHECK (kind IN ('REC', 'DESP')),
                clinic_id TEXT NOT NULL REFERENCES clinics(id),
                drug_code TEXT NOT NULL REFERENCES drugs(code),
                qty INTEGER NOT NULL,
                raw_text TEXT NOT NULL,
                -- Which channel this reached us on. Same command format, same
                -- reconciliation engine either way - this column only exists
                -- so the audit trail can show the capability/access trade-off
                -- (SMS needs no data/smartphone; WhatsApp is the upgrade path
                -- for whoever already has both). Added 04/Oct/2026 per Lucas's
                -- note, see ADICAO_whatsapp.md.
                channel TEXT NOT NULL DEFAULT 'sms' CHECK (channel IN ('sms', 'whatsapp'))
            );

            -- One row per (clinic, drug) reconciliation outcome. Recomputed
            -- whenever a new event for that pair arrives; superseded rows are
            -- kept (never deleted) so the trail shows how the picture evolved.
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                clinic_id TEXT NOT NULL REFERENCES clinics(id),
                drug_code TEXT NOT NULL REFERENCES drugs(code),
                desp_total INTEGER NOT NULL,
                rec_total INTEGER NOT NULL,
                gap INTEGER NOT NULL,
                confidence REAL NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('ok', 'escalated', 'flagged')),
                explanation TEXT,
                escalation_reason TEXT,
                evidence_event_ids TEXT NOT NULL
            );
            """
        )


def seed_if_empty(clinics, drugs):
    with connect() as conn:
        n = conn.execute("SELECT COUNT(*) FROM clinics").fetchone()[0]
        if n > 0:
            return False
        conn.executemany("INSERT INTO clinics (id, name) VALUES (?, ?)", clinics)
        conn.executemany(
            "INSERT INTO drugs (code, name, dosage) VALUES (?, ?, ?)", drugs
        )
        return True


def insert_event(kind, clinic_id, drug_code, qty, raw_text, channel="sms"):
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO events (ts, kind, clinic_id, drug_code, qty, raw_text, channel) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (_now(), kind, clinic_id, drug_code, qty, raw_text, channel),
        )
        return cur.lastrowid


def totals_for(clinic_id, drug_code):
    with connect() as conn:
        rows = conn.execute(
            "SELECT kind, COALESCE(SUM(qty), 0) AS total FROM events "
            "WHERE clinic_id = ? AND drug_code = ? GROUP BY kind",
            (clinic_id, drug_code),
        ).fetchall()
        out = {"REC": 0, "DESP": 0}
        for r in rows:
            out[r["kind"]] = r["total"]
        return out


def evidence_events(clinic_id, drug_code, limit=20):
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM events WHERE clinic_id = ? AND drug_code = ? "
            "ORDER BY ts DESC LIMIT ?",
            (clinic_id, drug_code, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def insert_alert(clinic_id, drug_code, desp_total, rec_total, gap, confidence,
                  status, explanation, escalation_reason, evidence_event_ids):
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO alerts (ts, clinic_id, drug_code, desp_total, rec_total, "
            "gap, confidence, status, explanation, escalation_reason, evidence_event_ids) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (_now(), clinic_id, drug_code, desp_total, rec_total, gap, confidence,
             status, explanation, escalation_reason, ",".join(map(str, evidence_event_ids))),
        )
        return cur.lastrowid


def list_alerts(limit=50):
    with connect() as conn:
        rows = conn.execute(
            "SELECT a.*, c.name AS clinic_name, d.name AS drug_name, d.dosage AS drug_dosage "
            "FROM alerts a "
            "JOIN clinics c ON c.id = a.clinic_id "
            "JOIN drugs d ON d.code = a.drug_code "
            "ORDER BY a.id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def list_events(limit=200):
    with connect() as conn:
        rows = conn.execute(
            "SELECT e.*, c.name AS clinic_name, d.name AS drug_name, d.dosage AS drug_dosage "
            "FROM events e "
            "JOIN clinics c ON c.id = e.clinic_id "
            "JOIN drugs d ON d.code = e.drug_code "
            "ORDER BY e.id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def list_clinics():
    with connect() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM clinics ORDER BY id").fetchall()]


def list_drugs():
    with connect() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM drugs ORDER BY code").fetchall()]
