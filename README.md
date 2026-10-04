# DawaTrace

**Offline-first medicine stock reconciliation, over SMS and WhatsApp, for health
posts with no reliable internet, no smartphone requirement, and no dedicated
inventory staff.**

Built for Hack-Nation 7th Global AI Hackathon — Track 04a, World Bank:
*"Small AI for development, Track A: Health."*

## Try it in 60 seconds

A juror can test this directly, without watching the video.

**Live demo** (synthetic data already loaded, so the trail is never empty):
<https://projects.helpaz.net/dawatrace/>

1. Channel: **SMS**. Clinic: `Clinic #14 - Beira Central`.
2. Send as Clinic: `REC 500 AMOX 250` — the clinic reports receiving 500 units of Amoxicillin 250mg.
3. Send as Warehouse: `DESP 800 AMOX 250` — the warehouse reports dispatching 800 units of the same drug.
4. **Expected result, within seconds:** the reconciliation trail shows exactly one alert,
   `dispatched 800 · received 500 · gap 300`, with the evidence line by line (both messages, who
   sent them, when) and a deterministic confidence score. With only two corroborating messages
   and no transport record, confidence comes out low (around 23/100), so the system **escalates to
   a human** rather than asserting a cause. That escalation is the intended behaviour, not an
   error — the system refuses to state a cause it cannot prove.
5. The same flow works on the **WhatsApp** channel: identical command format, same reconciliation
   engine underneath.

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
5. A **provider-agnostic reasoning layer** reads the deterministic numbers and
   the raw evidence (the actual REC/DESP messages) and writes a short,
   plain-language explanation plus its own escalate/don't-escalate judgement.
   It tries Claude (`claude-haiku-4-5`) first, falls back to DeepSeek
   (`deepseek-chat`) if that provider is unavailable, and falls back again to
   a deterministic, template-based explanation built straight from the
   numbers if neither model answers - the demo never shows an error, and the
   dashboard never goes quiet just because one vendor's API had a bad moment.
   In every case, the layer is structurally unable to invent or override the
   gap or confidence numbers; it can only explain them and decide what to
   recommend doing next. This also means the reasoning step is not tied to
   one vendor, which matters directly for the brief's own framing of
   constrained environments: the same contract could be pointed at a locally
   hosted open-weight model with no code change beyond adding a provider
   function.
6. Every message, calculation, and decision is written to an append-only
   audit trail (SQLite), shown on the dashboard with the exact evidence
   behind every alert.

**On tone**: DawaTrace never says "theft," "fraud," or assigns blame. The
language throughout is "reconciliation gap" / "visibility gap." The system
proves a number; it explicitly does not claim to know the cause — a gap can
be a transport delay, a reporting error, or a real loss, and conflating them
would be both inaccurate and harmful to the people being reported on.

**On language**: the explanation layer writes in Portuguese, because that is
the working language of the clinics this is built for. That is a deliberate
choice, not a development artefact — the system prompt and the deterministic
fallback are each a single constant, so a deployment in another language
means editing two strings, not rebuilding the reasoning layer. The brief asks
for solutions designed around local languages; this is what that looks like
when the local language is not English. Mozambique's own national languages
(Changana, Macua) are a roadmap item, not a claim made here.

**On channels, delivered and roadmap**: the two channels that work in this
build are **SMS** (the transport is simulated, and that is declared, not
hidden) and **WhatsApp** (the same engine, offered as an upgrade path for
staff who already have a smartphone and data — not a dependency). Anything
else is explicitly roadmap, not capability: an interactive **voice / IVR**
channel is on the roadmap and is deliberately not counted today, precisely so
that nothing in this submission overstates what the demo actually does.

## Architecture

```
web/                  Static dashboard (HTML + vanilla JS + Tailwind via CDN)
                       - SMS/WhatsApp channel toggle (same format, same API)
                       - Live audit trail + reconciliation alerts

backend/
  app.py               FastAPI app: intake -> reconcile -> explain -> store
  reconcile.py         Deterministic parsing, gap, and confidence score
  claude_agent.py      Provider-agnostic reasoning layer: Claude, then DeepSeek,
                       then a deterministic fallback built from the same numbers
                       (never touches the gap or the confidence score)
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

Requires Python 3.11+. The reasoning layer works with an Anthropic API key,
falls back to a DeepSeek key if one is set, and still produces a complete
deterministic explanation if neither is — so the app runs with no keys at all.

```bash
cp .env.example .env
# edit .env and paste your ANTHROPIC_API_KEY (optional: DEEPSEEK_API_KEY)

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

## What's deliberately out of scope for this demo

- Real SMS/WhatsApp delivery (see above).
- Authentication / multi-tenant warehouses (one shared demo instance).
- Editing or deleting past events — the audit trail is append-only by
  design; corrections would be a new event, not a rewrite of history.

## Synthetic data disclosure

All clinic names, drug names/dosages, and quantities in this repository are
fictional, generated for demonstration purposes. No real patients, health
facilities, or stock data are represented anywhere in this codebase.
