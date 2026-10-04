# ROADMAP DA NOITE — DawaTrace (Hack-Nation 7)

Escrito pela Luna, 4/Out/2026 ~05:55 Macau. Prazo: 21:00 Macau (+15min). Lucas a dormir.
Este ficheiro e o meu mapa — reviso-o a cada checkpoint para nao me perder nem repetir trabalho.

**Regra de ouro:** se um passo falhar 3x, paro, registo em BLOQUEIOS.md, salto para o
proximo item que nao dependa dele, e só acordo o Lucas se for Nivel 3/4 ou bloqueio real
sem alternativa.

---

## CHECKPOINT 0 — Setup (05:55-06:15) ✅ FEITO
- [x] Estrutura de pastas + git init em /root/projects/dawatrace
- [x] Spec completa escrita para o Claude Code (PEDIDO_CLAUDE_CODE.md)
- [x] Chave Anthropic confirmada no ~/.hermes/.env
- [x] Pedido disparado ao Claude Code via pedir_ao_claude_code.py (06:02 Macau)
- [x] Confirmado a trabalhar (explorou estrutura, a planear) — 06:03 Macau

## CHECKPOINT 1 — Caminho feliz ponta-a-ponta (06:15-10:00, ~4h) ✅ FEITO (pelo Claude Code, por confirmar pela Luna)
Objectivo: ver REC + DESP a gerar um ALERT no painel, nem que seja feio.
- [x] Simulador de SMS (2 caixas de texto: Clinic / Warehouse)
- [x] Motor de reconciliacao (cruza REC vs DESP, calcula desvio) — backend/reconcile.py
- [x] Painel mostra o alerta gerado — testado com o exemplo exacto do brief (REC 500 /
      DESP 800 AMOX 250 em Clinic #14 -> gap 300)
- [x] CHECK: `git log --oneline` tem 4 commits pequenos; `ls backend/ web/` confere
- [x] CHECK: app corre com `./run.sh` numa pasta limpa (sem .venv nem data/dawatrace.db)

## CHECKPOINT 2 — Inteligencia (10:00-13:00, ~3h) ✅ FEITO
Objectivo: o agente explica a anomalia, cita evidencia, decide escalar ou nao.
- [x] Integracao Claude (claude-haiku-4-5, tool-use real) — backend/claude_agent.py
- [x] Confidence score (calculado deterministicamente, nao pelo LLM) — backend/reconcile.py
- [x] Escalonamento humano quando confidence baixo (ESCALATION_CEILING=55)
- [x] CHECK: testado com 3 cenarios (C02/PARA gap grande corroborado -> escalated a 46%;
      C04/ACT gap pequeno isolado -> escalated a 11.5%; C05/ORS sem gap -> ok, sem alerta)
- NOTA: ver PERGUNTAS.md #1 — o cenario scripted principal tambem sai "escalated" (23%),
  nao "flagged" directo. Decisao de produto, nao bloqueio — continuei com o comportamento
  actual.

## CHECKPOINT 3 — Polimento + dados (13:00-15:30, ~2h30) 🟡 PARCIAL
- [x] Dados sinteticos (5 clinicas, 4 medicamentos: Amox, Paracetamol, ACT, ORS)
- [x] Trilha de auditoria completa visivel no painel (quem, quando, evidencia, canal)
- [x] UI decente (tailwind CDN)
- [x] Canal duplo SMS/WhatsApp (pedido extra via ADICAO_whatsapp.md) — mesmo formato,
      mesmo motor, so a UI distingue
- [ ] ElevenLabs (voz) — NAO FEITO, fica para se houver tempo (nice-to-have, como previsto)

## CHECKPOINT 4 — Publicacao tecnica (15:30-17:00, ~1h30) ✅ FEITO (a parte minha)
- [x] README.md em ingles, com o problema, a arquitectura, como correr, e o passo-a-passo
      do exemplo do brief
- [x] App preparada para correr com 1 comando (`./run.sh`, testado do zero)
- [ ] Live demo link — NAO fiz, como o pedido original instruiu explicitamente ("nao te
      preocupes com isso agora"). Fica para quando decidirem o tunnel/porto publico.
- [ ] GitHub: NAO criei repo nem fiz push, como instruido. Trabalho todo em commits locais
      (4 commits em /root/projects/dawatrace, `git log --oneline` para ver).

## CHECKPOINT 5 — Videos + submissao (17:00-20:00, ~3h) — REQUER O LUCAS
Isto NAO posso fazer sozinha: precisa da cara/voz dele nos videos (team intro, pitch) e da
decisao final de submeter. Aqui o trabalho passa a ser COM ele, nao por ele.
- [ ] Team photo
- [ ] 3 videos ≤60s (team intro, product demo, tech walkthrough)
- [ ] Guiao do pitch escrito e pronto para ensaiar
- [ ] GitHub publico criado (precisa do token dele)
- [ ] Live demo link testado

## CHECKPOINT 6 — Submissao final (20:00-21:00) — REQUER O LUCAS
- [ ] Submeter no HackOS
- [ ] Submeter no Google Form (OBRIGATORIO, dupla submissao)
- [ ] Confirmar "Your project is submitted"
- [ ] Congelar — nao tocar mais em nada

---

## Como eu (Luna) vou usar isto esta noite
1. ~~Disparo o Checkpoint 0 agora.~~ FEITO 06:02 Macau.
2. De ~90 em 90 minutos, verifico o progresso real (git log, ls, correr a app) — nao
   confio so no que o Claude Code diz que fez.
3. Actualizo as caixas [ ] -> [x] neste ficheiro a cada verificacao.
4. Se um checkpoint atrasar MUITO (ex: Checkpoint 1 ainda nao terminou as 11h), corto
   escopo no Checkpoint 3 (ElevenLabs e o primeiro a cair) para nao comprometer os
   checkpoints 5-6 que precisam do Lucas acordado.
5. Ficheiro de bloqueios reais: /root/projects/dawatrace/BLOQUEIOS.md (crio se precisar).
6. Nao acordo o Lucas por nada que resolvo sozinha. Acordo-o cedo se houver algo de
   Nivel 3/4 real (ex: o GitHub token) para nao perder tempo mais tarde.

## Log de verificacoes
- 06:03 Macau — Claude Code confirmado a trabalhar (explorou estrutura, a planear).
- 06:1x Macau — Progresso real visto: backend com SmsIn, reconciliacao a ser verificada.
- 06:1x Macau — Lucas sugeriu WhatsApp em vez de SMS. Decisao: SMS fica principal (bate no
  brief oficial "offline-capable, devices people already have"), WhatsApp entra como
  canal OPCIONAL (mesmo motor, UI diferente) — responde ao criterio oficial "capability
  vs access trade-offs". Enviado como ADICAO_whatsapp.md, nao-bloqueante, apos Claude Code
  ficar livre (~8min de espera, script correcto nao interrompeu trabalho em curso).
