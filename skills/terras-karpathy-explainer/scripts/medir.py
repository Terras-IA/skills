#!/usr/bin/env python3
"""Mede um texto contra as metas de escrita controlada (ASD-STE100) da skill.

    python3 medir.py explicacao.md               # meta "80%"
    python3 medir.py explicacao.md --rigor 100   # STE completo
    python3 medir.py - < texto.md                # lê da entrada padrão

Item de lista numerada conta como frase de procedimento (teto 20 palavras);
o resto, como descrição (teto 25). Bloco de código, tabela e título são ignorados.
Sai com código 1 quando reprova.
"""
import argparse
import re
import sys

TETO_PROC, TETO_DESC, MAX_PARAG, MEDIA_DESC = 20, 25, 6, 18
METAS = {  # rigor -> (fração de frases acima do teto, fração de passivas)
    80: (0.20, 0.10),
    100: (0.0, 0.0),
}
PASSIVA = re.compile(
    r"\b(é|são|foi|foram|será|serão|seja|sejam|sendo|sido|era|eram"
    r"|is|are|was|were|be|been|being)\s+(\w+\s+)?"
    r"\w+(ado|ada|ados|adas|ido|ida|idos|idas|ed|en)\b",
    re.IGNORECASE,
)
FIM_FRASE = re.compile(r"(?<=[.!?])\s+(?=[\"'(«A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9])")


def blocos(texto):
    """Devolve parágrafos como (é_procedimento, [linhas]) sem código, tabela e título."""
    em_codigo, atual, saida = False, [], []
    def fecha():
        if atual:
            saida.append(list(atual))
            atual.clear()
    for linha in texto.splitlines():
        s = linha.strip()
        if s.startswith("```"):
            em_codigo = not em_codigo
            fecha()
            continue
        if em_codigo or s.startswith(("#", "|", ">")) or not s:
            fecha()
            continue
        if re.match(r"^(\d+[.)]|[-*+])\s+", s):
            fecha()
            saida.append([s])  # item de lista é um bloco próprio
            continue
        atual.append(s)
    fecha()
    return saida


def frases(bloco):
    texto = " ".join(bloco)
    proc = bool(re.match(r"^\d+[.)]\s+", texto))
    texto = re.sub(r"^(\d+[.)]|[-*+])\s+", "", texto)
    texto = re.sub(r"`[^`]*`", "X", texto)  # código inline vale uma palavra
    texto = re.sub(r"\*\*|__|\*|_", "", texto)
    partes = [p.strip() for p in FIM_FRASE.split(texto) if p.strip()]
    return proc, partes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--rigor", type=int, choices=sorted(METAS), default=80)
    a = ap.parse_args()
    texto = sys.stdin.read() if a.arquivo == "-" else open(a.arquivo, encoding="utf-8").read()
    frac_longa, frac_passiva = METAS[a.rigor]

    todas, longas, passivas, parag_longos, desc = [], [], [], [], []
    for bloco in blocos(texto):
        proc, fs = frases(bloco)
        if len(fs) > MAX_PARAG:
            parag_longos.append((len(fs), fs[0][:60]))
        for f in fs:
            n = len(f.split())
            teto = TETO_PROC if proc else TETO_DESC
            todas.append(n)
            if not proc:
                desc.append(n)
            if n > teto:
                longas.append((n, teto, f))
            if PASSIVA.search(f):
                passivas.append(f)

    if not todas:
        print("REPROVA: nenhuma frase encontrada.")
        return 1
    total = len(todas)
    media_desc = sum(desc) / len(desc) if desc else 0
    falhas = []
    if len(longas) > frac_longa * total:
        falhas.append(f"{len(longas)} frase(s) acima do teto (limite {int(frac_longa * total)})")
    if any(n > TETO_DESC + 10 for n, _, _ in longas) and a.rigor == 80:
        falhas.append("frase com mais de 35 palavras: nem a folga de 80% cobre")
    if media_desc > MEDIA_DESC and a.rigor == 80:
        falhas.append(f"média de descrição {media_desc:.1f} > {MEDIA_DESC}")
    if len(passivas) > frac_passiva * total:
        falhas.append(f"{len(passivas)} passiva(s) (limite {int(frac_passiva * total)})")
    if parag_longos:
        falhas.append(f"{len(parag_longos)} parágrafo(s) com mais de {MAX_PARAG} frases")

    status = "PASSA" if not falhas else "REPROVA"
    print(f"{status} (rigor {a.rigor}%): {total} frases, média {sum(todas) / total:.1f}, "
          f"máx {max(todas)}, longas {len(longas)}, passivas {len(passivas)}")
    for f in falhas:
        print(f"  - {f}")
    for n, teto, f in longas:
        print(f"  [longa {n}/{teto}] {f}")
    for f in passivas:
        print(f"  [passiva] {f}")
    for n, inicio in parag_longos:
        print(f"  [parágrafo {n} frases] {inicio}...")
    return 0 if not falhas else 1


if __name__ == "__main__":
    sys.exit(main())
