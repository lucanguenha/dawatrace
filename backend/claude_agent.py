"""Reasoning layer: plain-language explanation + escalate/don't-escalate
judgement, provider-agnostic.

Hard rule from the brief, enforced here structurally rather than just by
prompting: the deviation and confidence NUMBERS always come from
reconcile.py and are written into the DB and shown on the dashboard
verbatim, regardless of what the model says. The model is given those
numbers as fixed input and may only act on them through the one tool/JSON
contract below - there is no path by which its output can change the
number shown.

Tone rule from the brief (also non-negotiable): never "theft"/"fraud"/
"desvio" (as in misappropriation) in anything user-facing.

Provider order (04/Out/2026, correcao de ultima hora antes da demo): tenta
Anthropic, depois DeepSeek, e so se os dois falharem usa uma explicacao
determinística construída no backend a partir dos numeros reais. EM
NENHUM CAMINHO o texto que chega ao utilizador menciona que uma chamada
falhou ou que um fornecedor está indisponível - isso fica só nos logs do
servidor (stderr), nunca em explicacao/motivo.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

import anthropic

ANTHROPIC_MODEL = os.environ.get("DAWATRACE_MODEL", "claude-haiku-4-5-20251001")
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

SYSTEM_PROMPT = """Tu és o motor de explicação do DawaTrace, um sistema de reconciliação \
de stock de medicamentos entre postos de saúde e o armazém central, usado em contextos \
sem internet (as mensagens chegam por SMS ou WhatsApp).

