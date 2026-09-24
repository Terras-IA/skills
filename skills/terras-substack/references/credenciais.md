# Credenciais: como obter e renovar o cookie de sessao

A ferramenta autentica com o cookie `substack.sid` (a sessao do navegador). Nao
ha senha, token ou chave de API envolvida.

> O cookie da acesso total a conta. Ele fica em
> `~/.config/terras-substack/config.json` com permissao `600`. Nunca coloque em
> repositorio e evite colar no chat (o transcript fica registrado).

## Caminho que funciona nesta maquina: navegador embutido do ZCode

O navegador embutido do ZCode guarda a sessao em texto claro na particao
`zcode-embedded-browser`. Basta estar logado na aba dele:

```bash
python3 ~/.zcode/skills/terras-substack/scripts/chrome_cookie.py substack.com \
  --profile ~/.config/ZCode --save-config --user-id <SEU_USER_ID>
```

Isso grava `substack.sid` e `substack.lli` em
`~/.config/terras-substack/config.json` (mode 600) e nao imprime o valor.
Para so conferir o que existe, sem gravar nada, omita `--save-config`.

## Caminho alternativo: copiar do DevTools

1. No Chrome (ou no navegador embutido), ja logado, abra `https://substack.com`.
2. `F12` (DevTools) → **Application** → **Storage → Cookies** →
   `https://substack.com`.
3. Clique em **`substack.sid`** e copie o **Value**.
4. Rode no terminal (o valor nao aparece na tela nem no historico):

```bash
mkdir -p ~/.config/terras-substack && chmod 700 ~/.config/terras-substack
python3 - <<'PY'
import json, os, pathlib, sys
print("Cole o valor de substack.sid e pressione Enter:")
sid = sys.stdin.readline().strip()
if not sid:
    raise SystemExit("nada colado")
p = pathlib.Path.home() / ".config/terras-substack" / "config.json"
cfg = json.loads(p.read_text()) if p.exists() else {}
cfg.setdefault("publication", "https://SEU-SUBDOMINIO.substack.com")
cfg.setdefault("user_id", 0)
cfg.setdefault("cookies", {})["substack.sid"] = sid
p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
os.chmod(p, 0o600)
print("salvo em", p)
PY
python3 ~/.zcode/skills/terras-substack/scripts/terras_substack.py check
```

Tambem aceita variaveis de ambiente para uso pontual: `SUBSTACK_SID`,
`SUBSTACK_PUBLICATION`, `SUBSTACK_USER_ID`, `SUBSTACK_COOKIES` (`"a=1; b=2"`).

## Renovacao

O cookie expira. Sintoma: `HTTP 403 Not authorized`. Repita o caminho que usou
(uma linha, no caso do navegador embutido). Enquanto a sessao do navegador
estiver viva, o valor novo e o mesmo; se voce deslogar no navegador, o cookie
morre.

## Chrome do sistema: por que a leitura automatica falha

`chrome_cookie.py` tambem aceita apontar para o Chrome
(`--profile ~/.config/google-chrome`), mas **nesta maquina isso nao funciona**:
o Chrome 153 guarda a chave mestra de criptografia no portal XDG
(`org.freedesktop.portal.Secret`) e o chaveiro do usuario nao esta acessivel a
um processo sem interface grafica. O script continua util em perfis antigos ou
com keyring destravado, e serve de diagnostico (ele diz exatamente o que
encontrou). O caminho confiavel aqui e o navegador embutido ou o DevTools.

Use `--profile-name Default` quando quiser limitar a leitura a uma base
especifica em vez de varrer o perfil inteiro.

## Rota sem cookie nenhum

Se preferir nao exportar cookie algum, faca tudo pelo navegador com a sessao da
propria aba (ver `rota-navegador.md`). Nesse caso nada e salvo em disco.
