# GUIA DE VÍDEOS E SUBMISSÃO — DawaTrace (Hack-Nation 7)
Escrito pela Luna, 4/Out/2026 18:10 Macau. Prazo: **21:00 Macau hoje** (09:00 ET, +15 min de tolerância).

## 0. O QUE A ORGANIZAÇÃO DISSE HOJE (dos emails que recebeste)

| Quem | O que disse |
|---|---|
| **Linn _(organizadora), 14:28** | "World Bank Challenge Clarification: **Submit 3 separate videos, max 1 min each: Team Intro, Demo & Teach.** No 3 a 5 min video required." |
| **Linn _, 11:18** | "**Record videos early.** Great lighting, music + visuals win." (exemplos: tinyurl.com/team-vid-26 e tinyurl.com/demo-vid-26) |
| **Kai Wiederhold (organizador), 15:39** | "Submission: **DO it both on app.hack-nation.ai AND our Google Forms**: https://forms.gle/VnivSgAJ2w5bZyJW9" |
| Discord | `simonj2` mencionou-te no canal #announcements (1 mensagem por ler) |

Bate certo com o HackOS: **3 vídeos de ≤60s cada** = Team Introduction, Product Demo, Technical Walkthrough (o "Teach" é o técnico).

---

## 1. ESPECIFICAÇÕES TÉCNICAS (não falhar isto)

- **3 vídeos, ≤60 segundos cada.** 60 exactos é aceitável; 61 pode ser rejeitado.
- Formato **MP4 ou MOV**. Se a plataforma rejeitar, exportar **H.264 MP4**.
- Máximo **1 GB por vídeo** (irrelevante, vão ter poucos MB).
- Idioma: **inglês**.
- Gravar **em horizontal** (16:9), não vertical.
- Som limpo. Se houver ruído de fundo, grava a voz à parte e junta.
- Fecha notificações do telefone/PC antes de gravar. Nada de notificações no ecrã.

### Truques que a organizadora deu (grátis, e são critério)
- **Luz de frente**, nunca janela atrás de ti (ficarias em contraluz). Uma lâmpada à frente da cara serve.
- Fala mais devagar do que te apetece. A pressa é o que estraga os primeiros 10 segundos.
- **Grava 2 vezes.** A segunda sai sempre melhor que a primeira.

---

## 2. VÍDEO 1 — TEAM INTRODUCTION (55s)

Objectivo: quem és, porque é que este problema é teu, e o que estás a construir. Um jurado decide nos primeiros 30 segundos.

**[0:00-0:10] — Abertura, sem preâmbulo**
> "I'm Lucas Nguenha. I spent seven years as a financial auditor in Mozambique, and I'm the only person on my team."

**[0:10-0:28] — O problema, concreto**
> "In health supply chains across emerging markets, medicine leaves a central warehouse and arrives at a rural clinic days later. Between those two points there is no shared system. When stock disappears, nobody can prove it happened, or where, or how much."

**[0:28-0:45] — O que fazes**
> "I'm building DawaTrace. It reconciles medicine stock and health spending over SMS, on any phone, with no app, no smartphone and no internet. It proves the gap, cites the evidence, and escalates to a human when it isn't sure."

**[0:45-0:55] — Porque tu**
> "I'm not an engineer. I'm an auditor applying a reconciliation problem I solved for a living to health systems that have far less infrastructure to work with."

**Planos:** cara à câmara. Nos 15 segundos finais podes ter o painel em segundo plano, se preferires. Sem cortes elaborados.

---

## 3. VÍDEO 2 — PRODUCT DEMO (58s)

**Este é o vídeo que decide.** É gravação de ecrã do fluxo a correr em https://projects.helpaz.net/dawatrace/ com a tua voz por cima. Nada de slides.

Antes de gravar: abre o link, faz **Ctrl+Shift+R** (recarregar sem cache), aumenta o zoom do browser (Ctrl e +) uma vez, e fecha tudo o resto.

**[0:00-0:12] — Define o cenário**
> "A central warehouse dispatches 800 boxes of amoxicillin to a rural clinic. This is what the clinic receives."

**[0:12-0:30] — Faz o fluxo ao vivo**
1. Clica **Send as Clinic** (`REC 500 AMOX 250`).
2. Clica **Send as Warehouse** (`DESP 800 AMOX 250`).
3. Aponta o rato para o alerta que aparece.
> "Two independent SMS reports. The system reconciles them and returns one number: 300 boxes unaccounted for, between the warehouse and Clinic #14."

**[0:30-0:50] — O painel (o que distingue isto de um script)**
Desce no **Reconciliation trail**. Abre o **View evidence** de um alerta.
> "Every alert carries its evidence line by line: which SMS produced it, who reported it and when. The confidence score is calculated in the backend, not by the model. Here it comes out at 23 percent, so the system escalates to a human instead of asserting a cause."
> "It never names the cause. It proves the number. The gap can be a transport delay, a recording error, or a real loss. That distinction belongs to a human."

