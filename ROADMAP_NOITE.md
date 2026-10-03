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

## CHECKPOINT 1 — Caminho feliz ponta-a-ponta (06:15-10:00, ~4h) 🔵 EM CURSO
Objectivo: ver REC + DESP a gerar um ALERT no painel, nem que seja feio.
- [ ] Simulador de SMS (2 caixas de texto: Clinic / Warehouse)
- [ ] Motor de reconciliacao (cruza REC vs DESP, calcula desvio)
- [ ] Painel mostra o alerta gerado
- [ ] CHECK ~07:30: correr `git log --oneline` e `ls backend/ web/` — ver progresso real
- [ ] CHECK ~09:00: tentar correr a app localmente e ver se sobe sem erro
- [ ] CHECK ~10:00: fechar o checkpoint, avaliar atraso vs plano

## CHECKPOINT 2 — Inteligencia (10:00-13:00, ~3h)
Objectivo: o agente explica a anomalia, cita evidencia, decide escalar ou nao.
- [ ] Integracao Claude (haiku/sonnet) para explicar o alerta em linguagem simples
- [ ] Confidence score (calculado deterministicamente, nao pelo LLM)
- [ ] Escalonamento humano quando confidence baixo
- [ ] CHECK: testar com 2-3 cenarios (desvio real, desvio pequeno/ambiguo, sem desvio)

## CHECKPOINT 3 — Polimento + dados (13:00-15:30, ~2h30)
- [ ] Dados sinteticos realistas (5 clinicas, 3-4 medicamentos tipo Amox/Paracetamol/ACT)
- [ ] Trilha de auditoria completa visivel no painel (quem, quando, evidencia)
- [ ] UI decente (tailwind CDN, nao precisa ser perfeita)
- [ ] Integracao ElevenLabs (voz) SE houver tempo — e nice-to-have, nao bloqueia o resto
- [ ] CHECK: screenshot do painel, ver se "bate" com o cartaz ja feito

## CHECKPOINT 4 — Publicacao tecnica (15:30-17:00, ~1h30)
- [ ] README.md em ingles, claro, com o problema + como correr
- [ ] App preparada para correr com 1 comando
- [ ] Live demo link — expor a app publicamente (tunnel ou porto do servidor)
- [ ] ACORDAR O LUCAS SE: precisar de criar o repo GitHub (preciso do token dele) — isto e
      bloqueio real, nao decisao estetica. Senao deixo para quando ele acordar organicamente.

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
