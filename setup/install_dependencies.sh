#!/bin/bash

# Install additional dependencies for the Bluetooth message broadcaster

echo "========================================="
echo "Installing Additional Dependencies"
echo "========================================="

# Install audio and TTS dependencies
echo "Installing audio and text-to-speech packages..."
sudo apt install -y \
    espeak \
    espeak-data \
    pulseaudio \
    pulseaudio-utils \
    alsa-utils \
    festival \
    festival-dev \
    sox \
    libsox-fmt-all

# Install GUI notification dependencies
echo "Installing GUI notification packages..."
sudo apt install -y \
    libnotify-bin \
    python3-notify2 \
    python3-gi \
    gir1.2-notify-0.7

# Install additional Python packages
echo "Installing additional Python packages..."
pip3 install --user \
    psutil \
    requests \
    configparser \
    logging \
    threading \
    queue \
    datetime

# Test audio system
echo "Testing audio system..."
speaker-test -t sine -f 1000 -l 1 & sleep 1 && killall speaker-test

# Test TTS
echo "Testing text-to-speech..."
echo "Bluetooth receiver ready" | espeak

# Set up audio permissions
echo "Configuring audio permissions..."
sudo usermod -a -G audio $USER

# Create log directory
mkdir -p ~/bluetooth_project/logs

echo "========================================="
echo "Dependencies installed successfully!"
echo "========================================="
echo "Audio test: You should have heard a beep and TTS"
echo "If no audio, check volume and audio output settings"
echo "Next step: Copy Python scripts and configure service"
echo "========================================="