**[0:50-0:58] — Fecho**
> "No app, no internet. Working today."

**Nota importante:** se ao gravar ainda vires algum texto de erro no painel, para e diz-me. Estou a corrigir isso agora.

---

## 4. VÍDEO 3 — TECHNICAL WALKTHROUGH / TEACH (58s)

Objectivo: provar que há engenharia a sério e que a decisão de escopo foi deliberada.

**[0:00-0:12] — Arquitectura em uma frase**
> "Four moving parts: an input layer, a reconciliation engine in Python, a reasoning layer, and an append-only audit trail."

**[0:12-0:32] — O motor (o mérito técnico)**
Abre `backend/reconcile.py` no editor, rola até à função do cálculo.
> "The gap is pure arithmetic: expected versus reported. It is computed deterministically, never by the model. The model only explains and decides whether to escalate. That separation is deliberate: a language model must not be allowed to invent a number."
> "Confidence is a function of corroboration and timing, not sentiment. Below the ceiling, the system escalates to a human. Here the ceiling is 55."

**[0:32-0:48] — Porque é "Small AI" (o critério do World Bank)**
> "The input layer is SMS and voice, because that is what a rural clinic actually has. The reasoning layer is provider-agnostic: it runs on a hosted model when there is connectivity and falls back to a deterministic explanation when there is not. That is the trade-off between capability and access, made explicit in the architecture."

**[0:48-0:58] — Honestidade técnica (isto pontua)**
> "What is simulated: the SMS gateway. In a real deployment that is a GSM modem and a short code. Everything downstream of the message is real code, running live."

**Se tiveres tempo:** abre o terminal e mostra `git log --oneline` e `./run.sh`. Um comando, a coisa sobe.

---

## 5. FOTO DE EQUIPA

- **JPG, PNG ou WebP · máximo 10 MB.**
- Equipa de 1: uma foto tua. Rosto visível, luz decente, fundo arrumado.
- Se quiseres dar leitura de "equipa", uma foto de trabalho (ao PC, com o DawaTrace no ecrã) funciona melhor que uma selfie de sofá.
- Não uses logótipos do World Bank nem de parceiros (o regulamento proíbe).

---

## 6. SUBMISSÃO — A PARTE QUE DESQUALIFICA SE FALHAR

**São DUAS submissões obrigatórias. Falhar uma = fora.**

### A) HackOS — https://app.hack-nation.ai
| Campo | O que pôr |
|---|---|
| Project name | `DawaTrace` |
| Challenge | `04a - World Bank: Small AI for development (Track A: Health)` |
| GitHub repository | `https://github.com/lucanguenha/dawatrace` (público, já confirmado) |
| Live project URL | `https://projects.helpaz.net/dawatrace/` (já verificado, HTTP 200) |
| Team photo | a que gravares |
| Team introduction | vídeo 1 (≤60s) |
| Product demo | vídeo 2 (≤60s) |
| Technical walkthrough | vídeo 3 (≤60s) |
| Descrição | ver secção 7 abaixo |

**"Save draft" NÃO é submeter.** Tem de aparecer **"Your project is submitted"**.

### B) Google Form — obrigatório
O organizador (Kai Wiederhold) publicou hoje no Luma: **https://forms.gle/VnivSgAJ2w5bZyJW9**

⚠️ **Atenção, há dois links diferentes:** o que estava guardado do brief de hoje de manhã é
`forms.gle/VS65tsovASMuBwEn9`. **Usa o link que aparecer DENTRO da página de submissão do
HackOS** (é o autoritativo). Se o HackOS não mostrar nenhum, usa o do Kai (o mais recente).
Se ambos existirem e forem formulários distintos, **submete os dois** — o custo é 2 minutos e o
custo de falhar é a desqualificação.

---

## 7. TEXTO DE SUBMISSÃO (pronto a colar)

**Título:** DawaTrace: proving where medicine disappears, over SMS

**Descrição curta:**
> DawaTrace reconciles medicine stock and health spending between a central warehouse and rural clinics using nothing but SMS and voice, on the phones people already own. Two independent reports, reconciled deterministically: a warehouse dispatch of 800 boxes against a clinic receipt of 500 returns one number, 300 unaccounted for, with the evidence line by line and a confidence score. When confidence is low, it escalates to a human instead of naming a cause it cannot prove. Built for 2G coverage, zero mobile data, no smartphone, no app.

**A frase que vale o prémio Best Quote ($500 em créditos):**
> "It does not tell you who took the medicine. It proves, with evidence, that the medicine is not there. The second is what an auditor can actually defend."

---

## 8. PRÉMIO "GO VIRAL" — $500, fecha às 21:00 (o mesmo prazo)

O post de LinkedIn está pronto em `/root/projects/vida/LinkedIn_HackNation.md`, em inglês, com a
marcação @Hack-Nation. Regra do prémio: **"Tag us by Sun, Oct 4, 9 am ET"** = 21:00 Macau hoje.
Custo: 15 minutos. É o melhor retorno por minuto de todo o evento.
