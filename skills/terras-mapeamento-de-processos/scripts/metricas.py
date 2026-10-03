#!/usr/bin/env python3
"""Calcula as métricas de diagnóstico a partir do processo.json e imprime tabela Markdown.

Uso:
  python3 metricas.py --json processo.json
  python3 metricas.py --json processo.json --volume 180 --custo-hora 45
"""
import argparse
import json
import sys


def fmt_min(v):
    if v is None:
        return "n/d"
    v = float(v)
    if v < 60:
        return f"{v:.0f} min"
    if v < 480:
        return f"{v / 60:.1f} h"
    return f"{v / 480:.1f} d ({v / 60:.1f} h)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--volume", type=float, default=None, help="transações por mês")
    ap.add_argument("--custo-hora", type=float, default=None, help="custo-hora médio (R$)")
    args = ap.parse_args()

    dados = json.load(open(args.json, encoding="utf-8"))
    passos = dados.get("passos", [])
    if not passos:
        print("JSON sem passos.", file=sys.stderr)
        return 1

    trab = sum(float(p.get("tempo_execucao_min") or 0) for p in passos)
    esp = sum(float(p.get("tempo_espera_min") or 0) for p in passos)
    lead = trab + esp
    sem_tempo = [p["id"] for p in passos if p.get("tempo_execucao_min") is None and p.get("tempo_espera_min") is None]
    retrabalho = [p for p in passos if p.get("excecoes")]
    espera_nodes = [p for p in passos if p.get("tipo") == "espera" or (p.get("tempo_espera_min") or 0) > 0]
    handoffs = sum(1 for a, b in zip(passos, passos[1:]) if a.get("ator") != b.get("ator"))

    # Normaliza nomes de sistema: "ERP (export)" e "ERP (consulta)" são o mesmo ERP
    def canonico(nome: str) -> str:
        base = str(nome).split("(")[0].split("/")[0].strip()
        return base or str(nome).strip()

    sistemas = sorted({canonico(s) for p in passos for s in p.get("sistema", []) if str(s).strip()})

    pct_esp = (esp / lead * 100) if lead else 0
    linhas = [
        "| Métrica | Valor | Origem |",
        "| --- | --- | --- |",
        f"| Lead time (ponta a ponta) | {fmt_min(lead)} | soma dos tempos informados no relato |",
        f"| Tempo de trabalho efetivo | {fmt_min(trab)} | idem |",
        f"| Tempo de espera/fila | {fmt_min(esp)} | idem |",
        f"| % do lead time que é espera | {pct_esp:.0f}% | calculado |",
        f"| Passos mapeados | {len(passos)} | calculado |",
        f"| Passos sem tempo informado | {len(sem_tempo)} ({', '.join(sem_tempo) if sem_tempo else '-'}) | lacuna de medição |",
        f"| Passos com exceção/retrabalho | {len(retrabalho)} ({', '.join(p['id'] for p in retrabalho)}) | relato |",
        f"| Etapas com espera | {len(espera_nodes)} | calculado |",
        f"| Handoffs (troca de ator) | {handoffs} | calculado |",
        f"| Sistemas envolvidos | {len(sistemas)} ({', '.join(sistemas) if sistemas else '-'}) | relato/tela |",
    ]

    if args.volume:
        # FTE mede TRABALHO (toque), não fila: usar lead time inflaria o número
        fte_h = trab / 60 * args.volume
        espera_mes = esp / 60 * args.volume
        linhas.append(f"| FTE-h/mês (trabalho efetivo) | {fte_h:.1f} h ({fte_h / 168:.2f} FTE) | volume {args.volume:g}/mês × tempo de trabalho |")
        linhas.append(f"| Espera acumulada/mês (fila) | {espera_mes:.1f} h | volume {args.volume:g}/mês × tempo de espera |")
        if args.custo_hora:
            linhas.append(f"| Custo do processo/mês | R$ {fte_h * args.custo_hora:,.2f} | FTE-h × R$ {args.custo_hora:g}/h |".replace(",", "."))
    else:
        linhas.append("| FTE-h/mês | n/d | informe `--volume` para calcular |")

    print("\n".join(linhas))
    if pct_esp >= 50:
        print(f"\n> Alerta: {pct_esp:.0f}% do lead time é espera — o problema é fila/prazo, não produtividade de quem executa.")
    if len(sem_tempo) >= len(passos) / 2:
        print("\n> Atenção: mais da metade dos passos está sem tempo medido. Colete tempos reais (cronômetro/relatório do sistema) antes de prometer ganho.")

    nao_unitarios = [p["id"] for p in passos
                     if any(t in (p.get("frequencia") or "").lower()
                            for t in ("semanal", "mensal", "diári", "diari", "1x", "eventual"))]
    if nao_unitarios and args.volume:
        print(f"\n> Atenção: passos {', '.join(nao_unitarios)} não são por demanda — multiplicar pelo "
              "volume mensal os superestima. Calcule-os por período (ex.: semanal = ×4/mês) antes de usar o FTE-h.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
