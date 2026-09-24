#!/usr/bin/env python3
"""Testes offline do modo --dry-run do cliente.

Roda com: cd scripts && python3 -m unittest discover -s tests -t .
Nao toca a rede: em dry-run o cliente nao chama `requests`.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from terras_substack import Client  # noqa: E402


class TestSetTagsDryRun(unittest.TestCase):
    def setUp(self):
        self.client = Client({"publication": "https://exemplo.substack.com"}, dry_run=True)

    def test_set_tags_nao_quebra_em_dry_run(self):
        resultado = self.client.set_tags(42, ["ia", "gestao"])
        self.assertEqual(len(resultado), 2)
        for chamada in resultado:
            self.assertTrue(chamada["dry_run"])
            self.assertEqual(chamada["method"], "POST")
            self.assertIn("/post/42/tag/", chamada["url"])

    def test_url_da_simulacao_nomeia_a_tag(self):
        resultado = self.client.set_tags(42, ["ia"])
        self.assertIn("ia", resultado[0]["url"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
