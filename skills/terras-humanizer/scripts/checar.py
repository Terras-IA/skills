#!/usr/bin/env python3
"""Verificador da terras-humanizer: acha marcas de texto de IA por regra, sem modelo.

Só lê. Aponta trecho, linha e nível de cada achado; quem decide a reescrita é quem escreve.

Uso:
  checar.py arquivo.md [outro.md ...]     um texto por arquivo
  checar.py -                             lê um texto da entrada padrão
  checar.py --lote textos.json            lista JSON de textos (ou de objetos com --campo)
  checar.py --lote textos.json --campo en
  checar.py --testar                      roda os casos de tests/casos.json

Opções:
  --json              saída em JSON
  --sem-hashtag       hashtag vira regra dura (comentário de LinkedIn)
  --lingua pt|en      força a língua (padrão: detecta por texto)

Níveis:
  duro     regra dura da skill (travessão, resíduo de chat). Sai com código 1.
  forte    um dos cinco padrões fortes ou linguagem de venda. Sai com código 1.
  atencao  sinal fraco sozinho; pesa quando se repete no texto ou no lote.

No lote, além de cada texto, o verificador compara os textos entre si: mesma abertura,
mesmo tipo de fecho (contraste, "so...", dois-pontos) e a proporção de cada um.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
REF = SKILL / 'references'

# ---------------------------------------------------------------- limpeza

def prosa(texto):
    """Tira o que não é prosa: bloco de código, código inline, URL, caminho."""
    t = re.sub(r'```.*?```', lambda m: '\n' * m.group(0).count('\n'), texto, flags=re.S)
    t = re.sub(r'`[^`\n]+`', 'CODIGO', t)
    t = re.sub(r'https?://\S+', 'URL', t)
    t = re.sub(r'(?<!\w)(?:~|\.{1,2})?/[\w.\-/]+', 'CAMINHO', t)
    return t


def frases(paragrafo):
    partes = re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ"“(])', paragrafo.strip())
    return [p for p in partes if p.strip()]


def paragrafos(t):
    return [p for p in re.split(r'\n\s*\n', t) if p.strip()]


def detectar_lingua(t):
    w = re.findall(r"[a-záéíóúâêôãõçà']+", t.lower())
    en = sum(x in {'the', 'and', 'of', 'to', 'is', "it's", 'that', 'with', 'you', 'i'} for x in w)
    pt = sum(x in {'de', 'que', 'não', 'o', 'a', 'é', 'para', 'com', 'um', 'uma', 'os', 'em'} for x in w)
    return 'en' if en > pt else 'pt'

# ---------------------------------------------------------------- listas das referências

def _tabela(md, ate=None):
    """Primeira coluna das tabelas markdown de um arquivo, até o título `ate`."""
    if ate and ate in md:
        md = md[:md.index(ate)]
    termos = []
    for linha in md.splitlines():
        m = re.match(r'\|\s*([^|]+?)\s*\|', linha)
        if not m or set(m.group(1)) <= set('-: ') or m.group(1).lower() in {'em vez de', 'palavra ou expressão'}:
            continue
        cel = re.sub(r'\([^)]*\)', '', m.group(1))
        for t in cel.split(','):
            t = t.strip().lower()
            if t and 'x' not in t.split() and len(t) > 2:
                termos.append(t)
    return termos


def listas():
    b1 = _tabela((REF / 'ingles-b1b2.md').read_text(encoding='utf-8'), '## O que não é problema de nível')
    b1 = [t for t in b1 if t not in {'the majority of', 'a number of'}]
    pt = (REF / 'padroes-pt.md').read_text(encoding='utf-8')
    sec = pt[pt.index('### 12.'):pt.index('### 13.')] if '### 12.' in pt else ''
    ia_pt = [t for t in _tabela(sec) if not re.search(r'[a-z]+ en:', t)]
    return b1, ia_pt

# ---------------------------------------------------------------- padrões

def rx(*termos):
    return re.compile(r'(?<![\w-])(?:' + '|'.join(termos) + r')(?![\w-])', re.I)

PADROES = {
    'pt': {
        'ditado': rx('a verdadeira questão', 'no fundo', 'na essência', 'o que realmente importa', 'em última análise',
                     'o cerne da questão', 'vira uma armadilha'),
        'aquecimento': rx('vamos mergulhar', 'vamos explorar', 'vamos destrinchar', 'aqui está o que você precisa saber',
                          'sem mais delongas', 'vale destacar', 'é importante ressaltar', 'antes de tudo', 'olha só',
                          'sinceramente\\?', 'a real é que'),
        'briga com ninguém': rx('não estou dizendo que', 'para deixar claro', 'não me entenda mal', 'isso não quer dizer que',
                                'alguém poderia argumentar', 'pode-se pensar que'),
        'venda': rx('solução robusta', 'plataforma completa', 'transformador[a]?', 'revolucionári[oa]', 'disruptiv[oa]',
                    'eleve (seu|sua|o seu|a sua)', 'desbloqueie', 'potencialize', 'de tirar o fôlego', 'imperdível',
                    'no coração de'),
        'resíduo de chat': rx('espero ter ajudado', 'claro!', 'certamente!', 'ótima pergunta', 'quer que eu',
                              'gostaria que eu', 'fico à disposição', 'me avise se'),
        'contraste': [
            re.compile(r'\bnão (?:é|são|era|foi|se trata de)\b(?! (?:minha|meu|nossa|nosso) )[^.!?]{1,80}?[,;:]\s*(?:é|são|era|foi|mas (?:é|são|sim|sobre|de|da|do|um|uma|o|a|os|as)|e sim)\b', re.I),
            re.compile(r'\bnão (?:apenas|só|somente)\b[^.!?]{1,90}?\bmas\b', re.I),
        ],
        'contraste partido': (re.compile(r'^(?:isso |o problema |a questão )?não (?:é|são|era)\b', re.I),
                              re.compile(r'^(?:é|são|era)\b', re.I)),
        'contraste no fim': re.compile(r'\b(?:em vez de|ao invés de|e não|não porque|não antes|e sim)\b', re.I),
        'fecho de moral': re.compile(r',\s*(?:para que|para (?:o|a|os|as) [^,.!?]+ continuar|assim|e assim)\b[^,.!?]*[.!?]?$', re.I),
        'elogio-ponte': re.compile(r'^(?:ótimo post|excelente post|que post|gostei muito|amei|adorei|o que eu gostei|parabéns pelo post)\b', re.I),
    },
    'en': {
        'ditado': rx('the real question', 'at its core', 'at the end of the day', 'what really matters',
                     'the heart of the matter', 'the language of', 'is a trap'),
        'aquecimento': rx("let's dive", 'let’s dive', 'dive into', "let's explore", "here's the thing", 'here’s the thing',
                          "here's why", "here's what you need to know", 'it is worth noting', "it's worth noting",
                          'it is important to note', 'without further ado', 'honestly\\?'),
        'briga com ninguém': rx("i'm not saying", 'i am not saying', 'to be clear', "don't get me wrong",
                                'one might argue', 'some would argue', 'that is not to say'),
        'venda': rx('robust solution', 'game[- ]changer', 'transformative', 'revolutionary', 'unlock the (?:full )?potential',
                    'elevate your', 'seamless(?:ly)?', 'cutting[- ]edge', 'world[- ]class', 'next[- ]level'),
        'resíduo de chat': rx('i hope this helps', 'great question', 'certainly!', 'absolutely!', 'let me know if',
                              'would you like me to', 'happy to help', 'feel free to ask'),
        'contraste': [
            re.compile(r"\bnot (?:just|only|merely|simply)\b[^.!?]{1,90}?\bbut\b", re.I),
            re.compile(r"\b(?:isn'?t|is not|aren'?t|wasn'?t)\b[^.!?]{1,80}?[,;:]\s*(?:it'?s|they'?re|but|it is)\b", re.I),
            re.compile(r"\bit'?s not (?:about )?[^.!?]{1,60}?[,;]\s*it'?s\b", re.I),
        ],
        'contraste partido': (re.compile(r"^(?:it|this|that)(?:'s| is| was) not\b|^(?:it|this|that) isn'?t\b", re.I),
                              re.compile(r"^(?:it|this|that)(?:'s| is| was)\b", re.I)),
        'contraste no fim': re.compile(r"\b(?:instead of|rather than|not because|not before)\b|,\s*not\s+(?!only|just)\w", re.I),
        'fecho de moral': re.compile(r",\s*so(?: that)? (?!far\b|much\b|many\b|on\b|i\b|i'd\b|i'll\b|we\b|we'd\b)\w[^,.!?]*[.!?]?$", re.I),
        'elogio-ponte': re.compile(r"^(?:great (?:post|point|breakdown|read)|love this|loved this|the part i (?:liked|loved)|"
                                   r"what i liked|this is (?:gold|spot on)|spot on)\b", re.I),
    },
}

EMOJI = re.compile('[\U0001F300-\U0001FAFF☀-➿⭐✅]')
TRAVESSAO = re.compile(r'[—–]|(?<=\s)--(?=\s)')
HASHTAG = re.compile(r'(?:^|\s)#[^\s#\d]\w*')
DOIS_PONTOS = re.compile(r'[a-zà-ú)]\s*:\s+[a-zà-ú]')  # "X: y" no meio da frase (revelação)
TRIO = re.compile(r'\b[\w-]+(?: [\w-]+)?, [\w-]+(?: [\w-]+)?,? (?:and|e|or|ou) [\w-]+', re.I)
NEGRITO_ROTULO = re.compile(r'^\s*(?:[-*]|\d+\.)?\s*\*\*[^*]+\*\*\s*[:.]', re.M)
ASPAS_CURVAS = re.compile('[“”‘’]')

# ---------------------------------------------------------------- verificação de um texto

def achado(regra, nivel, trecho, linha):
    return {'regra': regra, 'nivel': nivel, 'trecho': trecho.strip()[:120], 'linha': linha}


def linha_de(texto, pos):
    return texto.count('\n', 0, pos) + 1


def checar(texto, lingua=None, sem_hashtag=False, b1=(), ia_pt=()):
    t = prosa(texto)
    lingua = lingua or detectar_lingua(t)
    P = PADROES[lingua]
    out = []

    for m in TRAVESSAO.finditer(t):
        out.append(achado('travessão', 'duro', t[max(0, m.start() - 30):m.end() + 30], linha_de(t, m.start())))
    if sem_hashtag:
        for m in HASHTAG.finditer(t):
            out.append(achado('hashtag', 'duro', m.group(0), linha_de(t, m.start())))
    for regra in ('resíduo de chat',):
        for m in P[regra].finditer(t):
            out.append(achado(regra, 'duro', m.group(0), linha_de(t, m.start())))
    for regra in ('ditado', 'aquecimento', 'briga com ninguém', 'venda'):
        for m in P[regra].finditer(t):
            out.append(achado(regra, 'forte', m.group(0), linha_de(t, m.start())))
    for r in P['contraste']:
        for m in r.finditer(t):
            out.append(achado('não é X, é Y', 'forte', m.group(0), linha_de(t, m.start())))
    for m in EMOJI.finditer(t):
        out.append(achado('emoji', 'atencao', t[max(0, m.start() - 20):m.end() + 5], linha_de(t, m.start())))
    for m in NEGRITO_ROTULO.finditer(t):
        out.append(achado('negrito de rótulo', 'atencao', m.group(0), linha_de(t, m.start())))
    if ASPAS_CURVAS.search(t):
        out.append(achado('aspas curvas', 'atencao', ASPAS_CURVAS.search(t).group(0), linha_de(t, ASPAS_CURVAS.search(t).start())))

    pars = paragrafos(t)
    todas = [f for p in pars for f in frases(p)]
    a, b = P['contraste partido']
    for f1, f2 in zip(todas, todas[1:]):
        if a.search(f1) and b.search(f2):
            out.append(achado('não é X, é Y (partido)', 'forte', f1 + ' ' + f2, linha_de(t, t.find(f1))))

    # Fecho de uma linha: último parágrafo com uma frase curta depois de parágrafo longo.
    if len(pars) >= 2 and len(frases(pars[-1])) == 1 and len(pars[-1].split()) <= 8 and len(pars[-2].split()) >= 25:
        out.append(achado('fecho de uma linha', 'forte', pars[-1], linha_de(t, t.rfind(pars[-1]))))

    if todas:
        ini, fim = todas[0], todas[-1]
        if P['elogio-ponte'].search(ini):
            out.append(achado('elogio-ponte na abertura', 'atencao', ini, 1))
        if P['contraste no fim'].search(fim):
            out.append(achado('contraste no fim', 'atencao', fim, linha_de(t, t.rfind(fim))))
        if P['fecho de moral'].search(fim):
            out.append(achado('fecho de moral ("so..." / "para que...")', 'atencao', fim, linha_de(t, t.rfind(fim))))

    dp = [m for m in DOIS_PONTOS.finditer(t)]
    if len(dp) >= 2 or (dp and len(todas) <= 4):
        out.append(achado('dois-pontos de revelação', 'atencao',
                          t[max(0, dp[0].start() - 40):dp[0].end() + 30], linha_de(t, dp[0].start())))
    trios = TRIO.findall(t)
    if len(trios) >= 2:
        out.append(achado('trio por hábito', 'atencao', trios[0], linha_de(t, t.find(trios[0]))))

    # Aberturas repetidas: três frases seguidas com a mesma primeira palavra.
    for i in range(len(todas) - 2):
        w = [f.split()[0].lower().strip('"“(') for f in todas[i:i + 3] if f.split()]
        if len(w) == 3 and len(set(w)) == 1 and w[0] not in {'-', '*'}:
            out.append(achado('aberturas repetidas', 'atencao', ' / '.join(f[:30] for f in todas[i:i + 3]), linha_de(t, t.find(todas[i]))))
            break

    # Frases curtas em série: três ou mais frases seguidas de até 8 palavras (fora lista e hashtag).
    corridas = [f for p in pars for f in frases(p)]
    seq = []
    for f in corridas + ['']:
        prosa_f = f.strip() and not re.match(r'\s*([-*•#]|\d+\.)', f)
        if prosa_f and len(f.split()) <= 8:
            seq.append(f)
            continue
        if len(seq) >= 3:
            out.append(achado('frases curtas em série', 'atencao', ' / '.join(s[:30] for s in seq[:4]), linha_de(t, t.find(seq[0]))))
            break
        seq = []

    baixo = t.lower()
    if lingua == 'en':
        for termo in b1:
            for m in re.finditer(r'(?<![\w-])' + re.escape(termo) + r'(?![\w-])', baixo):
                out.append(achado(f'acima de B1/B2: {termo}', 'atencao', t[max(0, m.start() - 25):m.end() + 25], linha_de(t, m.start())))
    else:
        for termo in ia_pt:
            for m in re.finditer(r'(?<![\w-])' + re.escape(termo) + r'(?![\w-])', baixo):
                out.append(achado(f'palavra de IA: {termo}', 'atencao', t[max(0, m.start() - 25):m.end() + 25], linha_de(t, m.start())))

    return {'lingua': lingua, 'frases': len(todas), 'achados': out}

# ---------------------------------------------------------------- lote

def lote(resultados, textos):
    """Compara os textos entre si. Um vício que passa em cada texto pode ser o molde do lote."""
    n = len(textos)
    out = []
    if n < 3:
        return out
    aberturas = Counter()
    for tx in textos:
        fs = frases(paragrafos(prosa(tx))[0]) if prosa(tx).strip() else []
        if fs:
            aberturas[' '.join(re.findall(r"[\w']+", fs[0].lower())[:2])] += 1
    for ab, c in aberturas.most_common():
        if c >= 3 and c / n >= 0.25:
            out.append({'regra': 'mesma abertura no lote', 'trecho': ab, 'quantos': c, 'de': n})
    for regra, limite in (('contraste no fim', 0.25), ('fecho de moral ("so..." / "para que...")', 0.25),
                          ('dois-pontos de revelação', 0.4), ('elogio-ponte na abertura', 0.2)):
        c = sum(any(a['regra'] == regra for a in r['achados']) for r in resultados)
        if c >= 3 and c / n >= limite:
            out.append({'regra': f'{regra} em boa parte do lote', 'trecho': f'{c} de {n} textos (limite {int(limite * 100)}%)',
                        'quantos': c, 'de': n})
    return out

# ---------------------------------------------------------------- saída

def imprimir(nome, r):
    print(f'== {nome} ({r["lingua"]}, {r["frases"]} frases)')
    if not r['achados']:
        print('   nada a apontar')
    for a in sorted(r['achados'], key=lambda a: ('duro', 'forte', 'atencao').index(a['nivel'])):
        print(f'   [{a["nivel"]}] {a["regra"]} (linha {a["linha"]}): {a["trecho"]}')


def testar():
    casos = json.loads((SKILL / 'tests' / 'casos.json').read_text(encoding='utf-8'))
    b1, ia_pt = listas()
    falhas = 0
    for c in casos:
        r = checar(c['texto'], c.get('lingua'), c.get('sem_hashtag', False), b1, ia_pt)
        regras = {a['regra'] for a in r['achados']}
        faltou = [e for e in c.get('espera', []) if not any(x.startswith(e) for x in regras)]
        sobrou = [x for x in regras if any(x.startswith(p) for p in c.get('nao_espera', []))]
        ok = not faltou and not sobrou
        falhas += not ok
        print(('ok   ' if ok else 'FALHA'), c['nome'], ('' if ok else f'faltou={faltou} sobrou={sobrou}'))
    print(f'{len(casos) - falhas}/{len(casos)} casos ok')
    return 1 if falhas else 0


def main(argv):
    if '--testar' in argv:
        return testar()
    as_json = '--json' in argv
    sem_hashtag = '--sem-hashtag' in argv
    lingua = argv[argv.index('--lingua') + 1] if '--lingua' in argv else None
    campo = argv[argv.index('--campo') + 1] if '--campo' in argv else None
    pula = {v for i, a in enumerate(argv) if a in ('--lingua', '--campo', '--lote') for v in argv[i + 1:i + 2]}
    b1, ia_pt = listas()

    textos, nomes = [], []
    if '--lote' in argv:
        dados = json.loads(Path(argv[argv.index('--lote') + 1]).read_text(encoding='utf-8'))
        for i, d in enumerate(dados):
            tx = d.get(campo) if isinstance(d, dict) else d
            if tx:
                textos.append(tx)
                nomes.append(str(d.get('id', i)) if isinstance(d, dict) else str(i))
    else:
        for a in argv:
            if a.startswith('--') or a in pula:
                continue
            textos.append(sys.stdin.read() if a == '-' else Path(a).read_text(encoding='utf-8'))
            nomes.append(a)
    if not textos:
        print(__doc__)
        return 2

    rs = [checar(tx, lingua, sem_hashtag, b1, ia_pt) for tx in textos]
    lt = lote(rs, textos)
    if as_json:
        print(json.dumps({'textos': [dict(nome=n, **r) for n, r in zip(nomes, rs)], 'lote': lt}, ensure_ascii=False, indent=1))
    else:
        for n, r in zip(nomes, rs):
            imprimir(n, r)
        if lt:
            print('== lote')
            for a in lt:
                print(f'   [lote] {a["regra"]}: {a["trecho"]}')
        tot = Counter(a['nivel'] for r in rs for a in r['achados'])
        print(f'-- {len(textos)} texto(s): duro {tot["duro"]}, forte {tot["forte"]}, atencao {tot["atencao"]}, lote {len(lt)}')
    return 1 if any(a['nivel'] in ('duro', 'forte') for r in rs for a in r['achados']) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
