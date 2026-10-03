PEDIDO — Construir DawaTrace (hackathon, 15h restantes, Hack-Nation 7 / World Bank track)

CONTEXTO
O Lucas (meu operador) esta a competir no Hack-Nation 7th Global AI Hackathon, track
"04a - World Bank: Small AI for development (Track A: Health)". Prazo de submissao:
2026-10-04 21:00 Asia/Macau (+15min tolerancia). Ele foi dormir - trabalha sozinho (equipa
de 1) e eu (Luna) estou a orquestrar a construcao enquanto ele descansa. Preciso que
construas o produto de forma AUTONOMA esta noite. Repara: o Lucas NAO e engenheiro (e
auditor financeiro), por isso o codigo e todo teu, mas a logica de negocio vem de mim.

BRIEF OFICIAL DO TRACK (li no HackOS, texto exacto):
"Build AI that works where connectivity, devices and infrastructure are constrained.
Create a targeted, offline-capable solution for health, agriculture or tourism, designed
around local languages, real-world data and the devices people already have."

Avaliacao oficial do World Bank: merito tecnico + relevancia para o desenvolvimento +
design e inclusividade (reconhecer trade-offs capacidade/acesso).

O PRODUTO: "DawaTrace"
Sistema de reconciliacao de stock de medicamentos e despesa de saude por SMS e voz, para
locais sem internet/smartphone. Fluxo (e o que tem de aparecer na demo, fim a fim,
funcional, em 60 segundos):

1. Um POSTO DE SAUDE "manda" um SMS a reportar o que recebeu:
   REC 500 AMOX 250   (formato: REC <quantidade> <medicamento> <dosagem>)
2. O ARMAZEM CENTRAL "manda" um SMS a reportar o que despachou:
   DESP 800 AMOX 250  (formato: DESP <quantidade> <medicamento> <dosagem>)
3. O sistema CRUZA os dois e devolve, tambem em formato SMS simples:
   ALERT: 300 boxes missing between warehouse and Clinic #14 - AMOX 250
4. Um PAINEL WEB (para o gestor/auditor) mostra a TRILHA COMPLETA: cada evento, quem
   reportou, quando, o desvio calculado, a EVIDENCIA citada linha a linha (que SMS geraram
   aquele alerta), e um CONFIDENCE SCORE da anomalia.
5. Quando o confidence score e baixo (ex: pode ser atraso de transporte, nao
   necessariamente perda real), o sistema ESCALA PARA HUMANO em vez de acusar - isto e
   importante, os jurados preferem ver o agente a recusar decidir com certeza baixa do que
   inventar uma certeza que nao tem.

IMPORTANTE SOBRE TOM: o produto NAO acusa ninguem de roubo. E "reconciliation" e
"visibility gap", nunca "desvio" ou "fraude" nos textos/UI. O gap pode ser atraso de
transporte, erro de registo, ou perda real - o sistema so prova o numero, nao a causa.

ARQUITECTURA TECNICA PEDIDA
- Nao precisamos de Twilio real nem SMS real a funcionar de verdade - e um HACKATHON DEMO.
  Simula o SMS: uma pagina web simples com 2 caixas de texto ("Clinic sends:" e
  "Warehouse sends:") onde se digita o comando no formato REC/DESP e se clica enviar. Isto
  SUBSTITUI o hardware de telemovel/SMS real - e honesto dizer isto no video tecnico.
- Motor de reconciliacao em Python (FastAPI) ou Node (Express) - a tua escolha, o que for
  mais rapido de construir e mais estavel.
- Para "explicar a anomalia em linguagem simples" e "citar evidencia", usa a API da
  Anthropic (tenho chave configurada no servidor com $24.90 de credito, modelo
  claude-haiku ou claude-sonnet, o mais barato que resolva bem - sao poucas chamadas numa
  demo). Loop real de tool-use: o modelo decide se escala para humano ou nao, com base no
  confidence score que TU calculas deterministicamente no backend (nao deixes o LLM
  inventar o numero do desvio - isso e calculo simples: quantidade esperada vs recebida).
- Painel web: HTML/CSS/JS simples e bonito (tailwind via CDN serve), nao precisa de
  framework pesado. Prioridade: FUNCIONAR e ser bonito o suficiente para um screenshot,
  nao arquitectura perfeita.
- Audit log: guarda cada evento (SMS simulado recebido, calculo feito, alerta gerado,
  decisao do agente) num ficheiro JSON ou SQLite simples, e mostra isso no painel como
  "trilha de auditoria".
- Dados sinteticos: cria ~5 clinicas e 3-4 medicamentos (nomes reais tipo Amoxicillin,
  Paracetamol, ACTs/antimalaricos - sao comuns em Mocambique) com nomes ficticios de
  postos de saude (ex: "Clinic #14 - Beira Central", "Clinic #22 - Nampula Norte"). ZERO
  dados clinicos reais, ZERO PHI - isto e so stock e logistica, nunca dados de doentes.

ONDE TRABALHAR
/root/projects/dawatrace/ - ja criado, git inicializado (user.name "Lucas Andre Nguenha",
user.email lucas@helpaz.net). Estrutura sugerida: backend/, web/, data/, docs/. Decide a
melhor dentro disso.

O QUE PRECISO QUE ENTREGUES (nesta ordem de prioridade)
1. Caminho feliz a funcionar PONTA A PONTA primeiro (feio esta bem) - simular SMS, cruzar,
   gerar alerta, mostrar no painel. Sem isto, nada resto importa.
2. So depois: polir, agente Claude a explicar em linguagem natural, confidence score,
   escalonamento.
3. README.md claro (em ingles) explicando o que e, como correr localmente, e qual e o
   problema que resolve (pode usar o meu texto do brief acima).
4. Garantir que corre com um comando simples (ex: `python3 app.py` ou `npm start`) - vou
   precisar de um "Live demo link" funcional mais tarde (hoje vamos resolver isso com um
   host simples, tipo correr num porto publico do servidor ou um tunnel - nao te
   preocupes com isso agora, so deixa a app pronta a correr).
5. NAO crias o repositorio GitHub nem fazes push - nao tenho token configurado. So
   trabalha localmente em /root/projects/dawatrace com git commits normais (git add, git
   commit) para eu/Lucas podermos criar o remote e dar push de manha.

RESTRICOES
- Chave Anthropic: ja esta disponivel no ambiente deste servidor (verifica variaveis
  ANTHROPIC_API_KEY ou pergunta-me se nao encontrares - nao a exponhas em logs nem a
  commites no git).
- Zero dados pessoais reais, zero PHI, zero numeros inventados apresentados como factos
  reais fora do contexto de demo (tudo e claramente synthetic/demo data).
- Commits frequentes e pequenos (nao um commit gigante no fim) - preciso de conseguir ver
  o progresso.
- Se ficares bloqueado em algo que precises de decisao minha (nao tecnica, ex: nome de
  algo, prioridade), ESCREVE a pergunta num ficheiro /root/projects/dawatrace/PERGUNTAS.md
  e continua a trabalhar no resto - nao pares a espera de resposta.

Comeca agora. Trabalha de forma continua e autonoma - o Lucas esta a dormir e eu vou
verificar o teu progresso periodicamente, nao preciso de relatorios intermedios constantes,
so progresso real e commits.
