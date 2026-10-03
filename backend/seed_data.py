"""Synthetic clinics, drugs and historical SMS traffic.

Zero real data: names are fictional, numbers are made up for demo purposes.
No patient data of any kind is modelled anywhere in this system - only
stock/logistics events (drug, dosage, quantity, clinic, timestamp).
"""
import datetime
import random

from . import store

CLINICS = [
    ("C01", "Clinic #14 - Beira Central"),
    ("C02", "Clinic #22 - Nampula Norte"),
    ("C03", "Clinic #07 - Maputo Catembe"),
    ("C04", "Clinic #31 - Tete Moatize"),
    ("C05", "Clinic #09 - Quelimane Sede"),
]

DRUGS = [
    ("AMOX", "Amoxicillin", "250"),
    ("PARA", "Paracetamol", "500"),
    ("ACT", "Artemether-Lumefantrine (ACT)", "20/120"),
    ("ORS", "Oral Rehydration Salts", "standard"),
]

WAREHOUSE_LABEL = "Central Warehouse"


def _hours_ago(h):
    return datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=h)


def seed():
    """Returns a set of (clinic_id, drug_code) pairs that need an initial
    reconciliation pass, or None if seeding had already happened before
    (nothing new to reconcile)."""
    created = store.seed_if_empty(CLINICS, DRUGS)
    if not created:
        return None

    rng = random.Random(42)  # deterministic demo data, reproducible across runs

    # Deliberate scenarios matching the brief's 3 demo cases, seeded as
    # HISTORY so the dashboard already looks populated before the live
    # REC/DESP boxes are used for the actual 60s demo on Clinic #14/AMOX.
    deliberate = [
        # clear, large, well-corroborated gap -> should FLAG directly
        ("C02", "PARA", 600, 420, 48),
        ("C02", "PARA", 600, 430, 36),
        ("C02", "PARA", 600, 410, 24),
        # small gap, single data point, recent -> ESCALATE (ambiguous)
        ("C04", "ACT", 120, 115, 2),
        # no gap at all -> ok
        ("C05", "ORS", 300, 300, 10),
    ]

    for clinic_id, drug_code, desp_qty, rec_qty, hours_ago in deliberate:
        store_pair(clinic_id, drug_code, desp_qty, rec_qty, hours_ago)

    # Calm baseline (no gap) for every OTHER clinic/drug combo, so the
    # dashboard/audit trail looks like a real operating system rather than
    # 3 isolated incidents. Pairs already used above are skipped on purpose -
    # mixing a clean baseline into a deliberate scenario's own (clinic, drug)
    # totals would dilute its gap ratio and could flip "flagged"/"escalated"
    # back to "ok" (found exactly this bug while testing: C04/ACT's intended
    # ESCALATE case vanished because a clean baseline batch landed on the
    # same key and pulled the gap ratio under the noise tolerance).
    # C01/AMOX is reserved for the LIVE 60s demo exactly as scripted in the
    # brief (REC 500 / DESP 800 / "~300 missing") - no baseline noise there,
    # so the numbers on screen during the demo are exactly what was typed.
    used = {(c, d) for c, d, *_ in deliberate} | {("C01", "AMOX")}
    for clinic_id, _ in CLINICS:
        for drug_code, _, _ in DRUGS:
            if (clinic_id, drug_code) in used:
                continue
            qty = rng.choice([100, 150, 200, 250, 300])
            store_pair(clinic_id, drug_code, qty, qty, 200 + rng.randint(0, 40))

    # Expose which (clinic, drug) pairs need reconciliation run on them right
    # after seeding, so the dashboard isn't empty on first load. app.py calls
    # this back in its startup hook (kept here, not in app.py, to avoid a
    # circular import between the two modules).
    return {(c, d) for c, d, *_ in deliberate}


def store_pair(clinic_id, drug_code, desp_qty, rec_qty, hours_ago):
    """Writes a synthetic DESP + REC pair directly (bypassing the live
    /api/sms endpoint, since this is bulk historical seeding, not a demo
    interaction) and timestamps them to look like real history."""
    import sqlite3

    desp_ts = (_hours_ago(hours_ago)).isoformat()
    rec_ts = (_hours_ago(hours_ago - 1)).isoformat()  # clinic reports ~1h after dispatch

    dosage = next(d for c, _, d in DRUGS if c == drug_code)
    with store.connect() as conn:
        conn.execute(
            "INSERT INTO events (ts, kind, clinic_id, drug_code, qty, raw_text) VALUES (?,?,?,?,?,?)",
            (desp_ts, "DESP", clinic_id, drug_code, desp_qty, f"DESP {desp_qty} {drug_code} {dosage}"),
        )
        conn.execute(
            "INSERT INTO events (ts, kind, clinic_id, drug_code, qty, raw_text) VALUES (?,?,?,?,?,?)",
            (rec_ts, "REC", clinic_id, drug_code, rec_qty, f"REC {rec_qty} {drug_code} {dosage}"),
        )


if __name__ == "__main__":
    pairs = seed()
    print(f"seeded, {len(pairs)} pairs to reconcile" if pairs is not None else "already seeded, skipped")
