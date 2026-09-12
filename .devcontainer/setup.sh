#!/usr/bin/env bash
# Provision both labs. Runs once, when the container is created.
#
# Everything here is the same `kestrel.py setup` a student would run by hand - the
# container just runs it for them, so the first thing they type is an attack
# rather than an install. Both days are installed whichever configuration you
# picked; they share one requirements.txt, so the second one is nearly free.
#
#   usage: setup.sh [day1|day2]      which day to point at in the closing message
set -euo pipefail

FOCUS="${1:-day1}"
cd "$(dirname "$0")/.."

# The container image provides `python`; a macOS or Linux host often only has
# `python3`. Pick whichever is there so this script can be run and tested outside
# the container too.
PY="$(command -v python || command -v python3 || true)"
if [ -z "$PY" ]; then
  echo "No python on PATH - cannot provision the labs." >&2
  exit 1
fi
echo "using $PY ($("$PY" --version 2>&1))"

# The two .venv paths are named volumes (see devcontainer.json) and Docker creates
# them owned by root. Hand them to the user we actually run as, or pip cannot write.
for day in workshop-day1 workshop-day2; do
  if [ -d "$day/.venv" ] && [ ! -w "$day/.venv" ]; then
    sudo chown -R "$(id -u):$(id -g)" "$day/.venv"
  fi
done

for day in workshop-day1 workshop-day2; do
  echo ""
  echo "=== $day ==============================================================="
  ( cd "$day" && "$PY" kestrel.py setup && "$PY" kestrel.py doctor )
done

if [ "$FOCUS" = "day2" ]; then
  DIR=workshop-day2; FIRST="attack all"; BLURB="all 8 stop - a LANDED result is a regression"; REAL=b1
else
  DIR=workshop-day1; FIRST="attack all"; BLURB="all 7 stop - a LANDED result is a regression"; REAL=a3
fi

cat <<EOF

=======================================================================
  Kestrel Goat SOLUTION BUILD is ready. Both labs installed and seeded.

  This is the answer key, not the lab. Teach from ollama-real-model-support.

  Start here:

      cd $DIR
      python kestrel.py $FIRST     # $BLURB
      python kestrel.py run           # then open the forwarded port 8000

  Storefront     http://127.0.0.1:8000/
  Control room   http://127.0.0.1:8000/console
  Tutorials      http://127.0.0.1:8000/tutorial

  The model is the offline mock by default - no API key, no network needed.
  To use a real model, run Ollama on your HOST (not in here) and:

      LLM_PROVIDER=ollama python kestrel.py attack $REAL

  Read $DIR/README.md next.
=======================================================================
EOF
