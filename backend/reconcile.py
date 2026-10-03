"""Deterministic reconciliation engine.

Per the brief: the deviation number and the confidence score are NEVER
invented by the LLM. This module is the single source of truth for both -
the Claude agent (claude_agent.py) only ever receives these numbers, it
never recomputes or overrides them.

Parsing: REC/DESP SMS lines look like
    REC 500 AMOX 250
    DESP 800 AMOX 250
i.e. <KIND> <QTY> <DRUG_CODE> <DOSAGE>. The drug code + dosage together
resolve to one row in the drugs table (seed_data.py creates them with
matching codes, e.g. "AMOX" / "250").
"""
import re

SMS_RE = re.compile(r"^\s*(REC|DESP)\s+(\d+)\s+([A-Za-z]+)\s+(\S+)\s*$", re.IGNORECASE)


class ParseError(ValueError):
    pass


def parse_sms(text):
    """Returns (kind, qty, drug_code, dosage) or raises ParseError."""
    m = SMS_RE.match(text or "")
    if not m:
        raise ParseError(
            "Formato não reconhecido. Esperado: 'REC <qtd> <medicamento> <dosagem>' "
            "ou 'DESP <qtd> <medicamento> <dosagem>' (ex: REC 500 AMOX 250)."
        )
    kind, qty, drug, dosage = m.groups()
    return kind.upper(), int(qty), drug.upper(), dosage


# Gaps smaller than this (as a fraction of what was dispatched) are treated as
# rounding/packing noise, not a reconciliation gap worth raising at all.
NOISE_TOLERANCE = 0.02


def compute_gap(desp_total, rec_total):
    """Returns (gap, gap_ratio). gap > 0 means fewer boxes were received than
    dispatched (the case the brief cares about: 'missing between warehouse and
    clinic'). gap < 0 means the clinic reported MORE than was dispatched -
    also worth surfacing (double counting, or a dispatch that was never
    logged), just framed differently in the explanation."""
    gap = desp_total - rec_total
    ratio = abs(gap) / desp_total if desp_total > 0 else (1.0 if rec_total else 0.0)
    return gap, ratio


def compute_confidence(desp_total, rec_total, gap_ratio, n_desp_events, n_rec_events,
                        hours_between_latest_events):
    """0-100: how confident we are that this gap reflects a REAL, actionable
    reconciliation issue (as opposed to normal reporting lag or a single
    noisy data point). Deliberately simple and auditable - a judge reading
    this function should be able to recompute it by hand from the numbers
    shown on the dashboard.

    Pushes CONFIDENCE DOWN (i.e. towards "escalate to a human instead of
    asserting") when:
      - there's only one data point on either side (one bad SMS can't prove
        a pattern),
      - the two reports are far apart in time (could simply be that the
        clinic hasn't reported receipt yet - a timing lag, not a loss),
      - the gap is small relative to the volume shipped (rounding, partial
        box counts).
    Pushes it UP when the gap is large, corroborated by multiple events on
    both sides, and the reports arrived close together in time (so a timing
    lag is an unlikely explanation).
    """
    if gap_ratio <= NOISE_TOLERANCE:
        return 0.0

    base = min(gap_ratio, 1.0) * 70.0  # size of the gap does most of the work, capped

    corroboration = min(n_desp_events, n_rec_events)
    if corroboration <= 1:
        base *= 0.5
    elif corroboration >= 3:
        base += 15.0

    # Reports arriving close together make "it's just delayed reporting"
    # an unlikely explanation, so confidence rises; far apart, confidence
    # falls. 12h is the knee of the curve - chosen because clinics in this
    # scenario are assumed to send same-day reports under normal operation.
    if hours_between_latest_events is not None:
        if hours_between_latest_events <= 12:
            base += 10.0
        elif hours_between_latest_events >= 72:
            base *= 0.6

    return round(max(0.0, min(base, 100.0)), 1)


# Below this, we refuse to assert a reconciliation issue and escalate to a
# human instead - this is the "the agent prefers to say I don't know" rule
# from the brief, enforced in code so the LLM can't talk its way past it.
ESCALATION_CEILING = 55.0


def decide_status(confidence):
    if confidence <= 0:
        return "ok"
    if confidence < ESCALATION_CEILING:
        return "escalated"
    return "flagged"
