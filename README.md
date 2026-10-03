# DawaTrace

**Offline-first medicine stock reconciliation, over SMS and WhatsApp, for health
posts with no reliable internet, no smartphone requirement, and no dedicated
inventory staff.**

Built for Hack-Nation 7th Global AI Hackathon — Track 04a, World Bank:
*"Small AI for development, Track A: Health."*

## The problem

Rural clinics and the central warehouses that supply them run on paper
registers and phone calls. When a shipment of medicine doesn't fully arrive,
nobody finds out until a clinic physically runs out — and even then, nobody
can say *where* the gap happened, because the warehouse's records and the
clinic's records live in two different places that never talk to each other.

DawaTrace closes that loop using the only two channels that work everywhere
reporters already are: **SMS** (works on any phone with signal, zero mobile
data) and **WhatsApp** (an upgrade path for staff who already have a
smartphone and data — not a dependency). Both channels speak the exact same
tiny command language and feed the exact same reconciliation engine.

## How it works

1. A **health post** reports what it received:
   `REC 500 AMOX 250` → *received 500 units of Amoxicillin 250mg*
2. The **central warehouse** reports what it dispatched:
   `DESP 800 AMOX 250` → *dispatched 800 units of Amoxicillin 250mg*
3. The backend cross-references the two streams per (clinic, drug) and
   computes the gap **deterministically** — this number is never touched by
   an LLM.
4. A **confidence score**, also computed deterministically from the size of
   the gap, how many messages corroborate it, and how far apart in time the
   two reports arrived, decides what happens next:
   - High confidence → the gap is shown as a direct finding.
   - Low confidence → the system explicitly **escalates to a human** instead
     of asserting a conclusion it can't support. This is deliberate: a
     wrong accusation is worse than an honest "I'm not sure."
5. Claude (`claude-haiku-4-5`) reads the deterministic numbers and the raw
   evidence (the actual REC/DESP messages) and writes a short, plain-language
   explanation plus its own escalate/don't-escalate judgement, through one
   real tool-use call — it is structurally unable to invent or override the
   gap or confidence numbers; it can only explain them and decide what to
   recommend doing next.
6. Every message, calculation, and decision is written to an append-only
   audit trail (SQLite), shown on the dashboard with the exact evidence
   behind every alert.

**On tone**: DawaTrace never says "theft," "fraud," or assigns blame. The
language throughout is "reconciliation gap" / "visibility gap." The system
proves a number; it explicitly does not claim to know the cause — a gap can
be a transport delay, a reporting error, or a real loss, and conflating them
would be both inaccurate and harmful to the people being reported on.

## Architecture

```
web/                  Static dashboard (HTML + vanilla JS + Tailwind via CDN)
                       - SMS/WhatsApp channel toggle (same format, same API)
                       - Live audit trail + reconciliation alerts

backend/
  app.py               FastAPI app: intake -> reconcile -> explain -> store
  reconcile.py         Deterministic parsing, gap, and confidence score
  claude_agent.py      Single tool-use call to Claude for explanation +
                       escalation judgement (never touches the numbers)
  store.py             SQLite persistence + the append-only audit log
  seed_data.py         Synthetic clinics/drugs/history for the demo

data/dawatrace.db      SQLite database (created on first run, gitignored)
```

No real SMS/WhatsApp gateway integration — simulating the message transport
is an explicit, honest scope decision for a hackathon demo (see the tech
walkthrough video for why: Twilio/WhatsApp Business API require production
phone numbers and Meta business verification that can't happen in the time
available, and would not change anything about the actual reconciliation
logic, which is the part being judged).

## Running it

Requires Python 3.11+ and an Anthropic API key.

```bash
cp .env.example .env
# edit .env and paste your ANTHROPIC_API_KEY

./run.sh
```

Then open **http://localhost:8420**.

First run seeds 5 synthetic clinics, 4 synthetic drugs (Amoxicillin,
Paracetamol, an antimalarial ACT, and oral rehydration salts), and a handful
of historical reconciliation scenarios so the dashboard isn't empty —
including one clear flagged gap, one small ambiguous one that gets escalated
instead of asserted, and one clean no-gap pair. **Zero real patient data is
modelled anywhere** — this system only ever sees drug/dosage/quantity/clinic/
timestamp, never anything about a patient.

### Try the worked example from the brief

1. Channel: SMS. Clinic: `Clinic #14 - Beira Central`.
2. Clinic sends: `REC 500 AMOX 250`
3. Warehouse sends: `DESP 800 AMOX 250`
4. The reconciliation trail on the right shows a 300-unit gap, with Claude's
   plain-language explanation and its escalation judgement, within seconds.

## What's deliberately out of scope for this demo

- Real SMS/WhatsApp delivery (see above).
- Authentication / multi-tenant warehouses (one shared demo instance).
- Editing or deleting past events — the audit trail is append-only by
  design; corrections would be a new event, not a rewrite of history.

## Synthetic data disclosure

All clinic names, drug names/dosages, and quantities in this repository are
fictional, generated for demonstration purposes. No real patients, health
facilities, or stock data are represented anywhere in this codebase.
