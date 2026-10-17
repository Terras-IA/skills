#!/usr/bin/env python3
"""Testes offline do feed_indice.py (análise do feed em lote).

Roda com: cd scripts && python3 -m unittest discover -s tests -t .
Não toca a rede. O que trava: export com formato errado aceito, post repetido ou
repost contado duas vezes rumo ao mínimo, e índice declarando mínimo que não atingiu.
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import feed_indice as fi  # noqa: E402


def post(n, **extra):
    p = {"url": f"https://www.linkedin.com/feed/update/urn:li:activity:{n}/", "autor": f"Autor {n}",
         "quando": "2 h", "texto": f"texto do post {n}", "links": []}
    p.update(extra)
    return p


class TestCarregar(unittest.TestCase):
    def test_aceita_array_e_objeto(self):
        self.assertEqual(len(fi.carregar(json.dumps([post(1)]))), 1)
        self.assertEqual(len(fi.carregar(json.dumps({"posts": [post(1), post(2)]}))), 2)

    def test_recusa_com_erro_nomeado(self):
        with self.assertRaisesRegex(fi.EntradaInvalida, "JSON inválido"):
            fi.carregar("não é json")
        with self.assertRaisesRegex(fi.EntradaInvalida, "array de posts"):
            fi.carregar(json.dumps({"outra": 1}))
        with self.assertRaisesRegex(fi.EntradaInvalida, "post 0 sem url"):
            fi.carregar(json.dumps([{"autor": "x"}]))


class TestNormalizar(unittest.TestCase):
    def test_urn_texto_e_links(self):
        p = fi.normalizar(post(7, texto="  linha 1\n\n\n\nlinha 2   ", links=[
            "https://github.com/a/b?utm_source=li", "https://github.com/a/b",
            "https://www.linkedin.com/in/alguem", "https://lnkd.in/abc", "javascript:void(0)"]))
        self.assertEqual(p["urn"], "urn:li:activity:7")
        self.assertEqual(p["texto"], "linha 1\n\nlinha 2")
        self.assertEqual(p["links"], ["https://github.com/a/b", "https://lnkd.in/abc"])

    def test_so_urn_monta_url(self):
        p = fi.normalizar({"urn": "urn:li:ugcPost:9", "texto": "x"})
        self.assertEqual(p["url"], "https://www.linkedin.com/feed/update/urn:li:ugcPost:9/")

    def test_tipo_link(self):
        self.assertEqual(fi.tipo_link("https://github.com/a/b"), "github")
        self.assertEqual(fi.tipo_link("https://youtu.be/x"), "video")
        self.assertEqual(fi.tipo_link("https://lnkd.in/x"), "encurtado")
        self.assertEqual(fi.tipo_link("https://arxiv.org/abs/1"), "paper")
        self.assertEqual(fi.tipo_link("https://blog.exemplo.com/p"), "artigo")


class TestDeduplicarEResumo(unittest.TestCase):
    def test_remove_mesma_urn_e_repost(self):
        a, a2 = fi.normalizar(post(1)), fi.normalizar(post(1))
        repost = fi.normalizar(post(2, autor="Autor 1", texto="texto do post 1"))
        posts, removidos = fi.deduplicar([a, a2, repost, fi.normalizar(post(3))])
        self.assertEqual([p["urn"] for p in posts], ["urn:li:activity:1", "urn:li:activity:3"])
        self.assertEqual(removidos, 2)

    def test_minimo_conta_so_unicos(self):
        cem = [fi.normalizar(post(i)) for i in range(100)]
        self.assertTrue(fi.resumir(cem, 100)["minimoAtingido"])
        self.assertFalse(fi.resumir(cem[1:], 100)["minimoAtingido"])

    def test_indice_honesto_e_escapado(self):
        md = fi.indice_bruto([fi.normalizar(post(1, texto="a | b"))], "f.json", "2026-10-17", 100, 0)
        self.assertIn("1 posts únicos", md)
        self.assertIn("abaixo do mínimo de 100", md)
        self.assertIn("a \\| b", md)


class TestMain(unittest.TestCase):
    def rodar(self, conteudo, minimo=100):
        d = Path(tempfile.mkdtemp())
        (d / "feed.json").write_text(conteudo, encoding="utf-8")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            codigo = fi.main([str(d / "feed.json"), "--saida", str(d / "out"), "--minimo", str(minimo)])
        return codigo, d / "out"

    def test_codigos_de_saida(self):
        feed = [post(i, links=[f"https://github.com/x/r{i % 6}?utm_source=li"] if i % 4 == 0 else []) for i in range(110)]
        feed += feed[:10]
        codigo, out = self.rodar(json.dumps(feed))
        self.assertEqual(codigo, 0)
        self.assertEqual(len(json.loads((out / "posts.json").read_text(encoding="utf-8"))), 110)
        self.assertEqual(len((out / "links.txt").read_text(encoding="utf-8").split()), 3)
        codigo, out = self.rodar(json.dumps(feed[:50]))
        self.assertEqual(codigo, 1)
        self.assertIn("abaixo do mínimo", (out / "INDICE-BRUTO.md").read_text(encoding="utf-8"))
        codigo, out = self.rodar(json.dumps({"x": 1}))
        self.assertEqual(codigo, 2)
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
