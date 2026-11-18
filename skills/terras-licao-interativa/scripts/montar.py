#!/usr/bin/env python3
"""Valida um curso.json e monta a página única (HTML autocontido) da lição interativa.

Uso:
  python3 montar.py curso.json -o saida.html
  python3 montar.py curso.json --checar        # só valida
  python3 montar.py curso.json -o pagina.html --artifact   # para o tool Artifact

Sai com código 1 se houver erro. Avisos não bloqueiam.
"""
import argparse
import json
import re
import sys
from pathlib import Path

MOTOR = Path(__file__).resolve().parent.parent / "motor"
TIPOS_NO = {"caixa", "banco", "pessoas", "fila", "zona", "rotulo", "placa"}
TONS = {"azul", "verde", "laranja", "roxo", "rosa", "amarelo", "cinza", "vermelho", "teal"}
ESTADOS = {"normal", "caido", "quente", "fantasma"}
TIPOS_PASSO = {"contexto", "problema", "solucao", "tecnica", "troca", "resumo"}


def validar(c):
    erros, avisos = [], []
    validar_tema(c.get("tema"), erros)
    if not c.get("titulo"):
        erros.append("curso: falta 'titulo'")
    mods = c.get("modulos") or []
    if not mods:
        erros.append("curso: falta 'modulos' com ao menos uma lição")
    ids = set()
    for mi, m in enumerate(mods, 1):
        for l in m.get("licoes") or []:
            lid = l.get("id")
            onde = f"lição '{lid or '?'}' (módulo {mi})"
            if not lid:
                erros.append(f"{onde}: falta 'id'")
            elif lid in ids:
                erros.append(f"{onde}: id repetido")
            ids.add(lid)
            if lid and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", str(lid)):
                erros.append(f"{onde}: id só com letras minúsculas, dígitos e hífen (vira âncora #<id>-p<passo>)")
            mets = {m2.get("id") for m2 in l.get("metricas") or []}
            nos = {}
            for n in (l.get("cena") or {}).get("nos") or []:
                if not n.get("id"):
                    erros.append(f"{onde}: nó da cena sem 'id'")
                    continue
                if n["id"] in nos:
                    erros.append(f"{onde}: nó '{n['id']}' repetido na cena")
                nos[n["id"]] = dict(n)
            lig = (l.get("cena") or {}).get("ligacoes") or []
            passos = l.get("passos") or []
            if len(passos) < 2:
                erros.append(f"{onde}: precisa de ao menos 2 passos")
            elif len(passos) < 4:
                avisos.append(f"{onde}: só {len(passos)} passos; lição boa costuma ter 6 a 12")
            for pi, p in enumerate(passos, 1):
                op = f"{onde}, passo {pi}"
                for k in ("titulo", "texto", "rotulo"):
                    if not p.get(k):
                        erros.append(f"{op}: falta '{k}'")
                if len(p.get("rotulo") or "") > 14:
                    avisos.append(f"{op}: rótulo da linha do tempo com mais de 14 caracteres")
                if p.get("tipo") and p["tipo"] not in TIPOS_PASSO:
                    erros.append(f"{op}: tipo '{p['tipo']}' inválido ({', '.join(sorted(TIPOS_PASSO))})")
                if len(p.get("texto") or "") > 700:
                    avisos.append(f"{op}: texto com mais de 700 caracteres; o painel fica longo")
                for nid, patch in (p.get("nos") or {}).items():
                    if patch is None:
                        if nid not in nos:
                            avisos.append(f"{op}: remove '{nid}', que não existe")
                        nos.pop(nid, None)
                        continue
                    novo = dict(nos.get(nid, {}))
                    novo.update(patch)
                    novo["id"] = nid
                    nos[nid] = novo
                for k in (p.get("metricas") or {}):
                    if k not in mets:
                        erros.append(f"{op}: métrica '{k}' não declarada em 'metricas' da lição")
                if p.get("ligacoes") is not None:
                    lig = p["ligacoes"]
                for g in lig:
                    for ponta in ("de", "para"):
                        alvo = g.get(ponta)
                        if alvo not in nos:
                            erros.append(f"{op}: ligação {g.get('de')}→{g.get('para')} aponta para '{alvo}', que não existe neste passo")
                        elif nos[alvo].get("oculto"):
                            avisos.append(f"{op}: ligação {g.get('de')}→{g.get('para')} usa nó oculto '{alvo}' (a linha aparece sem o nó)")
                    if g.get("falha", 0) >= 0.8 and g.get("falhaEm", 0.6) < 1:
                        avisos.append(f"{op}: ligação {g.get('de')}→{g.get('para')} com falha {g['falha']}: quase nada chega; é isso mesmo?")
                    if g.get("cor") and g["cor"] not in TONS:
                        erros.append(f"{op}: cor de ligação '{g['cor']}' inválida")
                q = p.get("quiz")
                if q:
                    ops = q.get("opcoes") or []
                    if len(ops) < 2 or not isinstance(q.get("certa"), int) or not 0 <= q["certa"] < len(ops):
                        erros.append(f"{op}: quiz precisa de 'opcoes' (2+) e 'certa' (índice a partir de 0)")
                for nid, n in nos.items():
                    if n.get("tipo", "caixa") not in TIPOS_NO:
                        erros.append(f"{op}: nó '{nid}' com tipo '{n.get('tipo')}' inválido ({', '.join(sorted(TIPOS_NO))})")
                    if "x" not in n or "y" not in n:
                        erros.append(f"{op}: nó '{nid}' sem 'x' e 'y' (nó novo em passo precisa da definição completa)")
                    if n.get("tom") and n["tom"] not in TONS:
                        erros.append(f"{op}: nó '{nid}' com tom '{n['tom']}' inválido ({', '.join(sorted(TONS))})")
                    if n.get("estado") and n["estado"] not in ESTADOS:
                        erros.append(f"{op}: nó '{nid}' com estado '{n['estado']}' inválido")
                    if n.get("tipo", "caixa") in ("caixa", "banco") and not n.get("rotulo"):
                        avisos.append(f"{op}: nó '{nid}' sem rótulo")
                    if n.get("tipo", "caixa") == "caixa" and len(n.get("rotulo") or "") > 22:
                        avisos.append(f"{op}: rótulo de '{nid}' longo demais para o topo da caixa (máx. ~22)")
                    if len(str(n.get("selo") or "")) > 18:
                        avisos.append(f"{op}: selo de '{nid}' com mais de 18 caracteres; detalhe vai melhor numa placa")
                    if n.get("tipo") == "banco" and len(n.get("rotulo") or "") > 16:
                        avisos.append(f"{op}: rótulo do banco '{nid}' longo (vai numa pílula à direita); máx. ~16")
                    if n.get("tipo") == "placa" and len(n.get("linhas") or []) > 6:
                        avisos.append(f"{op}: placa '{nid}' com mais de 6 linhas; o resto não aparece")
                # nós encostados no mesmo passo (distância de grade < 1,6)
                solidos = [(nid, n) for nid, n in nos.items()
                           if not n.get("oculto") and n.get("tipo", "caixa") in ("caixa", "banco", "pessoas", "fila")
                           and isinstance(n.get("x"), (int, float)) and isinstance(n.get("y"), (int, float))]
                pontos = []
                for nid, n in solidos:
                    k = n.get("quantidade", 5) if n.get("tipo") == "fila" else 1
                    e = n.get("espaco", 0.6)
                    for i in range(k):
                        dx, dy = ((0, e * i) if n.get("direcao") == "y" else (e * i, 0)) if n.get("tipo") == "fila" else (0, 0)
                        pontos.append((nid, n["x"] + dx, n["y"] + dy))
                ja = set()
                for i, (a1, x1, y1) in enumerate(pontos):
                    for a2, x2, y2 in pontos[i + 1:]:
                        if a1 != a2 and (a1, a2) not in ja and ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 < 1.6:
                            ja.add((a1, a2))
                            avisos.append(f"{op}: '{a1}' e '{a2}' encostados (distância < 1,6 na grade); afaste para 2")
            for o in l.get("objetivos") or []:
                if o.get("passo") and o["passo"] > len(passos):
                    erros.append(f"{onde}: objetivo '{o.get('texto', '')[:30]}' marca passo {o['passo']} > {len(passos)}")
    return erros, avisos


