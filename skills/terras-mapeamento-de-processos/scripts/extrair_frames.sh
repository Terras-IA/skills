#!/usr/bin/env bash
# Extrai frames de um vídeo/gravação de tela e monta folhas de contato para leitura visual.
# Uso: extrair_frames.sh <video> [dir_saida=frames] [intervalo_seg=15] [largura=1280]
set -euo pipefail

VIDEO="${1:?uso: extrair_frames.sh <video> [dir_saida] [intervalo_seg] [largura]}"
OUT="${2:-frames}"
INTERVALO="${3:-15}"
LARGURA="${4:-1280}"

command -v ffmpeg >/dev/null || { echo "ffmpeg não encontrado" >&2; exit 1; }
mkdir -p "$OUT"

DURACAO=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$VIDEO" 2>/dev/null || echo 0)

echo "Vídeo: $VIDEO"
echo "Duração: $(python3 -c "print(f'{float('${DURACAO:-0}')/60:.1f} min')")  |  Intervalo: ${INTERVALO}s  |  Saída: $OUT"

ffmpeg -hide_banner -loglevel error -i "$VIDEO" \
  -vf "fps=1/${INTERVALO},scale=${LARGURA}:-2" -q:v 3 "$OUT/frame_%04d.jpg"

# Mapa frame -> timestamp (para citar evidência no relatório)
python3 - "$OUT" "$INTERVALO" <<'PY'
import sys, glob, os
out, intervalo = sys.argv[1], float(sys.argv[2])
frames = sorted(glob.glob(os.path.join(out, "frame_*.jpg")))
with open(os.path.join(out, "timestamps.txt"), "w") as f:
    for i, fr in enumerate(frames):
        s = int(round(i * intervalo))
        f.write(f"{os.path.basename(fr)}\t{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}\n")
print(f"Frames extraídos: {len(frames)}  ->  {out}/timestamps.txt")
PY

# Folhas de contato 4x4 (uma imagem por 16 frames) para leitura em lote
ffmpeg -hide_banner -loglevel error -framerate 1 -i "$OUT/frame_%04d.jpg" \
  -vf "scale=420:-2,tile=4x4:padding=6:margin=8:color=white" -q:v 3 "$OUT/folha_%03d.jpg" || true

ls "$OUT"/folha_*.jpg 2>/dev/null | wc -l | xargs -I{} echo "Folhas de contato: {} (4x4 frames cada; a ordem é a de timestamps.txt)"

cat <<'EOF'

Próximo passo: leia as folhas de contato com a ferramenta de leitura e registre, por frame,
o sistema aberto e a ação visível (ex.: "ERP > tela Pedido de venda — redigita dados do CRM").
Isso alimenta a seção "Telas observadas" da transcrição enriquecida.
EOF
