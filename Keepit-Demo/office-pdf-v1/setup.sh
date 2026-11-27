#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
# Linux / Debian / Ubuntu. Review commands before installing system packages.
sudo apt-get update
sudo apt-get install -y --no-install-recommends python3 python3-venv libreoffice-writer libreoffice-impress libseccomp2 fontconfig fonts-liberation fonts-crosextra-carlito fonts-crosextra-caladea
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
mkdir -p "$HOME/.local/share/fonts/keepit-demo"
cp fonts/Pangolin-Regular.ttf "$HOME/.local/share/fonts/keepit-demo/"
fc-cache -f "$HOME/.local/share/fonts/keepit-demo"
echo 'Installed. Run: ./run.sh'
