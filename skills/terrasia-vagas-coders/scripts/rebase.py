#!/usr/bin/env python3
"""Varredura do Rebase Jobs (rebasedev.com.br/vagas) com os filtros do perfil.

Somente leitura. O script lista e pontua; o agente julga com references/perfil.md.

  python3 rebase.py                # vagas novas (não vistas), ranqueadas, em JSON
  python3 rebase.py --todas        # ignora o estado de vistas
  python3 rebase.py --marcar SLUG...   # marca como vistas (depois de entregar a triagem)
  python3 rebase.py --anuncio SLUG     # anúncio completo em texto

Token: REBASE_JOBS_TOKEN ou o arquivo ~/.config/terrasia-vagas-coders/rebase-token (uma linha,
com ou sem o prefixo "Bearer "). Nunca imprime o token.
"""
import html, json, os, re, sys, time, urllib.parse, urllib.request

API = 'https://rebasedev.com.br/api/v1/'
CONFIG = os.path.expanduser('~/.config/terrasia-vagas-coders')
ESTADO = os.path.join(CONFIG, 'rebase-vistas.json')
ARQUIVO_TOKEN = os.path.join(CONFIG, 'rebase-token')

NIVEIS = ['senior', 'staff', 'lideranca']
SKILLS = ['csharp', 'devops', 'kubernetes', 'azure', 'microservices', 'system-design', 'sre', 'php']
TITULOS = ['architect', 'platform', 'devops', 'backend', 'infrastructure', 'tech lead']
TEXTOS = ['laravel', '.net']  # sem tag própria no catálogo: busca no anúncio

PESO = {'csharp': 4, 'php': 4, 'devops': 2, 'kubernetes': 2, 'azure': 2, 'microservices': 2,
        'system-design': 2, 'docker': 1, 'ci-cd': 1, 'postgres': 1, 'sre': 1, 'terraform': 1,
        'distributed-systems': 1, 'rest-api': 1, 'llm': 1, 'python': 0.5}
BOM = r'\.net|c#|architect|devops|platform|sre|site reliab|back-?\s?end|infrastructure|cloud|tech lead|staff|principal'
RUIM = (r'front|mobile|android|ios|data (engineer|scien|analy)|analytics|machine learning|\bml\b|\bqa\b|'
        r'test engineer|designer|embedded|firmware|sales|solutions engineer|support|ai training|game|unity|salesforce')


def token():
    t = os.environ.get('REBASE_JOBS_TOKEN', '').strip()
    if not t and os.path.exists(ARQUIVO_TOKEN):
        t = open(ARQUIVO_TOKEN).read().strip()
    if not t:
        sys.exit(f'Sem token: gere em rebasedev.com.br/vagas/perfil/agentes e defina REBASE_JOBS_TOKEN '
                 f'ou grave em {ARQUIVO_TOKEN}.')
    return t if t.lower().startswith('bearer ') else 'Bearer ' + t


def get(path, **q):
    url = API + path + ('?' + urllib.parse.urlencode(q) if q else '')
    req = urllib.request.Request(url, headers={'Authorization': TOKEN, 'User-Agent': 'terrasia-vagas'})
    return json.load(urllib.request.urlopen(req, timeout=30))


def varrer():
    vagas = {}
    consultas = [dict(nivel=n, skill=s) for n in NIVEIS for s in SKILLS]
    consultas += [dict(nivel=n, q=t, titulo='true') for n in NIVEIS for t in TITULOS]
    consultas += [dict(nivel=n, q=t) for n in NIVEIS for t in TEXTOS]
    for q in consultas:
        pagina = 1
        while True:
            d = get('jobs', por_pagina=50, pagina=pagina, **q)
            for j in d['data']:
                vagas.setdefault(j['slug'], j)
            if pagina >= d['meta']['paginas']:
                break
            pagina += 1
        time.sleep(0.3)  # 60 chamadas/min por conta
    return vagas


def pontuar(j):
    t = j['title'].lower()
    s = sum(PESO.get(k, 0) for k in j['skills'])
    s += 4 if re.search(BOM, t) else 0
    s -= 8 if re.search(RUIM, t) else 0
    s -= 0 if j['hires_in_brazil'] == 'yes' else 2
    return s


def estado():
    try:
        return json.load(open(ESTADO))
    except FileNotFoundError:
        return {}


def main(a):
    global TOKEN
    TOKEN = token()
    if a[:1] == ['--anuncio']:
        d = get('jobs/' + a[1])['data']
        print(re.sub(r'\n\s*\n+', '\n\n', html.unescape(re.sub(r'<[^>]+>', '\n', d['description'] or ''))))
        return
    if a[:1] == ['--marcar']:
        e = estado()
        e.update({s: time.strftime('%Y-%m-%d') for s in a[1:]})
        os.makedirs(os.path.dirname(ESTADO), exist_ok=True)
        json.dump(e, open(ESTADO, 'w'), indent=0)
        print(f'{len(a) - 1} marcadas; {len(e)} vistas no total')
        return
    vistas = {} if '--todas' in a else estado()
    saida = []
    for j in varrer().values():
        if j['slug'] in vistas or j.get('oculta'):
            continue
        sal = f"{j['salary_min']}-{j['salary_max']} {j['salary_currency']}/{j['salary_interval']}" if j['salary_min'] else None
        saida.append(dict(score=pontuar(j), slug=j['slug'], titulo=j['title'], empresa=j['company']['name'],
                          nivel=j['seniority'], local=j['location'], brasil=j['hires_in_brazil'],
                          skills=j['skills'], salario=sal, publicada=j['published_at'][:10],
                          url=j['url'], aplicar=j['apply_url']))
    saida.sort(key=lambda x: -x['score'])
    print(json.dumps(saida, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main(sys.argv[1:])
