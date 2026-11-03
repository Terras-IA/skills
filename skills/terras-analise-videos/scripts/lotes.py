#!/usr/bin/env python3
"""Divide os vídeos preparados em lotes e aponta duplicatas.

Uso: python3 lotes.py SAIDA [--lotes 8]

Grava SAIDA/_lotes/lote_NN.txt (um id por linha, só o id) e
SAIDA/_lotes/duplicatas.json (mesmo md5, ou mesma transcrição com md5 diferente).
Lista feita em Python de propósito: `ls` com alias (eza, lsd) põe permissão e data
na linha, e o agente do lote recebe lixo no lugar do id.
"""
import argparse, json
from collections import defaultdict
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("saida")
ap.add_argument("--lotes", type=int, default=8)
a = ap.parse_args()

base = Path(a.saida).resolve()
dados, out = base / "_dados", base / "_lotes"
out.mkdir(exist_ok=True)
ids = sorted(p.parent.name for p in dados.glob("*/transcricao.json"))
if not ids:
    raise SystemExit(f"nada preparado em {dados}: rode preparar.py antes")

n = max(1, min(a.lotes, len(ids)))
for f in out.glob("lote_*.txt"):
    f.unlink()
for k in range(n):
    (out / f"lote_{k:02d}.txt").write_text("\n".join(ids[k::n]) + "\n")

por_md5, por_texto = defaultdict(list), defaultdict(list)
for i in ids:
    meta = json.loads((dados / i / "metadados.json").read_text()).get("_analise", {})
    por_md5[meta.get("md5")].append(i)
    t = json.loads((dados / i / "transcricao.json").read_text())
    texto = " ".join(s["texto"] for s in t["segmentos"]).strip().lower()
    if not t.get("sem_fala") and len(texto) > 80:
        por_texto[texto[:400]].append(i)
dups = [g for g in por_md5.values() if len(g) > 1] + \
       [g for g in por_texto.values() if len(g) > 1 and not any(set(g) <= set(x) for x in por_md5.values())]
(out / "duplicatas.json").write_text(json.dumps(dups, indent=1))
print(f"{len(ids)} vídeos em {n} lotes de ~{len(ids)//n}; {len(dups)} grupos de duplicatas -> {out}")
