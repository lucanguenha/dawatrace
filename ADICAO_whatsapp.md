ADICAO AO PEDIDO ANTERIOR (nao reescrevas o que ja fizeste — isto e um ADD, nao um pivot)

O Lucas levantou um ponto excelente enquanto dormia (via Telegram): porque so SMS, se o
WhatsApp e muito mais usado? Pensei nisto com cuidado e a resposta e: fazemos OS DOIS,
deliberadamente, porque isso bate EXACTAMENTE no criterio oficial de avaliacao do World
Bank que diz "design e inclusividade, incluindo reconhecer trade-offs entre capacidade e
acesso".

NAO MUDES A ARQUITECTURA CENTRAL. O motor de reconciliacao, o formato de comando
(REC/DESP), o confidence score, o audit log — tudo isso fica exactamente como esta.

O QUE ADICIONAR (depois de teres o caminho feliz SMS a funcionar — nao bloqueies o
checkpoint 1 por causa disto):

1. No simulador de input, em vez de so "SMS", ter DOIS modos de entrada que USAM O MESMO
   formato de comando (REC/DESP) e vao para o MESMO motor de reconciliacao:
   - "SMS (any phone, no internet)" — o que ja tens
   - "WhatsApp (smartphone with data)" — visualmente parecido com uma caixa de chat do
     WhatsApp (bolhas verdes, etc) mas e so UI, nao precisa de integracao real com a API
     do WhatsApp Business (isso exigiria verificacao Meta, impossivel no tempo que temos)

2. No painel/trilha de auditoria, cada evento regista por QUE CANAL chegou (sms ou
   whatsapp) — isto e importante, e a prova visual do "capability vs access" pensado.

3. No README e no texto do pitch (vou tratar eu do texto, tu so deixa a funcionalidade
   pronta), a frase-chave e: "SMS is the primary channel because it works on any phone
   with signal, zero data required — that's the lowest common denominator for rural
   clinics. WhatsApp is offered as an upgrade path for users who already have a
   smartphone and data, not a dependency."

4. Prioridade: isto e MELHORIA, nao bloqueio. Se estiver a demorar demasiado ou a meter
   em risco o caminho feliz basico, para e volta ao essencial (SMS a funcionar fim a fim)
   — o dual-channel e um "nice to have forte", nao um requisito do checkpoint 1.

Continua o que estavas a fazer. So integra isto quando o caminho feliz SMS estiver solido.
