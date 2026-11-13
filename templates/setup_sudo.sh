#!/usr/bin/env bash
# Dijalankan SEKALI oleh pengguna di terminal biasa (butuh password sudo).
# Agen AI tidak boleh menjalankan sudo.
set -e
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential git curl wget unzip p7zip-full \
  python3 python3-pip python3-venv cmake ninja-build clang lld \
  pkg-config libsdl2-dev libvulkan-dev vulkan-tools \
  libgl1-mesa-dev ripgrep jq flatpak file xxd binutils
sudo apt install -y openjdk-21-jdk || sudo apt install -y openjdk-17-jdk
echo
echo "Selesai. Jalankan: source ~/.bashrc"
echo "Lalu buka OpenCode dan kirim PERINTAH 2 dari README."
