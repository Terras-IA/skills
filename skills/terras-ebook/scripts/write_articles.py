"""
Parte 3: transforma cada transcrição num artigo, chamando a API da Anthropic.

ATENÇÃO AO CUSTO: esta etapa usa a SUA chave `ANTHROPIC_API_KEY` e é cobrada por
uso — não tem relação com a assinatura do ZCode. Se você está numa sessão do
ZCode, a rota B do SKILL.md não precisa disto: a própria sessão escreve os
artigos e você só usa o `export_epub.py` no fim.

Ajustes por variável de ambiente:
  TERRAS_EBOOK_IDIOMA  idioma do artigo (padrão: pt-BR; use `en` para inglês)
  TERRAS_EBOOK_MODELO  modelo da Anthropic (padrão: claude-sonnet-4-20250514)

Adaptado de zarazhangrui/youtube-to-ebook (MIT). Ver CREDITS.md.
"""

import argparse
import json
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
IDIOMA = os.getenv("TERRAS_EBOOK_IDIOMA", "pt-BR")
MODELO = os.getenv("TERRAS_EBOOK_MODELO", "claude-sonnet-4-20250514")

PROMPT_PT = """Você é um jornalista de revista. Transforme esta transcrição de vídeo do \
YouTube num artigo bem escrito e envolvente.

TÍTULO DO VÍDEO: {titulo}
CANAL: {canal}
URL: {url}

DESCRIÇÃO DO VÍDEO:
{descricao}

TRANSCRIÇÃO:
{transcricao}

---

Diretrizes:
- Use o título e a descrição para corrigir erros de transcrição, sobretudo nomes de pessoas, empresas e termos técnicos — a descrição costuma trazer a grafia correta.
- Comece com uma manchete envolvente, diferente do título do vídeo.
- O leitor é curioso e inteligente, mas não é especialista no assunto. Onde aparecer jargão ou referência obscura, explique.
- Muito legível e bem escrito. Traga os insights principais, sobretudo visões contrárias, anedotas memoráveis e dados surpreendentes. Preserve as citações-chave, limpando muletas e erros de transcrição.
- Sem comprimento fixo: depende do material e da densidade de ideias. Faça um texto longo que se sustente.
- NÃO escreva "neste vídeo" e não se refira ao vídeo em momento algum: escreva um artigo autônomo, que substitui o vídeo em vez de acompanhá-lo.
- Devolva apenas o artigo em markdown, começando por um título de nível 1 (`# `).

Idioma do artigo: português do Brasil."""

PROMPT_EN = """You are a skilled magazine writer. Transform this YouTube video transcript into a well-written, engaging article.

VIDEO TITLE: {titulo}
CHANNEL: {canal}
VIDEO URL: {url}

VIDEO DESCRIPTION:
{descricao}

TRANSCRIPT:
{transcricao}

---

Guidelines:
- Use the video title and description to correct any transcription errors, especially names of people, companies, or technical terms.
- Start with an engaging headline (different from the video title).
- The audience is a curious individual who is generally smart but not a specialist. Explain jargon and obscure references.
- Capture the key insights, especially contrarian viewpoints, memorable anecdotes, and surprising insights. Preserve key quotes.
- No fixed length requirement; make your own judgment. This should be a satisfying long-read.
- Do NOT include phrases like "In this video" — write it as a standalone article that replaces, not complements, the video.
- Return only the article in markdown, starting with a level-1 heading (`# `)."""


def montar_prompt(video):
    modelo = PROMPT_EN if IDIOMA.lower().startswith("en") else PROMPT_PT
    return modelo.format(
        titulo=video["title"],
        canal=video.get("channel", ""),
        url=video.get("url", ""),
        descricao=(video.get("description") or "")[:4000],
        transcricao=video["transcript"],
    )


def write_article(video):
    """Transforma a transcrição de um vídeo num artigo. Devolve o markdown ou None."""
    if not ANTHROPIC_API_KEY:
        raise SystemExit(
            "ANTHROPIC_API_KEY não configurada. Ou preencha a chave no .env, ou use a "
            "rota B do SKILL.md (a sessão escreve os artigos, sem chave)."
        )

    cliente = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        mensagem = cliente.messages.create(
            model=MODELO,
            max_tokens=8000,
            messages=[{"role": "user", "content": montar_prompt(video)}],
        )
        return mensagem.content[0].text

    except Exception as erro:
        print(f"  ⚠ erro ao gerar o artigo: {erro}")
        print(f"     (se for modelo inválido, defina TERRAS_EBOOK_MODELO)")
        return None


def write_articles_for_videos(videos):
    """Gera um artigo por vídeo com transcrição. Devolve a lista de artigos."""
    print("\nEscrevendo os artigos...\n")
    print("=" * 60)

    artigos = []

    for video in videos:
        print(f"Escrevendo: {video['title'][:60]}...")
        artigo = write_article(video)

        if artigo:
            artigos.append({
                "title": video["title"],
                "channel": video.get("channel", ""),
                "url": video.get("url", ""),
                "article": artigo,
            })
            print("  ✓ artigo gerado\n")
        else:
            print("  ✗ artigo não gerado\n")

    print("=" * 60)
    print(f"{len(artigos)} artigo(s) gerado(s)")
    return artigos


def main(videos, saida_json=None):
    """Etapa encadeável: recebe vídeos com transcrição, devolve a lista de artigos."""
    artigos = write_articles_for_videos(videos)

    if saida_json:
        with open(saida_json, "w", encoding="utf-8") as arquivo:
            json.dump(artigos, arquivo, ensure_ascii=False, indent=2)
        print(f"Gravado em: {saida_json}")

    return artigos


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Escreve artigos a partir das transcrições.")
    parser.add_argument("--entrada", required=True, help="JSON gerado por get_transcripts.py")
    parser.add_argument("--saida", help="grava o resultado neste JSON")
    args = parser.parse_args()

    with open(args.entrada, encoding="utf-8") as arquivo:
        videos_com_transcricao = json.load(arquivo)

    main(videos_com_transcricao, saida_json=args.saida)