def para_artifact(html):
    """O Artifact embrulha a página no próprio esqueleto: tira doctype, html, head e body."""
    html = re.sub(r"<!doctype html>\s*", "", html, flags=re.I)
    html = re.sub(r"</?(html|head|body)[^>]*>\s*", "", html, flags=re.I)
    html = re.sub(r'<meta charset="utf-8">\s*', "", html)
    html = re.sub(r'<meta name="viewport"[^>]*>\s*', "", html)
    return html


VAR_CSS = re.compile(r"^[a-z][a-z0-9-]{0,40}$")


def validar_tema(t, erros):
    if t is None:
        return
    if not isinstance(t, dict):
        erros.append("tema: precisa ser um objeto")
        return
    for k in ("cores", "coresEscuro"):
        for nome, v in (t.get(k) or {}).items():
            if not VAR_CSS.match(nome) or not isinstance(v, str) or any(ch in v for ch in ";{}<>"):
                erros.append(f"tema.{k}: '{nome}' inválido (nome de variável sem '--' e valor CSS simples)")
    for nome, v in (t.get("tons") or {}).items():
        if not (isinstance(v, list) and len(v) == 4 and all(isinstance(x, str) and re.match(r"^#[0-9a-fA-F]{3,8}$", x) for x in v)):
            erros.append(f"tema.tons: '{nome}' precisa de 4 cores hex [topo, face esq., face dir., contorno]")
    for f in t.get("fontes") or []:
        if not isinstance(f, str) or not re.match(r"^[A-Za-z0-9 ]+(:[a-z,@;0-9.]+)?$", f):
            erros.append(f"tema.fontes: '{f}' não parece família do Google Fonts ('Open Sans:wght@400;700')")
    if "css" in t and "</" in str(t["css"]):
        erros.append("tema.css: não pode conter '</'")