REGRAS INEGOCIÁVEIS:
1. Nunca uses as palavras "roubo", "fraude", "desvio" (no sentido de furto) ou qualquer \
palavra que acuse alguém. Usa sempre "reconciliation gap" / "visibility gap" / "gap entre \
o despachado e o recebido". O sistema prova um número, nunca uma causa - o gap pode ser \
atraso de transporte, erro de registo, ou perda real, e tu não sabes qual.
2. NUNCA inventes nem ajustes o número do gap nem o confidence score - esses vêm-te \
prontos e são a verdade do sistema. A tua função é só explicar em linguagem simples e \
decidir, com a tua própria análise, se isto deve ser escalado para revisão humana.
3. Quando a confiança for baixa, prefere sempre dizer "não sei com certeza, um humano \
devia ver isto" em vez de inventar uma certeza que não tens.
4. Nunca escrevas travessões longos (—) nem en dashes (–) no texto. Usa vírgulas ou \
pontos.
"""

DECISION_TOOL = {
    "name": "registar_decisao",
    "description": (
        "Regista a explicação em linguagem simples do gap de reconciliação e a "
        "decisão sobre escalar ou não para revisão humana."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "explicacao": {
                "type": "string",
                "description": (
                    "2-3 frases em português, linguagem simples, citando a evidência "
                    "concreta (que mensagens geraram este número). Nunca acusa ninguém. "
                    "Sem travessões longos nem en dashes."
                ),
            },
            "escalar": {
                "type": "boolean",
                "description": (
                    "true se isto deve ir para revisão humana em vez de ser apresentado "
                    "como facto; false se a evidência é forte e clara o suficiente para "
                    "mostrar como alerta directo."
                ),
            },
            "motivo": {
                "type": "string",
                "description": "Uma frase curta justificando a decisão de escalar ou não.",
            },
        },
        "required": ["explicacao", "escalar", "motivo"],
    },
}


def _log_erro(fornecedor, e):
    # So para os logs do servidor (journalctl/systemd) - nunca chega ao utilizador.
    print(f"[claude_agent] {fornecedor} falhou: {type(e).__name__}: {e}", file=sys.stderr)


def _user_msg(clinic_name, drug_label, desp_total, rec_total, gap, confidence, status,
              evidence_lines):
    gap_desc = (
        f"{abs(gap)} unidades em falta (despachado {desp_total}, recebido {rec_total})"
        if gap > 0
        else f"{abs(gap)} unidades a mais reportadas do que o despachado"
        if gap < 0
        else "sem gap"
    )
    return (
        f"Clínica: {clinic_name}\n"
        f"Medicamento: {drug_label}\n"
        f"Total despachado pelo armazém: {desp_total}\n"
        f"Total recebido reportado pela clínica: {rec_total}\n"
        f"Gap calculado (determinístico, não alteres): {gap_desc}\n"
        f"Confidence score (determinístico, não alteres): {confidence}/100\n"
        f"Classificação prévia do sistema: {status}\n\n"
        "Evidência (mensagens que geraram este número):\n" + "\n".join(evidence_lines) +
        "\n\nExplica isto em linguagem simples e decide se deve escalar para um humano."
    )


def _via_anthropic(user_msg):
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        tools=[DECISION_TOOL],
        tool_choice={"type": "tool", "name": "registar_decisao"},
        messages=[{"role": "user", "content": user_msg}],
    )
    for block in resp.content:
        if block.type == "tool_use" and block.name == "registar_decisao":
            return dict(block.input)
    raise RuntimeError("modelo nao chamou a ferramenta esperada")


def _via_deepseek(user_msg):
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY nao definida")
    body = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT + (
                "\n\nResponde APENAS com um objecto JSON, sem markdown, sem texto antes "
                "ou depois, com exactamente estas chaves: "
                '{"explicacao": "...", "escalar": true|false, "motivo": "..."}'
            )},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.3,
        "max_tokens": 500,
    }
    req = urllib.request.Request(
        DEEPSEEK_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
    texto = data["choices"][0]["message"]["content"].strip()
    # o modelo por vezes envolve o JSON em ```json ... ``` apesar da instrucao - extrair
    m = re.search(r"\{.*\}", texto, re.S)
    if not m:
        raise RuntimeError("resposta do DeepSeek nao continha JSON")
    out = json.loads(m.group(0))
    if not {"explicacao", "escalar", "motivo"} <= out.keys():
        raise RuntimeError("JSON do DeepSeek sem as chaves esperadas")
    return out


def _explicacao_deterministica(clinic_name, drug_label, desp_total, rec_total, gap,
                                confidence, status):
    """Último recurso, sem chamada a modelo nenhum. Frase completa e profissional,
    construida só a partir dos números reais - nunca menciona falha de modelo."""
    if gap > 0:
        pct = round(gap / desp_total * 100) if desp_total else 0
        corpo = (
            f"{clinic_name} registou {gap} unidades de {drug_label} a menos do que o "
            f"armazém despachou ({pct}% do total enviado). O gap foi calculado a partir "
            f"dos registos de despacho e de recepção desta clínica e deste medicamento."
        )
    elif gap < 0:
        corpo = (
            f"{clinic_name} reportou {abs(gap)} unidades de {drug_label} acima do que "
            f"o armazém tem registo de ter despachado. Pode indicar um despacho ainda "
            f"não registado ou uma diferença de contagem entre os dois lados."
        )
    else:
        corpo = f"{clinic_name} e o armazém reportam números iguais de {drug_label}."
    corpo += f" Confiança do sistema nesta leitura: {confidence:.0f} de 100."
    escalar = status != "flagged"
    motivo = (
        "Classificação feita pelo limiar determinístico de confiança, sem intervenção "
        "de um modelo de linguagem nesta leitura."
    )
    return {"explicacao": corpo, "escalar": escalar, "motivo": motivo}


def explicar_e_decidir(clinic_name, drug_label, desp_total, rec_total, gap,
                        confidence, status, evidence_lines):
    """evidence_lines: list[str], as mensagens em bruto por trás deste número."""
    user_msg = _user_msg(clinic_name, drug_label, desp_total, rec_total, gap, confidence,
                         status, evidence_lines)

    for fornecedor, fn in (("anthropic", _via_anthropic), ("deepseek", _via_deepseek)):
        try:
            out = fn(user_msg)
            out["fallback"] = False
            out["fornecedor"] = fornecedor
            return out
        except Exception as e:
            _log_erro(fornecedor, e)

    out = _explicacao_deterministica(clinic_name, drug_label, desp_total, rec_total,
                                      gap, confidence, status)
    out["fallback"] = True
    out["fornecedor"] = "determinístico"
    return out
