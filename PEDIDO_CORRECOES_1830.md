# PEDIDO — Correções de última hora no DawaTrace (antes das 21:00 Macau)

Contexto: demo ao vivo em https://projects.helpaz.net/dawatrace/ (serviço `dawatrace.service`,
corre `backend.app`). Faltam ~2h45 para a submissão do hackathon. Estas correcções são para
gravar os vídeos — a demo NÃO pode mostrar texto de erro.

## PROBLEMA 1 (crítico) — o LLM está a falhar e o erro aparece no ecrã

O saldo da API Anthropic está a zero, por isso a chamada ao modelo falha e o painel mostra
literalmente:
  "Explicação automática de recurso - a chamada ao modelo falhou."
  "Decisão de recurso pelo limiar determinístico (chamada ao Claude indisponível)."

Isto aparece no ecrã e vai ficar gravado no vídeo. Tem de desaparecer — que seja impossível
um jurado ver a palavra "falhou" ou "indisponível".

### O que quero

**(a) Camada de LLM agnóstica de fornecedor.** `backend/claude_agent.py` deve tentar, por ordem:
  1. Anthropic (como está hoje, se `ANTHROPIC_API_KEY` existir e tiver saldo)
  2. **DeepSeek** (fallback) — API compatível com OpenAI:
     - base_url: `https://api.deepseek.com`
     - endpoint: `POST /chat/completions`
     - modelo: `deepseek-chat`
     - chave: `DEEPSEEK_API_KEY`
  3. Se ambos falharem: explicação **determinística gerada no backend** a partir dos números
     reais do gap + evidência da trilha (frase completa e profissional, com o número e a
     percentagem dentro). NUNCA uma frase de erro.

A chave DeepSeek já existe no servidor: lê-a de `/root/.hermes/.env` (variável
`DEEPSEEK_API_KEY`) e acrescenta-a a `/root/projects/dawatrace/.env` (que é gitignored — confirma
no `.gitignore` antes de escrever; NUNCA faças commit da chave).

Isto reforça o pitch em vez de o enfraquecer: o brief do World Bank pede "offline-capable,
modelos locais". O frontend/README podem dizer que a camada de raciocínio é **agnóstica de
fornecedor** e corre em qualquer modelo (incluindo local). Ajusta o README nesse sentido — sem
inventar que estamos a correr um modelo local.

**(b) Nenhuma string de falha visível ao utilizador.** Substitui todas as mensagens de recurso
por texto neutro e completo. Sugestão de redacção (podes melhorar, em português, sem travessões
longos):
  - Explicação: frase construída com o número real, ex.: "A Clínica #14 registou 300 unidades de
    Amoxicilina 250 a menos do que o armazém despachou. O gap foi calculado a partir de dois SMS
    de reporte independentes e confirmado por ambos."
  - Linha de decisão: "Decisão tomada pelo limiar determinístico de confiança, sem intervenção
    do modelo." (sem dizer que o modelo falhou)
  O erro real fica só nos logs do servidor.

## PROBLEMA 2 (qualidade da demo) — alerta espúrio com "dispatched 0"

Reprodução: clicar "Send as Clinic" (`REC 500 AMOX 250`) ANTES de "Send as Warehouse"
(`DESP 800 AMOX 250`). Aparecem DOIS alertas na trilha:
  1. `dispatched 800 · received 500 · gap 300 (missing)` ← o correcto
  2. `dispatched 0 · received 500 · gap 500 (excess reported)` ← lixo, gerado antes de o
     DESP chegar, porque o lado do armazém ainda não tinha reporte

Um "dispatched 0" no ecrã num vídeo é mau. O comportamento correcto:
  - Um REC sem DESP correspondente **não** gera alerta de imediato. Fica em estado
    **"a aguardar registo do armazém"** (pendente), visível na trilha como pendente e não como gap.
  - Quando o DESP chega, os dois cruzam-se e sai **um** alerta limpo (300 missing).
  - O mesmo no sentido inverso (DESP sem REC → "a aguardar confirmação da clínica").
  - Só gera alerta quando existem os dois lados da mesma clínica + medicamento.

Objectivo verificável: correr o fluxo do brief do zero (limpar a base, REC 500 → DESP 800) e a
trilha tem de mostrar **exactamente um** alerta: `dispatched 800 · received 500 · gap 300`,
com confiança calculada e evidência. Nenhum alerta com dispatched 0.

## Restrições

- Não reescrevas a arquitectura. Mudanças mínimas e cirúrgicas.
- Não toques em `web/index.html` para além do necessário às mensagens de texto.
- Portuguese sem travessões longos (—) nem en dashes (–) no texto da UI.
- No fim: reinicia o serviço (`systemctl restart dawatrace.service`), corre o fluxo
  ponta-a-ponta e confirma o resultado real antes de dizer que está feito. Depois `git commit`.

Reporta: o que mudou, o output real do teste ponta-a-ponta, e o hash do commit.
