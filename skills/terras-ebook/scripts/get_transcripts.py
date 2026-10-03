"""
Parte 2: extrai as transcrições dos vídeos.

Duas fontes, nesta ordem por padrão:

1. `youtube-transcript-api` — grátis, sem chave, direto do YouTube. Funciona
   para a maioria dos vídeos, mas o YouTube bloqueia com frequência (e bloqueia
   quase sempre em servidor/nuvem).
2. Supadata (https://supadata.ai) — API paga, com cota gratuita. Não é
   bloqueada, porque a infraestrutura é deles. Exige `SUPADATA_API_KEY`.

Escolha com `--fonte auto|youtube|supadata` (padrão `auto`).

Adaptado de zarazhangrui/youtube-to-ebook (MIT). Ver CREDITS.md.
"""

import argparse
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

SUPADATA_API_KEY = os.getenv("SUPADATA_API_KEY")
SUPADATA_TRANSCRIPT_URL = "https://api.supadata.ai/v1/transcript"


def transcript_do_youtube(video_id):
    """
    Caminho grátis: baixa a legenda direto do YouTube.
    Devolve o texto ou None (vídeo sem legenda, ou bloqueio do YouTube).
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return None

    try:
        # A API de classe (`get_transcript`) foi removida; a instância é o caminho atual.
        api = YouTubeTranscriptApi()
        partes = api.fetch(video_id)
        texto = " ".join(p.text for p in partes)
        return texto.strip() or None
    except Exception as erro:
        print(f"  ⚠ youtube-transcript-api falhou ({type(erro).__name__})")
        return None


def transcript_da_supadata(video_id):
    """
    Caminho pago: a Supadata busca a transcrição na infraestrutura dela.
    Devolve o texto ou None.
    """
    if not SUPADATA_API_KEY or SUPADATA_API_KEY.startswith("your_"):
        print("  ⚠ SUPADATA_API_KEY não configurada no .env")
        return None

    try:
        resposta = requests.get(
            SUPADATA_TRANSCRIPT_URL,
            params={"url": f"https://www.youtube.com/watch?v={video_id}", "text": "true"},
            headers={"x-api-key": SUPADATA_API_KEY},
            timeout=60,
        )

        if resposta.status_code == 200:
            dados = resposta.json()
            if dados.get("content"):
                return dados["content"].strip()
            if dados.get("transcript"):
                return " ".join(seg.get("text", "") for seg in dados["transcript"]).strip()
            print("  ⚠ resposta sem conteúdo")
            return None

        if resposta.status_code == 404:
            print("  ⚠ vídeo sem transcrição disponível")
        elif resposta.status_code == 401:
            print("  ⚠ SUPADATA_API_KEY inválida")
        elif resposta.status_code == 429:
            print("  ⚠ limite de uso da Supadata atingido")
        else:
            print(f"  ⚠ erro da API: {resposta.status_code} - {resposta.text[:200]}")
        return None

    except requests.exceptions.Timeout:
        print("  ⚠ tempo esgotado na Supadata")
        return None
    except Exception as erro:
        print(f"  ⚠ erro ao buscar transcrição: {erro}")
        return None


def get_transcript(video_id, fonte="auto"):
    """Tenta a(s) fonte(s) pedida(s) e devolve o texto da transcrição, ou None."""
    if fonte in ("auto", "youtube"):
        texto = transcript_do_youtube(video_id)
        if texto:
            return texto
        if fonte == "youtube":
            return None
        print("  → caindo para a Supadata")

    if fonte in ("auto", "supadata"):
        return transcript_da_supadata(video_id)

    return None


def get_transcripts_for_videos(videos, fonte="auto"):
    """
    Recebe a lista de vídeos de `get_videos.py` e acrescenta `transcript` em cada um.
    Devolve só os que têm transcrição.
    """
    print("\nExtraindo transcrições...\n")
    print("=" * 60)

    for i, video in enumerate(videos):
        print(f"Transcrevendo: {video['title'][:60]}...")

        transcricao = get_transcript(video["video_id"], fonte=fonte)

        if transcricao:
            video["transcript"] = transcricao
            print(f"  ✓ {len(transcricao.split())} palavras\n")
        else:
            video["transcript"] = None
            print("  ✗ sem transcrição\n")

        # Pausa entre requisições: o YouTube limita quem vai rápido demais.
        if i < len(videos) - 1:
            time.sleep(2)

    com_transcricao = [v for v in videos if v.get("transcript")]

    print("=" * 60)
    print(f"Transcrição obtida em {len(com_transcricao)} de {len(videos)} vídeo(s)")

    return com_transcricao


def main(videos, fonte="auto", saida_json=None):
    """Etapa encadeável: recebe a lista de vídeos, devolve a lista com transcrições."""
    resultado = get_transcripts_for_videos(videos, fonte=fonte)

    if saida_json:
        with open(saida_json, "w", encoding="utf-8") as arquivo:
            json.dump(resultado, arquivo, ensure_ascii=False, indent=2)
        print(f"Gravado em: {saida_json}")

    return resultado


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrai transcrições de uma lista de vídeos.")
    parser.add_argument("--entrada", required=True, help="JSON gerado por get_videos.py --json")
    parser.add_argument("--saida", help="grava o resultado neste JSON")
    parser.add_argument("--fonte", default="auto", choices=["auto", "youtube", "supadata"])
    args = parser.parse_args()

    with open(args.entrada, encoding="utf-8") as arquivo:
        videos = json.load(arquivo)

    main(videos, fonte=args.fonte, saida_json=args.saida)
