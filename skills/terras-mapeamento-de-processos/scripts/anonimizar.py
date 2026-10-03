#!/usr/bin/env python3
"""Anonimiza os artefatos de um processo: troca nomes por rótulos genéricos.

Use quando o material sair do cliente (ou quando pedirem): nome da empresa vira
"Cliente X", o assistente de IA perde o nome próprio ("Agente de IA") e pessoas
viram papel ("a analista", "o responsável"). O nome do cliente aparece no título
do desenho e no corpo do relatório — trocar só o texto não basta.

Uso:
  python3 anonimizar.py --pasta processos/acme --mapa "Acme=Cliente X;Maya=Agente de IA"
  python3 anonimizar.py --pasta processos/acme --mapa-arquivo mapa.json --dry-run
  python3 anonimizar.py --pasta processos/acme --mapa "Acme=Cliente X" --regerar-png

Regras:
  --mapa          pares "de=para" separados por ";". Casa palavra inteira e,
                  por padrão, ignora maiúsculas/minúsculas (use --sensivel-maiuscula
                  para casar exatamente como escrito).
  --mapa-arquivo  JSON {"Acme": "Cliente X", "Maya": "Agente de IA"}.
  Arquivos de texto: .md .json .mmd .svg .txt .csv .log .vtt .srt .html .d2 .yaml .yml
  Arquivos com o nome no filename são renomeados ("relatorio-acme.md" -> "relatorio-cliente-x.md").
  PNG/PDF não são editáveis: regenere com render_fluxo.py (use --regerar-png) e re-renderize o PDF.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import unicodedata

EXTENSOES_TEXTO = {".md", ".json", ".mmd", ".svg", ".txt", ".csv", ".log", ".vtt", ".srt",
                   ".html", ".htm", ".d2", ".yaml", ".yml", ".tex", ".py", ".sh"}
EXTENSOES_BINARIAS = {".png", ".jpg", ".jpeg", ".pdf", ".mp4", ".mp3", ".wav", ".webm", ".zip"}
IGNORAR_PASTAS = {"node_modules", ".git", "__pycache__", ".venv", "venv"}


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower()
    return t or "anonimo"


def compilar(mapa, sensivel):
    regras = []
    for de, para in mapa.items():
        de = (de or "").strip()
        if not de:
            continue
        padrao = re.compile(r"(?<!\w)" + re.escape(de) + r"(?!\w)", 0 if sensivel else re.IGNORECASE)
        regras.append((de, para, padrao))
    return regras


def anonimizar_texto(texto, regras):
    total = {}
    for de, para, padrao in regras:
        texto, n = padrao.subn(para, texto)
        if n:
            total[de] = total.get(de, 0) + n
    return texto, total


def main() -> int:
    ap = argparse.ArgumentParser(description="anonimiza os artefatos de um processo")
    ap.add_argument("--pasta", required=True)
    ap.add_argument("--mapa", default=None, help='"De=Para;De2=Para2"')
    ap.add_argument("--mapa-arquivo", default=None, help="JSON {De: Para}")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sensivel-maiuscula", action="store_true", help="casa exatamente como escrito")
    ap.add_argument("--regerar-png", action="store_true", help="roda render_fluxo.py nos processo*.json depois")
    args = ap.parse_args()

    mapa = {}
    if args.mapa_arquivo:
        mapa.update(json.loads(pathlib.Path(args.mapa_arquivo).read_text(encoding="utf-8")))
    for par in (args.mapa or "").split(";"):
        if "=" in par:
            de, para = par.split("=", 1)
            mapa[de.strip()] = para.strip()
    if not mapa:
        raise SystemExit("informe --mapa \"De=Para;...\" ou --mapa-arquivo mapa.json")

    raiz = pathlib.Path(args.pasta)
    if not raiz.is_dir():
        raise SystemExit("pasta não encontrada: {}".format(raiz))
    regras = compilar(mapa, args.sensivel_maiuscula)

    tocados, renomeados, binarios, total = [], [], [], {}
    for caminho in sorted(raiz.rglob("*")):
        if not caminho.is_file() or any(p in IGNORAR_PASTAS for p in caminho.parts):
            continue
        if caminho.suffix.lower() in EXTENSOES_BINARIAS:
            binarios.append(caminho)
            continue
        if caminho.suffix.lower() not in EXTENSOES_TEXTO:
            continue
        try:
            original = caminho.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            binarios.append(caminho)
            continue
        novo, contagem = anonimizar_texto(original, regras)
        if contagem:
            tocados.append((caminho, contagem))
            for k, v in contagem.items():
                total[k] = total.get(k, 0) + v
            if not args.dry_run:
                caminho.write_text(novo, encoding="utf-8")
        # nome do arquivo
        novo_nome = caminho.name
        for de, para, padrao in regras:
            novo_nome = padrao.sub(slug(para), novo_nome)
        # variante com hífen, como o nome aparece em arquivo (relatorio-cliente-x.md)
        for de, para, _ in regras:
            padrao_slug = re.compile(r"(?<!\w)" + re.escape(slug(de)) + r"(?!\w)", re.IGNORECASE)
            novo_nome = padrao_slug.sub(slug(para), novo_nome)
        if novo_nome != caminho.name:
            destino = caminho.with_name(novo_nome)
            renomeados.append((caminho, destino))
            if not args.dry_run:
                caminho.rename(destino)

    print("Mapa aplicado: " + " | ".join("{}=>{}".format(k, v) for k, v in mapa.items()))
    print("Arquivos alterados: {}".format(len(tocados)))
    for caminho, contagem in tocados:
        print("  - {}: {}".format(caminho.relative_to(raiz),
                                  ", ".join("{}× {}".format(v, k) for k, v in contagem.items())))
    if renomeados:
        print("Renomeados:")
        for origem, destino in renomeados:
            print("  - {} -> {}".format(origem.name, destino.name))
    if total:
        print("Total de substituições: " + ", ".join("{}× {}".format(v, k) for k, v in total.items()))
    if binarios:
        print("Imagens/documentos que precisam ser regerados (o texto está dentro do desenho):")
        for b in binarios:
            print("  - {}".format(b.relative_to(raiz)))
    if args.dry_run:
        print("(--dry-run: nada foi gravado)")
        return 0

    if args.regerar_png:
        skill = pathlib.Path(__file__).resolve().parent
        for nome_json, nome_saida in (("processo.json", "as-is"), ("processo-to-be.json", "to-be")):
            candidatos = [p for p in raiz.rglob(nome_json) if p.is_file()]
            if not candidatos:
                continue
            js = sorted(candidatos, key=lambda p: len(p.parts))[0]
            saida = js.parent / nome_saida
            cmd = [sys.executable, str(skill / "render_fluxo.py"), "--json", str(js),
                   "--saida", str(saida), "--png"]
            print("+ " + " ".join(cmd[1:]))
            subprocess.run(cmd, check=False)
    elif binarios:
        print("Rode de novo o render_fluxo.py (--regerar-png) para o título anonimizado aparecer no desenho.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
