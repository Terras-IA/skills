#!/usr/bin/env python3
"""Junta os analise.md num relatório HTML único (abre offline) + índice CSV.

Uso: python3 relatorio.py SAIDA [--titulo "Análise dos vídeos"]

Lê SAIDA/_dados/*/analise.md e, se existir, SAIDA/RELATORIO-GERAL.md (visão geral
escrita pelo agente). Grava SAIDA/RELATORIO.html e SAIDA/indice.csv.
Precisa do pacote markdown (python3 -m pip install markdown, ou o do sistema).
"""
import argparse, csv, html, json, os, re
from pathlib import Path
import markdown

ap = argparse.ArgumentParser()
ap.add_argument("saida")
ap.add_argument("--titulo", default="Análise dos vídeos")
a = ap.parse_args()
base = Path(a.saida).resolve()
dados = base / "_dados"
CATS = ["Verdadeiro", "Majoritariamente verdadeiro", "Misto", "Enganoso", "Falso", "Não verificável", "Não se aplica"]
CORES = {"Verdadeiro": "#1b7f3b", "Majoritariamente verdadeiro": "#4c9a2a", "Misto": "#b7791f",
         "Enganoso": "#c2410c", "Falso": "#b91c1c", "Não verificável": "#6b7280", "Não se aplica": "#64748b"}

def categoria(linha):
    t = re.sub(r"[*_]", "", linha).split(":", 1)[-1].strip()
    for c in sorted(CATS, key=len, reverse=True):
        if t.lower().startswith(c.lower()):
            return c
    return "Não verificável"

itens = []
for f in sorted(dados.glob("*/analise.md")):
    txt = f.read_text()
    linhas = txt.splitlines()
    titulo = next((l[2:].strip() for l in linhas if l.startswith("# ")), f.parent.name)
    meta = next((l.strip() for l in linhas[1:6] if l.strip() and not l.startswith("#")), "")
    ver = next((l for l in linhas if re.match(r"[*_]*Veredito", l)), "Veredito: Não verificável")
    m = re.search(r"\*\*Resumo:?\*\*:?\s*(.+)", txt)
    meta_json = f.parent / "metadados.json"
    origem = json.loads(meta_json.read_text()).get("_analise", {}).get("origem", "") if meta_json.exists() else ""
    video = os.path.relpath(origem, base) if origem else ""
    itens.append(dict(id=f.parent.name, titulo=titulo, meta=meta, cat=categoria(ver),
                      veredito=re.sub(r"[*_]", "", ver).split(":", 1)[-1].strip(),
                      resumo=m.group(1).strip() if m else "", md=txt, video=video))

with open(base / "indice.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["id", "titulo", "categoria", "veredito", "resumo", "arquivo_video"])
    for it in itens:
        w.writerow([it["id"], it["titulo"], it["cat"], it["veredito"], it["resumo"],
                    it["video"]])

cont = {c: sum(1 for i in itens if i["cat"] == c) for c in CATS}
geral = markdown.markdown((base / "RELATORIO-GERAL.md").read_text(), extensions=["tables"]) if (base / "RELATORIO-GERAL.md").exists() else ""

cards = []
for it in itens:
    corpo = markdown.markdown(it["md"].split("\n", 1)[1] if "\n" in it["md"] else "", extensions=["tables"])
    q = f"_dados/{it['id']}/quadros.jpg"
    cards.append(f"""<details class="card" data-cat="{html.escape(it['cat'])}" data-busca="{html.escape((it['titulo']+' '+it['resumo']).lower())}">
<summary><span class="tag" style="background:{CORES[it['cat']]}">{html.escape(it['cat'])}</span>
<strong>{html.escape(it['titulo'])}</strong><span class="meta">{html.escape(it['meta'])}</span></summary>
<div class="corpo"><a href="{q}" target="_blank"><img loading="lazy" src="{q}" alt="16 quadros do vídeo"></a>
<p class="links"><a href="{html.escape(it['video'])}">▶ abrir vídeo</a> · <a href="_dados/{it['id']}/transcricao.txt">transcrição</a> · <a href="_dados/{it['id']}/analise.md">analise.md</a></p>
{corpo}</div></details>""")

filtros = "".join(f'<button data-f="{html.escape(c)}" style="--c:{CORES[c]}">{html.escape(c)} <b>{n}</b></button>' for c, n in cont.items() if n)
page = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(a.titulo)}</title><style>
:root{{--bg:#f7f7f5;--fg:#1f2328;--card:#fff;--mut:#667085;--bd:#e4e4e0}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16181c;--fg:#e6e6e6;--card:#1f2228;--mut:#9aa3af;--bd:#2e323a}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,sans-serif}}
main{{max-width:980px;margin:auto;padding:24px 16px 80px}} h1{{margin:.2em 0}}
.geral{{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:4px 20px;margin:16px 0}}
.bar{{position:sticky;top:0;background:var(--bg);padding:10px 0;display:flex;flex-wrap:wrap;gap:6px;z-index:2}}
.bar input{{flex:1 1 220px;padding:8px 10px;border:1px solid var(--bd);border-radius:8px;background:var(--card);color:var(--fg)}}
.bar button{{border:1px solid var(--c);color:var(--c);background:transparent;border-radius:20px;padding:5px 10px;cursor:pointer}}
.bar button.on{{background:var(--c);color:#fff}}
.card{{background:var(--card);border:1px solid var(--bd);border-radius:10px;margin:8px 0;padding:10px 14px}}
summary{{cursor:pointer;display:flex;flex-wrap:wrap;gap:6px 10px;align-items:baseline}}
.tag{{color:#fff;font-size:12px;border-radius:12px;padding:2px 8px;white-space:nowrap}}
.meta{{color:var(--mut);font-size:13px;width:100%}} .corpo img{{max-width:100%;border-radius:6px;margin-top:10px}}
.links{{font-size:14px}} table{{border-collapse:collapse}} td,th{{border:1px solid var(--bd);padding:4px 8px}} a{{color:#2563eb}}
</style></head><body><main>
<h1>{html.escape(a.titulo)}</h1><p style="color:var(--mut)">{len(itens)} vídeos · veracidade, conhecimento embutido e tecnologia para recriar</p>
<div class="geral">{geral}</div>
<div class="bar"><input id="q" placeholder="Buscar por perfil, tema, ferramenta…">{filtros}</div>
<div id="lista">{''.join(cards)}</div></main>
<script>
let f=null;const q=document.getElementById('q');
function ap(){{const t=q.value.toLowerCase();document.querySelectorAll('.card').forEach(c=>{{c.style.display=((!f||c.dataset.cat===f)&&(!t||c.dataset.busca.includes(t)))?'':'none'}})}}
document.querySelectorAll('.bar button').forEach(b=>b.onclick=()=>{{f=f===b.dataset.f?null:b.dataset.f;document.querySelectorAll('.bar button').forEach(x=>x.classList.toggle('on',x.dataset.f===f));ap()}});
q.oninput=ap;
</script></body></html>"""
(base / "RELATORIO.html").write_text(page)
print(len(itens), cont)
