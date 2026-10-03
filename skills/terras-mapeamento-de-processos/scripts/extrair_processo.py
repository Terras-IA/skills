#!/usr/bin/env python3
"""Extrai um processo estruturado (JSON) a partir de transcrição/descrição.

Uso:
  python3 extrair_processo.py --input transcricao-enriquecida.md --output processo.json
  python3 extrair_processo.py --input relato.txt --output processo.json --model gpt-5-mini

LLM: qualquer endpoint compatível com a API de Chat Completions (OpenAI e afins).
  TERRAS_LLM_API_KEY   chave (obrigatória para este caminho)
  TERRAS_LLM_BASE_URL  base do endpoint, quando não for a OpenAI
  TERRAS_LLM_MODEL     modelo padrão (ou --model)
Sem LLM configurado, escreva o processo.json à mão (ver templates/processo-json.md).
"""
import argparse
import json
import os
import sys

PASSO_PROPS = {
    "id": {"type": "string"},
    "nome": {"type": "string"},
    "ator": {"type": "string"},
    "tipo": {
        "type": "string",
        "enum": ["tarefa", "decisao", "espera", "sistema", "documento", "aprovacao"],
    },
    "sistema": {"type": "array", "items": {"type": "string"}},
    "entradas": {"type": "array", "items": {"type": "string"}},
    "saidas": {"type": "array", "items": {"type": "string"}},
    # anyOf (e não "type": ["number","null"]) — há provedor que recusa tipo anulável em array
    "tempo_execucao_min": {"anyOf": [{"type": "number"}, {"type": "null"}]},
    "tempo_espera_min": {"anyOf": [{"type": "number"}, {"type": "null"}]},
    "frequencia": {"type": "string"},
    "excecoes": {"type": "array", "items": {"type": "string"}},
    "evidencia": {"type": "string"},
    "confianca": {"type": "string", "enum": ["alta", "media", "baixa"]},
}

SCHEMA = {
    "type": "object",
    "properties": {
        "processo": {"type": "string"},
        "objetivo": {"type": "string"},
        "gatilho": {"type": "string"},
        "fim": {"type": "string"},
        "volume_mensal": {"type": "string"},
        "atores": {"type": "array", "items": {"type": "string"}},
        "sistemas": {"type": "array", "items": {"type": "string"}},
        "passos": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": PASSO_PROPS,
                "required": list(PASSO_PROPS.keys()),
                "additionalProperties": False,
            },
        },
        "lacunas": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "processo", "objetivo", "gatilho", "fim", "volume_mensal",
        "atores", "sistemas", "passos", "lacunas",
    ],
    "additionalProperties": False,
}

SYSTEM = """Você é um analista sênior de processos (BPM/Lean). Recebe a transcrição de uma \
entrevista, áudio ou gravação de tela em que alguém descreve um processo, e devolve o processo \
estruturado em JSON.

Regras obrigatórias:
1. NADA SEM EVIDÊNCIA: cada passo precisa de um trecho/timestamp literal em `evidencia`. Se não \
houver, NÃO crie o passo — registre a dúvida em `lacunas`.
2. Separe tempo de TRABALHO (`tempo_execucao_min`) de tempo de ESPERA/fila (`tempo_espera_min`). \
Converta unidades para minutos (1 dia útil = 480, 1 semana = 2400, 1 hora = 60).
3. Se o tempo não foi dito, use null e confianca "baixa" — nunca invente número preciso.
4. `tipo`: "tarefa" (trabalho manual), "decisao" (escolha/caminho alternativo), "espera" (fila, \
aguardando terceiro), "sistema" (ação automática do sistema), "documento" (emissão/recebimento \
de documento), "aprovacao" (autorização formal ou informal).
5. `ator` = papel/função (ex.: "Atendente", "Gestor"), nunca nome próprio de pessoa.
6. Liste em `excecoes` os desvios ditos ("quando dá errado", "às vezes", "se não achar").
7. `frequencia`: sempre/às vezes/1x por demanda/raro.
8. Preserve o processo REAL descrito, inclusive gambiarras (planilha paralela, WhatsApp), não o \
processo ideal. Se o relato descrever o "deveria ser", registre a divergência em `lacunas`.
9. `id`: P1, P2, P3... na ordem cronológica.
10. `lacunas`: o que falta para fechar o diagnóstico (volume, tempo, alçada, custo, sistema).
11. CAMINHO PRINCIPAL: ordene os passos pelo fluxo MAIS COMUM (o caso típico). Caminhos \
alternativos, urgentes ou raros NÃO viram passos próprios — registre-os em `excecoes` do passo \
de decisão, com o destino (ex.: "urgente: aciona técnico de plantão por telefone, sem passar \
pela fila"). O diagrama é uma cadeia linear do caminho principal.
12. Nunca use nomes próprios de pessoas; use o papel (Atendente, Gestor, Técnico).
13. NOMES CANÔNICOS: use sempre o mesmo nome curto para o mesmo sistema (ex.: "ERP", "CRM", \
"Outlook", "Excel", "WhatsApp"). Nunca crie variações como "ERP (consulta OS)" ou \
"ERP (export)" — a variação é da ação, não do sistema.
14. TODO TEMPO DITO NO RELATO DEVE APARECER: se o relato diz "fica 2 dias parado", o passo de \
fila precisa ter tempo_espera_min = 960; "meio dia esperando aprovação" = 240; "2 horas no \
relatório" = 120. Revise o resultado antes de responder e confira cada duração mencionada.
15. NENHUMA ETAPA CITADA PODE SER OMITIDA, mesmo as secundárias (reabertura de chamados, \
relatório semanal, faturamento no fim do mês, retrabalho).
Responda apenas com o JSON."""


