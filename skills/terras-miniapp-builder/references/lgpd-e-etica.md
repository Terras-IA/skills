# LGPD e ética — o que decidir antes de escrever código

Duas coisas diferentes moram aqui: **lei** (LGPD e correlatas) e **limite ético**
(o que o app não pode afirmar). As duas se resolvem no desenho, não na política.

A regra prática: **quanto menos dado sai do aparelho, menos obrigação você tem.**
Arquitetura local-first não é só economia de backend — é a forma mais barata de
estar em conformidade.

## Arquitetura de dados — decida e registre

| Desenho | O que você assume |
|---|---|
| **Local-first** (padrão) — IndexedDB no aparelho, sem backend | Nenhum dado pessoal sob sua guarda. Sem cadastro, sem transmissão. A política de privacidade fica curta e verdadeira. |
| Nuvem com conta | Você é controlador: base legal, aviso, retenção, exclusão, portabilidade, segurança, resposta a incidente. |
| Nuvem sem conta (código de sincronização) | Continua sendo tratamento. "Sem login" não é "sem LGPD". |

Escreva a decisão no `README.md` **com o motivo**. Quando alguém propuser sincronizar
depois, o motivo registrado é o que faz a conversa recomeçar do lugar certo.

## Dado de criança e adolescente

Dado de criança é **sensível** na LGPD (art. 14) e exige tratamento no melhor
interesse dela. Num app para pais, o conteúdo registrado é sobre a criança mesmo que
ela nunca toque no aparelho. Então:

- Minimize: não peça nome completo, data de nascimento exata, escola, diagnóstico.
  Apelido e idade aproximada resolvem quase tudo — e o app precisa funcionar sem isso.
- Não peça dado que não muda a experiência. Cada campo é risco sem contrapartida.
- Não exponha a criança a terceiros: sem analytics que mandem conteúdo do usuário,
  sem SDK de publicidade, sem fonte remota que receba o que foi digitado.
- Coloque na política uma frase clara de que os registros são do adulto sobre a
  criança, feitos no aparelho dele.

## Minimização, retenção e descarte

- **Minimização:** colete/guarde só o que a promessa exige.
- **Retenção:** defina por quanto tempo o dado fica e execute. Em local-first o
  aparelho é do usuário, mas o app ainda deve oferecer apagar tudo.
- **Descarte de mídia:** foto e áudio pesam e são o que mais expõe. Se o app guarda
  mídia, ofereça limpeza só dela.
- **Exportar e importar:** dado local sem exportação é dado que se perde na troca de
  aparelho — e o direito à portabilidade pede o caminho de saída. Um botão que gera
  arquivo resolve os dois.
- **Apagar todos os dados:** explícito, com confirmação, e funcionando de verdade.

## A política de privacidade

Exigida pelas duas lojas e boa prática sempre. Use `assets/templates/PRIVACIDADE.md`.

Regras que fazem a diferença entre uma política útil e uma que não se sustenta:

- Descreva **o que o app faz de fato**. Se nada sai do aparelho, diga isso na primeira
  linha — e não copie cláusula sobre transferência internacional que não acontece.
- Nomeie o responsável (razão social, CNPJ, contato) — campos entre colchetes no
  template, preenchidos antes de publicar.
- Diga como a pessoa apaga os dados dela (no caso local-first: desinstalar ou o botão
  dentro do app) e como fala com você.
- Revise antes de publicar. Rascunho de política é pendência aberta, não entregável.

## Disclaimers por tipo de assunto

Escreva o disclaimer **antes** da copy, para a copy nascer dentro do limite.

| Assunto | O que o app não pode afirmar |
|---|---|
| Saúde, desenvolvimento, comportamento | Não diagnostica, não trata, não substitui profissional. Ofereça caminho de ajuda (no Brasil, CVV 188, em caso de risco). |
| Dinheiro, investimento | Não é recomendação de investimento; simulações dependem de premissas que a pessoa informa. |
| Jurídico, contábil | Não é consultoria; confira com profissional. |
| Educação, parentalidade | Apoio educativo e reflexivo, sem prometer resultado no outro. |

Regras de escrita que sustentam o disclaimer:

- Fale do que a pessoa **faz**, não do que vai acontecer com ela ou com o filho.
  "Você registra e enxerga o padrão" — ok. "Seu filho vai melhorar" — não.
- Não use linguagem clínica sem profissional envolvido: hipótese, não diagnóstico.
- Onde a pessoa pode se machucar de verdade, o caminho de ajuda aparece no contexto,
  não escondido no "Sobre".

## Público adulto, e o que isso implica na loja

O app é do adulto responsável. Declarar "crianças" no Google Play aciona a
**Families Policy** (exigências bem maiores) e, na Apple, a categoria **Kids**
restringe o app. Declare público adulto, e mantenha a copy e os screenshots coerentes
com isso — a própria loja revisa essa coerência.

## Checklist antes de publicar em produção

- [ ] Arquitetura de dados decidida e escrita no README
- [ ] Se local-first: a política afirma isso e é verdade (nada de rede em runtime)
- [ ] Nenhum dado de contato, diagnóstico ou identificação direta sendo pedido
- [ ] Exportar/importar e apagar-tudo funcionando
- [ ] Disclaimer visível na primeira tela quando o assunto for sensível
- [ ] Caminho de ajuda presente quando houver risco
- [ ] Política de privacidade preenchida (sem colchetes) e publicada em URL
- [ ] Classificação de público adulto definida
- [ ] Quem valida o conteúdo aprovou (e o crédito está no app)
