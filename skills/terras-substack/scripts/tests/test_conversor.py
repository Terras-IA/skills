#!/usr/bin/env python3
"""Testes offline do conversor Markdown <-> ProseMirror.

Roda com: cd scripts && python3 -m unittest discover -s tests -t .
Nao toca a rede.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from terras_substack import (  # noqa: E402
    doc_to_markdown,
    markdown_to_doc,
    parse_inline,
    split_frontmatter,
)


def types(doc: dict) -> list[str]:
    return [node["type"] for node in doc["content"]]


class TestInline(unittest.TestCase):
    def test_negrito_e_italico(self):
        nodes = parse_inline("texto **forte** e *enfase*")
        self.assertEqual(nodes[1]["text"], "forte")
        self.assertEqual(nodes[1]["marks"], [{"type": "strong"}])
        self.assertEqual(nodes[3]["marks"], [{"type": "em"}])

    def test_negrito_italico_junto(self):
        nodes = parse_inline("***ambos***")
        self.assertEqual(nodes[0]["marks"], [{"type": "strong"}, {"type": "em"}])

    def test_codigo_inline_nao_interpreta_formatacao(self):
        nodes = parse_inline("`**nao e negrito**`")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]["text"], "**nao e negrito**")
        self.assertEqual(nodes[0]["marks"], [{"type": "code"}])

    def test_riscado(self):
        nodes = parse_inline("~~cortado~~")
        self.assertEqual(nodes[0]["marks"], [{"type": "strikethrough"}])

    def test_link(self):
        nodes = parse_inline("veja [o post](https://exemplo.com/a)")
        link = nodes[1]
        self.assertEqual(link["text"], "o post")
        self.assertEqual(link["marks"], [{"type": "link", "attrs": {"href": "https://exemplo.com/a"}}])

    def test_link_com_negrito_interno(self):
        nodes = parse_inline("[**negrito**](https://exemplo.com)")
        self.assertEqual(nodes[0]["marks"], [{"type": "link", "attrs": {"href": "https://exemplo.com"}}, {"type": "strong"}])

    def test_snake_case_nao_vira_italico(self):
        nodes = parse_inline("nome_com_underscores aqui")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]["text"], "nome_com_underscores aqui")
        self.assertNotIn("marks", nodes[0])


class TestBlocos(unittest.TestCase):
    def test_titulos(self):
        doc = markdown_to_doc("# Um\n\n## Dois\n\ntexto")
        self.assertEqual(types(doc), ["heading", "heading", "paragraph"])
        self.assertEqual(doc["content"][0]["attrs"]["level"], 1)
        self.assertEqual(doc["content"][1]["attrs"]["level"], 2)

    def test_paragrafo_com_linhas_soltas_junta_com_espaco(self):
        doc = markdown_to_doc("linha um\nlinha dois")
        self.assertEqual(types(doc), ["paragraph"])
        self.assertEqual(doc["content"][0]["content"][0]["text"], "linha um linha dois")

    def test_paragrafos_separados_por_linha_vazia(self):
        doc = markdown_to_doc("um\n\ndois")
        self.assertEqual(types(doc), ["paragraph", "paragraph"])

    def test_lista_simples(self):
        doc = markdown_to_doc("- um\n- dois")
        self.assertEqual(types(doc), ["bullet_list"])
        self.assertEqual(len(doc["content"][0]["content"]), 2)

    def test_lista_ordenada(self):
        doc = markdown_to_doc("1. primeiro\n2. segundo")
        self.assertEqual(types(doc), ["ordered_list"])
        self.assertEqual(len(doc["content"][0]["content"]), 2)

    def test_lista_aninhada(self):
        doc = markdown_to_doc("- pai\n  - filho\n- outro pai")
        lista = doc["content"][0]
        self.assertEqual(len(lista["content"]), 2)
        filho = lista["content"][0]["content"][1]
        self.assertEqual(filho["type"], "bullet_list")
        self.assertEqual(filho["content"][0]["content"][0]["content"][0]["text"], "filho")

    def test_citacao(self):
        doc = markdown_to_doc("> citado aqui")
        self.assertEqual(types(doc), ["blockquote"])
        self.assertEqual(doc["content"][0]["content"][0]["type"], "paragraph")

    def test_bloco_de_codigo_com_linguagem(self):
        doc = markdown_to_doc("```python\nprint('oi')\n```")
        node = doc["content"][0]
        self.assertEqual(node["type"], "codeBlock")
        self.assertEqual(node["attrs"]["language"], "python")
        self.assertEqual(node["content"][0]["text"], "print('oi')")

    def test_regua_horizontal(self):
        doc = markdown_to_doc("antes\n\n---\n\ndepois")
        self.assertEqual(types(doc), ["paragraph", "horizontal_rule", "paragraph"])

    def test_imagem_com_legenda(self):
        doc = markdown_to_doc("![alt da imagem](https://img.exemplo/a.png)\n^ legenda da foto")
        node = doc["content"][0]
        self.assertEqual(node["type"], "captionedImage")
        self.assertEqual(node["content"][0]["type"], "image2")
        self.assertEqual(node["content"][0]["attrs"]["src"], "https://img.exemplo/a.png")
        self.assertEqual(node["content"][0]["attrs"]["alt"], "alt da imagem")
        self.assertEqual(node["content"][1]["type"], "caption")
        self.assertEqual(node["content"][1]["content"][0]["text"], "legenda da foto")

    def test_imagem_com_diretiva_de_legenda(self):
        doc = markdown_to_doc("![foto](https://img.exemplo/b.png)\n\n::: caption Legenda via diretiva")
        node = doc["content"][0]
        self.assertEqual(node["content"][1]["type"], "caption")
        self.assertEqual(node["content"][1]["content"][0]["text"], "Legenda via diretiva")

    def test_diretiva_paywall(self):
        doc = markdown_to_doc("texto livre\n\n::: paywall\n\ntexto pago")
        self.assertEqual(types(doc), ["paragraph", "paywall", "paragraph"])

    def test_diretiva_subscribe(self):
        doc = markdown_to_doc("::: subscribe Assine para receber")
        node = doc["content"][0]
        self.assertEqual(node["type"], "subscribeWidget")
        self.assertEqual(node["attrs"]["text"], "Assine")
        self.assertEqual(node["content"][0]["type"], "ctaCaption")
        self.assertEqual(node["content"][0]["content"][0]["text"], "Assine para receber")

    def test_diretiva_subscribe_sem_texto_usa_padrao(self):
        doc = markdown_to_doc("::: subscribe")
        node = doc["content"][0]
        self.assertEqual(node["type"], "subscribeWidget")
        self.assertTrue(node["content"][0]["content"][0]["text"])

    def test_diretiva_button(self):
        doc = markdown_to_doc("::: button Assinar agora | https://exemplo.com/assinar")
        node = doc["content"][0]
        self.assertEqual(node["type"], "button")
        self.assertEqual(node["attrs"]["text"], "Assinar agora")
        self.assertEqual(node["attrs"]["href"], "https://exemplo.com/assinar")

    def test_diretiva_pullquote(self):
        doc = markdown_to_doc("::: pullquote\numa frase de efeito\n:::")
        node = doc["content"][0]
        self.assertEqual(node["type"], "pullquote")
        self.assertEqual(node["content"][0]["content"][0]["text"], "uma frase de efeito")

    def test_diretiva_desconhecida_falha(self):
        with self.assertRaises(Exception):
            markdown_to_doc("::: inventada")


class TestRoundTrip(unittest.TestCase):
    def test_doc_para_markdown(self):
        doc = markdown_to_doc(
            "# Titulo\n\nparagrafo com **negrito**\n\n- item\n- outro\n\n> citacao\n\n```python\nx = 1\n```\n\n---"
        )
        markdown = doc_to_markdown(doc)
        self.assertIn("# Titulo", markdown)
        self.assertIn("**negrito**", markdown)
        self.assertIn("- item", markdown)
        self.assertIn("> citacao", markdown)
        self.assertIn("```python", markdown)
        self.assertIn("---", markdown)

    def test_ida_e_volta_preserva_estrutura(self):
        original = "# T\n\ntexto\n\n- a\n- b"
        primeiro = markdown_to_doc(original)
        segundo = markdown_to_doc(doc_to_markdown(primeiro))
        self.assertEqual(types(primeiro), types(segundo))

    def test_no_desconhecido_vira_comentario(self):
        markdown = doc_to_markdown({"type": "doc", "content": [{"type": "tweet", "attrs": {"url": "x"}}]})
        self.assertIn("<!--", markdown)
        self.assertIn("tweet", markdown)

    def test_widget_de_assinatura_faz_ida_e_volta(self):
        doc = markdown_to_doc("::: subscribe Assine para receber")
        markdown = doc_to_markdown(doc)
        self.assertEqual(markdown, "::: subscribe Assine para receber")
        self.assertNotIn("nao convertido", markdown)

    def test_legenda_de_imagem_faz_ida_e_volta(self):
        doc = markdown_to_doc("![foto](https://img.exemplo/f.png)\n^ Legenda da foto")
        markdown = doc_to_markdown(doc)
        self.assertIn("^ Legenda da foto", markdown)
        self.assertNotIn("nao convertido", markdown)


class TestFrontmatter(unittest.TestCase):
    def test_extrai_campos(self):
        meta, body = split_frontmatter("---\ntitle: Meu post\nsubtitle: Uma linha\naudience: only_paid\ntags: [ia, carreira]\n---\n\ncorpo")
        self.assertEqual(meta["title"], "Meu post")
        self.assertEqual(meta["subtitle"], "Uma linha")
        self.assertEqual(meta["audience"], "only_paid")
        self.assertEqual(meta["tags"], ["ia", "carreira"])
        self.assertEqual(body.strip(), "corpo")

    def test_sem_frontmatter(self):
        meta, body = split_frontmatter("# Titulo\n\ntexto")
        self.assertEqual(meta, {})
        self.assertIn("# Titulo", body)

    def test_tags_com_virgula_sem_colchetes(self):
        meta, _ = split_frontmatter("---\ntags: ia, carreira, produto\n---\ncorpo")
        self.assertEqual(meta["tags"], ["ia", "carreira", "produto"])


class TestExemploReal(unittest.TestCase):
    """Post com o formato que a skill espera receber."""

    POST = """---
