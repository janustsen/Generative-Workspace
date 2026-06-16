#!/usr/bin/env bash
#
# Trus — local VISION model setup (for the Layout Studio "screenshot → layout"
# importer). Pulls a vision-capable model into Ollama and wires TRUS_VISION_MODEL.
# Safe to re-run. The everyday text model (Qwen3-4B) is text-only, so this is a
# separate, optional model used only when you import a reference screenshot.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL="${VISION_MODEL:-qwen2.5vl:7b}"
FALLBACKS=("qwen2.5vl:3b" "llava:7b")
PORT="${OLLAMA_PORT:-11434}"
HOST="http://localhost:${PORT}"

say()  { printf '\033[1;36m▶ %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m! %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

command -v ollama >/dev/null 2>&1 || die "Ollama isn't installed. Run: make ollama-setup"
if ! curl -fsS --max-time 2 "$HOST/api/version" >/dev/null 2>&1; then
  say "Starting Ollama…"; mkdir -p "$ROOT/.ollama-logs"
  nohup ollama serve >"$ROOT/.ollama-logs/serve.log" 2>&1 &
  for _ in $(seq 1 30); do if curl -fsS --max-time 2 "$HOST/api/version" >/dev/null 2>&1; then break; fi; sleep 1; done
fi
curl -fsS --max-time 2 "$HOST/api/version" >/dev/null 2>&1 || die "Ollama server not reachable."

have() { ollama list 2>/dev/null | awk '{print $1}' | grep -qx "$1"; }
pulled=""
for tag in "$MODEL" "${FALLBACKS[@]}"; do
  if have "$tag"; then ok "Vision model present: $tag"; MODEL="$tag"; pulled=1; break; fi
  say "Pulling $tag … (a few GB; vision models are larger)"
  if ollama pull "$tag"; then ok "Pulled $tag"; MODEL="$tag"; pulled=1; break; fi
  warn "Couldn't pull $tag — trying a fallback."
done
[ -n "$pulled" ] || die "Could not pull any vision model. Check your network."

# Wire TRUS_VISION_MODEL into the .env the backend loads (and the repo root).
wire() {
  f="$1"; [ -f "$f" ] || return 0
  tmp="$(mktemp)"
  awk '/^# >>> trus vision >>>/{skip=1} /^# <<< trus vision <<</{skip=0; next} skip!=1{print}' "$f" > "$tmp"
  { cat "$tmp"; printf '\n# >>> trus vision >>> (managed by scripts/setup-vision.sh)\n';
    printf 'TRUS_VISION_MODEL=%s\n' "$MODEL"; printf '# <<< trus vision <<<\n'; } > "$f"
  rm -f "$tmp"
}
wire "$ROOT/backend/.env"; wire "$ROOT/.env"
ok "Wired TRUS_VISION_MODEL=$MODEL"

cat <<EOF

$(ok "Local vision is ready.")
  Model: $MODEL  (used only by the Studio screenshot importer)
  Restart the backend (make dev-local) to pick it up, then in the Studio use
  "Import screenshot" to turn a reference UI into a Trus layout.
EOF
