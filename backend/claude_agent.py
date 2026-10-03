"""Claude integration: plain-language explanation + escalate/don't-escalate
judgement, via a single real tool-use round trip.

Hard rule from the brief, enforced here structurally rather than just by
prompting: the deviation and confidence NUMBERS always come from
reconcile.py and are written into the DB and shown on the dashboard
verbatim, regardless of what the model says. The model is given those
numbers as fixed input and may only act on them through the one tool below
- there is no path by which its output can change the number shown.

Tone rule from the brief (also non-negotiable): never "theft"/"fraud"/
"desvio" in anything user-facing. The system prompt below says this
explicitly and the only text that reaches the UI is the model's own
`explicacao`/`motivo` fields, so this is the one place that tone actually
needs enforcing.
"""
import json
import os

import anthropic

MODEL = os.environ.get("DAWATRACE_MODEL", "claude-haiku-4-5-20251001")

SYSTEM_PROMPT = """Tu és o motor de explicação do DawaTrace, um sistema de reconciliação \
de stock de medicamentos entre postos de saúde e o armazém central, usado em contextos \
sem internet (as mensagens chegam por SMS).

REGRAS INEGOCIÁVEIS:
1. Nunca uses as palavras "roubo", "fraude", "desvio" (no sentido de furto) ou qualquer \
palavra que acuse alguém. Usa sempre "reconciliation gap" / "visibility gap" / "gap entre \
o despachado e o recebido". O sistema prova um número, nunca uma causa - o gap pode ser \
atraso de transporte, erro de registo, ou perda real, e tu não sabes qual.
2. NUNCA inventes nem ajustes o número do gap nem o confidence score - esses vêm-te \
prontos e são a verdade do sistema. A tua função é só explicar em linguagem simples e \
decidir, com a tua própria análise, se isto deve ser escalado para revisão humana.
3. Quando a confiança for baixa, prefere sempre dizer "não sei com certeza, um humano \
devia ver isto" em vez de inventar uma certeza que não tens - os jurados avaliam isto \
explicitamente.
4. Usa SEMPRE a ferramenta registar_decisao para responderes - nunca escrevas só texto \
livre.
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
                    "concreta (que SMS geraram este número). Nunca acusa ninguém."
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


def _fallback(gap, confidence, status, clinic_name, drug_label):
    """Used if the API call fails for any reason - the demo must not break
    because of a network hiccup or an empty credit balance."""
    escalar = status != "flagged"
    sentido = "em falta" if gap > 0 else "a mais"
    return {
        "explicacao": (
            f"{clinic_name} reportou {abs(gap)} unidades de {drug_label} {sentido} em "
            f"relação ao que o armazém despachou (confiança {confidence:.0f}%). "
            "Explicação automática de recurso - a chamada ao modelo falhou."
        ),
        "escalar": escalar,
        "motivo": "Decisão de recurso pelo limiar determinístico (chamada ao Claude indisponível).",
        "fallback": True,
    }


def explicar_e_decidir(clinic_name, drug_label, desp_total, rec_total, gap,
                        confidence, status, evidence_lines):
    """evidence_lines: list[str], the raw SMS lines behind this number (already
    formatted for display, e.g. '[2026-10-04 05:10] DESP 800 AMOX 250 (Warehouse)')."""
    gap_desc = (
        f"{abs(gap)} unidades em falta (despachado {desp_total}, recebido {rec_total})"
        if gap > 0
        else f"{abs(gap)} unidades a mais reportadas do que o despachado"
        if gap < 0
        else "sem gap"
    )
    user_msg = (
        f"Clínica: {clinic_name}\n"
        f"Medicamento: {drug_label}\n"
        f"Total despachado pelo armazém: {desp_total}\n"
        f"Total recebido reportado pela clínica: {rec_total}\n"
        f"Gap calculado (determinístico, não alteres): {gap_desc}\n"
        f"Confidence score (determinístico, não alteres): {confidence}/100\n"
        f"Classificação prévia do sistema: {status}\n\n"
        "Evidência (SMS que geraram este número):\n" + "\n".join(evidence_lines) +
        "\n\nExplica isto em linguagem simples e decide se deve escalar para um humano, "
        "usando a ferramenta registar_decisao."
    )

    try:
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=MODEL,
            max_tokens=500,
            system=SYSTEM_PROMPT,
            tools=[DECISION_TOOL],
            tool_choice={"type": "tool", "name": "registar_decisao"},
            messages=[{"role": "user", "content": user_msg}],
        )
        for block in resp.content:
            if block.type == "tool_use" and block.name == "registar_decisao":
                out = dict(block.input)
                out["fallback"] = False
                return out
        raise RuntimeError("modelo não chamou a ferramenta esperada")
    except Exception as e:  # noqa: BLE001 - demo must degrade gracefully, not crash
        fb = _fallback(gap, confidence, status, clinic_name, drug_label)
        fb["erro"] = str(e)[:300]
        return fb
