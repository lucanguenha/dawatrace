const API = "";
let currentChannel = "sms";

function setChannel(channel) {
  currentChannel = channel;
  const isSms = channel === "sms";
  document.getElementById("smsMode").classList.toggle("hidden", !isSms);
  document.getElementById("waMode").classList.toggle("hidden", isSms);
  document.getElementById("chanSmsBtn").className =
    "px-3 py-1.5 font-medium " + (isSms ? "bg-slate-700 text-white" : "bg-slate-900 text-slate-400");
  document.getElementById("chanWaBtn").className =
    "px-3 py-1.5 font-medium " + (!isSms ? "bg-slate-700 text-white" : "bg-slate-900 text-slate-400");
  document.getElementById("channelNote").textContent = isSms
    ? "Works on any phone with signal, zero mobile data required — the lowest common denominator for rural clinics."
    : "Upgrade path for staff who already have a smartphone and mobile data — same format, same engine underneath.";
}

async function loadClinics() {
  const res = await fetch(`${API}/api/clinics`);
  const clinics = await res.json();
  const sel = document.getElementById("clinicSelect");
  sel.innerHTML = clinics.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
  // Default to Clinic #14, the one used in the brief's worked example.
  const beira = clinics.find(c => c.name.includes("#14"));
  if (beira) sel.value = beira.id;
}

function statusBadge(status) {
  const map = {
    ok: ["bg-emerald-900/50 text-emerald-300 border-emerald-700", "OK — reconciled"],
    escalated: ["bg-amber-900/50 text-amber-300 border-amber-700", "ESCALATED — needs human review"],
    flagged: ["bg-rose-900/50 text-rose-300 border-rose-700", "FLAGGED — visibility gap"],
  };
  const [cls, label] = map[status] || ["bg-slate-800 text-slate-300 border-slate-700", status];
  return `<span class="text-xs px-2 py-0.5 rounded border ${cls}">${label}</span>`;
}

function confidenceBar(c) {
  const pct = Math.max(0, Math.min(100, c));
  const color = pct >= 55 ? "bg-rose-500" : pct > 0 ? "bg-amber-500" : "bg-emerald-500";
  return `
    <div class="flex items-center gap-2 mt-1">
      <div class="flex-1 h-1.5 bg-slate-800 rounded overflow-hidden">
        <div class="${color} h-full" style="width:${pct}%"></div>
      </div>
      <span class="mono text-xs text-slate-400">${pct.toFixed(0)}%</span>
    </div>`;
}

async function loadAlerts() {
  const res = await fetch(`${API}/api/alerts`);
  const alerts = await res.json();
  const el = document.getElementById("alertsList");
  if (!alerts.length) {
    el.innerHTML = `<p class="text-sm text-slate-500">No reconciliation gaps yet — send some SMS on the left.</p>`;
    return;
  }
  el.innerHTML = alerts.map(a => {
    const sign = a.gap > 0 ? "missing" : a.gap < 0 ? "excess reported" : "no gap";
    return `
    <div class="border border-slate-800 rounded-lg p-3 bg-slate-950/40">
      <div class="flex items-center justify-between gap-2">
        <div class="text-sm font-medium">${a.clinic_name} · ${a.drug_name} ${a.drug_dosage}</div>
        ${statusBadge(a.status)}
      </div>
      <div class="text-xs text-slate-400 mt-1 mono">
        dispatched ${a.desp_total} · received ${a.rec_total} · gap ${Math.abs(a.gap)} (${sign})
      </div>
      ${confidenceBar(a.confidence)}
      ${a.explanation ? `<p class="text-sm text-slate-200 mt-2">${a.explanation}</p>` : ""}
      ${a.escalation_reason ? `<p class="text-xs text-slate-500 mt-1 italic">${a.escalation_reason}</p>` : ""}
      <details class="mt-2">
        <summary class="text-xs text-sky-400 cursor-pointer">View evidence (event ids)</summary>
        <div class="mono text-xs text-slate-500 mt-1">#${a.evidence_event_ids}</div>
      </details>
    </div>`;
  }).join("");
}

async function loadEvents() {
  const res = await fetch(`${API}/api/events`);
  const events = await res.json();
  const el = document.getElementById("eventsList");
  el.innerHTML = events.slice(0, 30).map(e => {
    const color = e.kind === "REC" ? "text-emerald-400" : "text-sky-400";
    const chanIcon = e.channel === "whatsapp" ? "💬" : "📟";
    return `<div class="${color}">[${e.ts.slice(0,16).replace('T',' ')}] ${chanIcon} ${e.kind} ${e.qty} ${e.drug_code} ${e.drug_dosage} — ${e.clinic_name}</div>`;
  }).join("");
}

async function refreshAll() {
  await Promise.all([loadAlerts(), loadEvents()]);
}

function _readInput(sender) {
  if (currentChannel === "whatsapp") {
    const el = document.getElementById(sender === "clinic" ? "clinicTextWa" : "warehouseTextWa");
    return (el.innerText || el.textContent || "").trim();
  }
  const el = document.getElementById(sender === "clinic" ? "clinicText" : "warehouseText");
  return el.value.trim();
}

async function sendSms(sender) {
  const clinicId = document.getElementById("clinicSelect").value;
  const text = _readInput(sender);
  const resultEl = document.getElementById("smsResult");
  resultEl.innerHTML = `<span class="text-slate-500">Sending…</span>`;
  try {
    const res = await fetch(`${API}/api/sms`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sender, clinic_id: clinicId, text, channel: currentChannel }),
    });
    const data = await res.json();
    if (!res.ok) {
      resultEl.innerHTML = `<span class="text-rose-400">${data.detail}</span>`;
      return;
    }
    if (data.alert.status === "ok") {
      resultEl.innerHTML = `<span class="text-emerald-400">Received. No reconciliation gap (yet).</span>`;
    } else if (data.alert.status === "pending") {
      const who = data.alert.waiting_for === "warehouse" ? "the warehouse's dispatch report" : "the clinic's receipt report";
      resultEl.innerHTML = `<span class="text-sky-400">Received. Waiting for ${who} before reconciling.</span>`;
    } else {
      resultEl.innerHTML = `<span class="text-amber-400">Received. Gap detected, see trail on the right.</span>`;
    }
    await refreshAll();
  } catch (e) {
    resultEl.innerHTML = `<span class="text-rose-400">Network error: ${e}</span>`;
  }
}

setChannel("sms");
loadClinics().then(refreshAll);
setInterval(refreshAll, 8000);
