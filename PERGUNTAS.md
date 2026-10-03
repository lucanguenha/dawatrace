# Perguntas para o Lucas (não bloqueiam o trabalho — continuei a construir)

## 1. O momento principal da demo escala, em vez de afirmar com confiança

No guião exacto do brief (REC 500 → DESP 800 → "ALERT: 300 boxes missing"), com dados
limpos (só essas 2 mensagens, sem histórico a diluir), o confidence score sai a ~23/100
e o sistema classifica como **"escalated — precisa de revisão humana"**, não como um
alerta directo e confiante.

Isto é intencional pelo meu lado: um único par de mensagens no mesmo dia não chega para
confiança alta na minha fórmula (confiança sobe com corroboração — várias mensagens — e
com os dois relatos chegarem próximos no tempo). E bate com o que o brief pede no ponto 5
("os jurados preferem ver o agente a recusar decidir com certeza baixa"). O número do
gap (300) aparece sempre no painel, com confiança ou sem ela — o que muda é só a
moldura ("é isto" vs "é isto, mas não tenho certeza da causa").

**A decidir por ti**: para o momento *scripted* da demo (os primeiros 60s), preferes que
isto saia:
  (a) como está agora — escalated, reforça a mensagem de "não inventamos certeza", ou
  (b) ajusto a fórmula para que este caso específico (gap grande, mesmo que só 1 ponto de
      dados) saia como "flagged" direto, e reservo o "escalated" só para os casos mais
      ambíguos que já tenho na seed (Clinic #31/ACT, gap pequeno)?

Os dois casos já existem nos dados sintéticos de fundo, por isso o pitch pode mostrar
ambos de qualquer forma — isto é só sobre qual aparece no momento *scripted* principal.

Continuei com (a) por agora, porque é o que já está construído e testado, e é fácil de
mudar (um número em reconcile.py: ESCALATION_CEILING) se preferires (b).
