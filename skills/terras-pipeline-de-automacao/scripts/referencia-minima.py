#!/usr/bin/env python3
"""Pipeline mínimo de referência — terras-pipeline-de-automacao.

Duas etapas (normalizar → relatorio) sobre um bruto qualquer, com as três
regras duras da skill em mecanismo, não em disciplina:

  1. medição vem de script (hash, contagem de palavras — nunca de modelo);
  2. etapa confere as digitais do que lê e recusa nomeando o comando;
  3. recibo com três finais (sucesso | falha | ja_estava_feito), tempo e
     custo; falha não deixa metade (tmp + rename).

Uso:
  pipeline_minimo.py DIR normalizar [--refazer]
  pipeline_minimo.py DIR relatorio [--falhar]
"""
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CUSTO = {"normalizar": 0.0, "relatorio": 0.01}


class Recusa(Exception):
    """A cadeia está inconsistente: não roda, manda refazer o dado."""


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def gravar_atomica(destino: Path, dados: bytes) -> None:
    tmp = destino.with_suffix(destino.suffix + ".tmp")
    tmp.write_bytes(dados)
    os.replace(tmp, destino)


def encerrar(dirt: Path, etapa: str, final: str, entradas, saidas, params,
             erro=None, custo=0.0, t0=None) -> None:
    recibo = {
        "etapa": etapa,
        "final": final,
        "entradas": entradas,
        "saidas": saidas,
        "parametros": params,
        "tempo_s": round(time.time() - t0, 3) if t0 else 0.0,
        "custo": custo,
        "erro": erro,
        "quando": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    caminho = dirt / "recibos" / f"{etapa}.json"
    gravar_atomica(caminho, json.dumps(recibo, indent=2, ensure_ascii=False).encode())


def ja_estava_feito(dirt: Path, etapa: str, entradas, params) -> bool:
    rc = dirt / "recibos" / f"{etapa}.json"
    if not rc.exists():
        return False
    antigo = json.loads(rc.read_text())
    return (antigo["final"] == "sucesso"
            and antigo["entradas"] == entradas
            and antigo["parametros"] == params)


def produzir_normalizar(dirt: Path, entradas, refazer: bool):
    texto = (dirt / "entrada.txt").read_bytes().upper()
    destino = dirt / "acervo" / "normalizado.txt"
    gravar_atomica(destino, texto)
    manifesto = {"entrada": entradas[0]["sha256"], "saida": sha256(destino)}
    gravar_atomica(dirt / "acervo" / "manifesto-normalizar.json",
                   json.dumps(manifesto, indent=2).encode())
    return [{"caminho": "acervo/normalizado.txt", "sha256": manifesto["saida"]}]


def produzir_relatorio(dirt: Path, entradas, falhar: bool):
    normalizado = dirt / "acervo" / "normalizado.txt"
    manifesto_path = dirt / "acervo" / "manifesto-normalizar.json"
    manifesto = json.loads(manifesto_path.read_text())
    atual = sha256(normalizado)
    if atual != manifesto["saida"]:
        raise Recusa(
            f"entrada mudou desde a etapa anterior (esperado {manifesto['saida'][:8]}…, "
            f"achei {atual[:8]}…). Rode: pipeline_minimo.py {dirt} normalizar --refazer"
        )
    if falhar:
        # simula quebra no meio: tmp nasce, rename nunca acontece
        (dirt / "acervo" / "relatorio.md.tmp").write_bytes(b"pela metade")
        raise RuntimeError("falha forçada no meio da etapa (simulação)")
    texto = normalizado.read_bytes().decode("utf-8", errors="replace")
    n_palavras = len(texto.split())  # medição vem daqui, não de modelo
    doc = f"# Relatório\n\npalavras: {n_palavras} (medido)\n\n## topo\n{texto.splitlines()[0]}\n"
    destino = dirt / "acervo" / "relatorio.md"
    gravar_atomica(destino, doc.encode())
    return [{"caminho": "acervo/relatorio.md", "sha256": sha256(destino)}]


def main() -> int:
    dirt = Path(sys.argv[1]).resolve()
    etapa = sys.argv[2]
    refazer = "--refazer" in sys.argv
    falhar = "--falhar" in sys.argv
    (dirt / "acervo").mkdir(parents=True, exist_ok=True)
    (dirt / "recibos").mkdir(parents=True, exist_ok=True)

    if etapa == "normalizar":
        bruto = dirt / "entrada.txt"
        params = {"modo": "maiusculas"}
    else:
        bruto = dirt / "acervo" / "normalizado.txt"
        params = {"topo": 1}
    entradas = [{"caminho": str(bruto.relative_to(dirt)), "sha256": sha256(bruto)}]

    if not refazer and ja_estava_feito(dirt, etapa, entradas, params):
        print(f"{etapa}: ja_estava_feito (não refaz, não paga duas vezes)")
        return 0

    t0 = time.time()
    try:
        if etapa == "normalizar":
            saidas = produzir_normalizar(dirt, entradas, refazer)
        else:
            saidas = produzir_relatorio(dirt, entradas, falhar)
    except Recusa as e:
        encerrar(dirt, etapa, "falha", entradas, [], params, erro=str(e), t0=t0)
        print(f"{etapa}: RECUSA — {e}", file=sys.stderr)
        return 2
    except Exception as e:
        tmp = dirt / "acervo" / "relatorio.md.tmp"
        if tmp.exists():
            tmp.unlink()
        encerrar(dirt, etapa, "falha", entradas, [], params, erro=str(e), t0=t0)
        print(f"{etapa}: falha — {e} (nada pela metade no acervo)", file=sys.stderr)
        return 1
    encerrar(dirt, etapa, "sucesso", entradas, saidas, params,
             custo=CUSTO[etapa], t0=t0)
    print(f"{etapa}: sucesso (custo R$ {CUSTO[etapa]:.2f}, {round(time.time() - t0, 3)}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