def css_tema(t):
    if not t:
        return "", "", '<span class="marca-ic" aria-hidden="true">◆</span>'
    fontes = ""
    if t.get("fontes"):
        fam = "&".join("family=" + f.replace(" ", "+") for f in t["fontes"])
        fontes = f'<link href="https://fonts.googleapis.com/css2?{fam}&display=swap" rel="stylesheet">'
    def bloco(d):
        return "".join(f"--{k}:{v};" for k, v in d.items())
    claro = dict(t.get("cores") or {})
    if t.get("fonteTexto"):
        claro["texto"] = t["fonteTexto"]
    if t.get("fonteTitulo"):
        claro["titulo"] = t["fonteTitulo"]
    css = f":root{{{bloco(claro)}}}\n" if claro else ""
    if t.get("coresEscuro"):
        e = bloco(t["coresEscuro"])
        css += (f'@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{{e}}}}}\n'
                f':root[data-theme="dark"]{{{e}}}\n')
    css += str(t.get("css") or "")
    marca = '<span class="marca-ic" aria-hidden="true">◆</span>'
    if t.get("logo"):
        alt = str(t.get("logoAlt", "")).replace('"', "&quot;")
        marca = f'<img class="marca-logo" src="{t["logo"]}" alt="{alt}">'
    return fontes, css, marca


def montar(c, saida, artifact=False):
    modelo = (MOTOR / "modelo.html").read_text(encoding="utf-8")
    css = (MOTOR / "cena.css").read_text(encoding="utf-8")
    js = (MOTOR / "cena.js").read_text(encoding="utf-8")
    dados = json.dumps(c, ensure_ascii=False).replace("</", "<\\/")
    titulo = str(c.get("titulo", "Lições")).replace("<", "&lt;")
    html = (modelo.replace("__LANG__", c.get("idioma", "pt-BR")).replace("__TITULO__", titulo)
            .replace("/*CSS*/", css).replace("/*DADOS*/", dados).replace("/*JS*/", js))
    fontes, tema, marca = css_tema(c.get("tema"))
    html = html.replace("<!--FONTES-->", fontes, 1).replace("/*TEMA*/", tema, 1).replace("<!--MARCA-->", marca, 1)
    if artifact:
        html = para_artifact(html)
    Path(saida).write_text(html, encoding="utf-8")
    return len(html.encode("utf-8"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("curso")
    ap.add_argument("-o", "--saida")
    ap.add_argument("--checar", action="store_true", help="só valida")
    ap.add_argument("--artifact", action="store_true", help="sem doctype/html/head/body, para publicar com o tool Artifact")
    a = ap.parse_args()
    try:
        c = json.loads(Path(a.curso).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "erro", "erros": [f"JSON inválido: {e}"]}, ensure_ascii=False, indent=2))
        sys.exit(1)
    erros, avisos = validar(c)
    res = {"status": "erro" if erros else "ok", "licoes": sum(len(m.get("licoes") or []) for m in c.get("modulos") or []),
           "passos": sum(len(l.get("passos") or []) for m in c.get("modulos") or [] for l in m.get("licoes") or []),
           "erros": erros, "avisos": avisos}
    if not erros and not a.checar:
        if not a.saida:
            a.saida = str(Path(a.curso).with_suffix(".html"))
        res["saida"] = str(Path(a.saida).resolve())
        res["bytes"] = montar(c, a.saida, a.artifact)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
