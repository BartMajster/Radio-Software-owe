#!/bin/bash

set -e

echo "======================================================="
echo "  Environment Installer for RPi Media System"
echo "======================================================="
echo ""

echo "[1/5] Updating system package lists..."
sudo apt update

echo "[2/5] Installing system packages..."
sudo apt install -y python3 python3-pip python3-venv vlc libvlc-dev python3-pyqt6 python3-requests libxcb-cursor0 matchbox-keyboard

sudo apt install -y fonts-dejavu fontconfig pulseaudio alsa-utils

echo "[3/5] Configuring Python virtual environment..."
VENV_DIR="env"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv --system-site-packages $VENV_DIR
    echo "  -> Environment '$VENV_DIR' created."
else
    echo "  -> Environment '$VENV_DIR' already exists."
fi

source $VENV_DIR/bin/activate

echo "[4/5] Installing PIP packages (python-vlc)..."
pip install --upgrade pip
pip install python-vlc

echo "[5/5] Activating environment and launching application"
source env/bin/activate

DISPLAY=:0 python3 ~/Desktop/piRadio/code/main.py

echo ""
echo "======================================================="
echo "  INSTALLATION COMPLETE!"
echo "======================================================="
echo ""
echo "To run the application (e.g. via SSH), use the following commands in the project directory:"
echo ""
echo "  source env/bin/activate"
echo "  DISPLAY=:0 python3 main.py"
echo ""
echo "======================================================="