def build_prompt(texto: str, contexto: str) -> str:
    extra = f"\n\nContexto adicional fornecido pelo usuário:\n{contexto}\n" if contexto else ""
    return f"Extraia o processo estruturado da evidência abaixo.{extra}\n\n--- EVIDÊNCIA ---\n{texto}\n--- FIM ---"


def call_llm(model: str, prompt: str) -> dict:
    from openai import OpenAI

    base = os.environ.get("TERRAS_LLM_BASE_URL") or os.environ.get("OPENAI_API_BASE")
    key = os.environ.get("TERRAS_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit(
            "Sem LLM configurado: defina TERRAS_LLM_API_KEY (e TERRAS_LLM_BASE_URL, se não for a OpenAI) "
            "ou escreva o processo.json à mão seguindo templates/processo-json.md."
        )
    client = OpenAI(api_key=key, base_url=base) if base else OpenAI(api_key=key)
    kwargs = {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_schema", "json_schema": {"name": "processo", "strict": True, "schema": SCHEMA}},
    }
    # Ajuste por família de modelo: no GPT, o raciocínio consome o teto de saída
    if model.startswith("gpt-5") or model.startswith("gpt-4"):
        kwargs["max_completion_tokens"] = 16000
        kwargs["extra_body"] = {"reasoning": {"effort": "medium"}}
    elif model.startswith("claude"):
        kwargs["max_tokens"] = 20000
        kwargs["extra_body"] = {"thinking": {"type": "enabled", "budget_tokens": 4000}}
    else:  # gemini e outros
        kwargs["max_tokens"] = 32000

    resp = client.chat.completions.create(**kwargs)
    if not resp.choices:
        raise RuntimeError(
            "O endpoint não retornou choices — normalmente é schema inválido para structured output. "
            "Use anyOf em vez de type: [\"number\", \"null\"] e evite additionalProperties aberto."
        )
    content = resp.choices[0].message.content
    if not content:
        raise RuntimeError(f"Resposta vazia do modelo ({resp.choices[0].finish_reason})")
    return json.loads(content)


def resumo(dados: dict) -> str:
    passos = dados.get("passos", [])
    trab = sum(p["tempo_execucao_min"] or 0 for p in passos)
    esp = sum(p["tempo_espera_min"] or 0 for p in passos)
    total = trab + esp
    pct = f"{esp / total * 100:.0f}%" if total else "n/d"
    linhas = [
        f"Processo: {dados.get('processo', '?')}",
        f"Passos: {len(passos)} | Atores: {len(dados.get('atores', []))} | Sistemas: {len(dados.get('sistemas', []))}",
        f"Trabalho: {trab:.0f} min | Espera: {esp:.0f} min | Lead time: {total:.0f} min | % espera: {pct}",
        f"Lacunas: {len(dados.get('lacunas', []))}",
        "",
        "Passos:",
    ]
    for p in passos:
        t = []
        if p.get("tempo_execucao_min"):
            t.append(f"{p['tempo_execucao_min']:.0f}min trab")
        if p.get("tempo_espera_min"):
            t.append(f"{p['tempo_espera_min']:.0f}min espera")
        linhas.append(f"  {p['id']:>4} [{p['tipo']:<9}] {p['ator']:<14} {p['nome'][:60]:<60} {' + '.join(t)}")
    if dados.get("lacunas"):
        linhas += ["", "Lacunas a confirmar:"] + [f"  - {l}" for l in dados["lacunas"]]
    return "\n".join(linhas)


def main() -> int:
    ap = argparse.ArgumentParser(description="Transcrição -> processo estruturado (JSON)")
    ap.add_argument("--input", required=True, help="arquivo de transcrição/descrição")
    ap.add_argument("--output", required=True, help="JSON de saída")
    ap.add_argument("--model", default=os.environ.get("TERRAS_LLM_MODEL", "gpt-5-mini"),
                    help="modelo do endpoint (default: TERRAS_LLM_MODEL ou gpt-5-mini)")
    ap.add_argument("--contexto", default="", help="contexto extra (setor, volume, custo-hora)")
    ap.add_argument("--dry-run", action="store_true", help="só valida o arquivo de entrada")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"Arquivo não encontrado: {args.input}", file=sys.stderr)
        return 1
    texto = open(args.input, encoding="utf-8").read()
    if len(texto.strip()) < 80:
        print("Evidência muito curta. Colete mais relato ou use references/roteiro-entrevista.md.", file=sys.stderr)
        return 1
    print(f"Evidência: {args.input} ({len(texto)} caracteres)")
    if args.dry_run:
        return 0

    dados = call_llm(args.model, build_prompt(texto, args.contexto))
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"\nJSON salvo em {args.output}\n")
    print(resumo(dados))
    return 0


if __name__ == "__main__":
    sys.exit(main())
