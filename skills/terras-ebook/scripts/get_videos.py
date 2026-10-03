"""
Parte 1: busca o vídeo mais recente (longo) de cada canal configurado.

Os canais vêm de `canais.txt`, um @handle por linha (`#` comenta). Descarta
YouTube Shorts e usa a playlist de uploads do canal, que é a única ordem
confiável — a Search API não devolve os vídeos em ordem cronológica real.

Adaptado de zarazhangrui/youtube-to-ebook (MIT). Ver CREDITS.md.
"""

import argparse
import json
import os
import sys

import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

AQUI = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_CANAIS = os.path.join(AQUI, "canais.txt")

# Usada quando `canais.txt` não existe ou está só com comentários.
CANAIS_PADRAO = [
    "@LatentSpacePod",
    "@ycombinator",
    "@a16z",
    "@RedpointAI",
    "@EveryInc",
    "@DataDrivenNYC",
    "@NoPriorsPodcast",
    "@DwarkeshPatel",
]


def carregar_canais():
    """
    Lê `canais.txt`: um @handle por linha, `#` inicia comentário.
    Cai para CANAIS_PADRAO se o arquivo não existir ou não tiver nenhum canal.
    """
    if not os.path.exists(ARQUIVO_CANAIS):
        return CANAIS_PADRAO

    canais = []
    with open(ARQUIVO_CANAIS, encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.split("#", 1)[0].strip()
            if linha:
                canais.append(linha)

    return canais or CANAIS_PADRAO


def get_channel_info(youtube, channel_handle):
    """
    Given a channel handle (@username), find its channel ID and uploads playlist ID.
    The uploads playlist contains ALL videos in exact upload order (most reliable).
    """
    # Remove @ if present for the API call
    handle = channel_handle.lstrip("@")

    # Get channel info including the contentDetails (which has the uploads playlist)
    request = youtube.channels().list(
        part="snippet,contentDetails",
        forHandle=handle
    )
    response = request.execute()

    if response.get("items"):
        channel = response["items"][0]
        return {
            "channel_id": channel["id"],
            "channel_name": channel["snippet"]["title"],
            "uploads_playlist_id": channel["contentDetails"]["relatedPlaylists"]["uploads"]
        }

    return None


def is_youtube_short(video_id):
    """
    Check if a video is a YouTube Short by testing the /shorts/ URL.
    If youtube.com/shorts/VIDEO_ID works (doesn't redirect away), it's a Short.

    Filtrar por duração não resolve: existem Shorts com mais de 60 segundos.
    """
    shorts_url = f"https://www.youtube.com/shorts/{video_id}"

    try:
        response = requests.head(shorts_url, allow_redirects=True, timeout=5)
        return "/shorts/" in response.url
    except Exception:
        # Se a checagem falhar, assume que não é Short (melhor processar do que perder).
        return False


def get_latest_video(youtube, uploads_playlist_id, channel_name):
    """
    Get the most recent LONG-FORM video from a channel's uploads playlist.
    Uses the uploads playlist (not search) for accurate chronological order.
    Skips YouTube Shorts by checking the /shorts/ URL pattern.
    """
    # Os 15 mais recentes; a playlist de uploads já vem do mais novo para o mais antigo.
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist_id,
        maxResults=15
    )
    response = request.execute()

    for item in response.get("items", []):
        video_id = item["snippet"]["resourceId"]["videoId"]

        if is_youtube_short(video_id):
            continue

        return {
            "title": item["snippet"]["title"],
            "video_id": video_id,
            "description": item["snippet"]["description"],
            "channel": channel_name,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        }

    return None


def buscar(canais=None):
    """
    Busca o último vídeo longo de cada canal e devolve a lista de vídeos.
    Não grava nada em disco — quem chama decide o que fazer com o resultado.
    """
    if not YOUTUBE_API_KEY:
        raise SystemExit(
            "YOUTUBE_API_KEY não configurada. Copie .env.example para .env e preencha "
            "(chave grátis no Google Cloud Console, APIs do YouTube Data v3)."
        )

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    canais = canais if canais is not None else carregar_canais()

    print(f"Buscando o vídeo longo mais recente de {len(canais)} canal(is)...\n")
    print("=" * 60)

    videos = []

    for canal in canais:
        print(f"Procurando: {canal}")

        info = get_channel_info(youtube, canal)

        if not info:
            print("  ✗ Canal não encontrado\n")
            continue

        print(f"  Canal: {info['channel_name']}")
        video = get_latest_video(youtube, info["uploads_playlist_id"], info["channel_name"])

        if video:
            videos.append(video)
            print(f"  ✓ Encontrado: {video['title']}")
            print(f"    {video['url']}\n")
        else:
            print("  ✗ Nenhum vídeo longo encontrado\n")

    print("=" * 60)
    print(f"{len(videos)} vídeo(s) no total.")
    return videos


def main(canais=None, saida_json=None):
    """
    Assinatura mantida para o `main.py` (importa como `fetch_videos`).
    Com `saida_json`, grava a lista em JSON para as etapas seguintes lerem.
    """
    videos = buscar(canais=canais)

    if saida_json:
        with open(saida_json, "w", encoding="utf-8") as arquivo:
            json.dump(videos, arquivo, ensure_ascii=False, indent=2)
        print(f"Gravado em: {saida_json}")

    return videos


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Busca o último vídeo longo de cada canal.")
    parser.add_argument("--canais", help="lista de @handles separada por vírgula (ignora canais.txt)")
    parser.add_argument("--json", dest="saida_json", help="grava o resultado neste arquivo JSON")
    args = parser.parse_args()

    lista = [c.strip() for c in args.canais.split(",")] if args.canais else None
    videos = main(canais=lista, saida_json=args.saida_json)

    if not args.saida_json and videos:
        print("\nDica: use --json videos.json para passar o resultado para a próxima etapa.")