title: O que aprendi automatizando minha newsletter
subtitle: Tres licoes praticas
audience: everyone
tags: [automacao, escrita]
---

Abertura com **gancho forte** e um [link](https://exemplo.com).

## O problema

- publicar era manual
- revisar era lento

> Automatizar nao e publicar mais, e publicar melhor.

![grafico de tempo](https://img.exemplo/grafico.png)
^ Tempo gasto por post

::: paywall

## A parte pratica

1. escrever em markdown
2. conferir o rascunho
3. publicar sem disparar e-mail

```bash
python3 terras_substack.py create-draft post.md
```

::: subscribe Assine para receber os proximos
"""

    def test_converte_post_completo(self):
        meta, body = split_frontmatter(self.POST)
        doc = markdown_to_doc(body)
        self.assertEqual(meta["title"], "O que aprendi automatizando minha newsletter")
        self.assertEqual(
            types(doc),
            [
                "paragraph",
                "heading",
                "bullet_list",
                "blockquote",
                "captionedImage",
                "paywall",
                "heading",
                "ordered_list",
                "codeBlock",
                "subscribeWidget",
            ],
        )

    def test_payload_serializa_como_json_string(self):
        _, body = split_frontmatter(self.POST)
        doc = markdown_to_doc(body)
        serializado = json.dumps(doc, ensure_ascii=False)
        self.assertIsInstance(serializado, str)
        self.assertEqual(json.loads(serializado)["type"], "doc")


if __name__ == "__main__":
    unittest.main(verbosity=2)
