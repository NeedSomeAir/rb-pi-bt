#!/bin/bash

# Bluetooth setup script for Raspberry Pi 4 with Ubuntu Desktop 22.04
# This script installs and configures Bluetooth for message reception

echo "========================================="
echo "Raspberry Pi Bluetooth Setup - Part 2"
echo "Bluetooth Configuration"
echo "========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please run this script as a regular user (not root)"
    exit 1
fi

# Install Bluetooth packages
echo "Installing Bluetooth packages..."
sudo apt update
sudo apt install -y \
    bluetooth \
    bluez \
    bluez-tools \
    python3-bluez \
    python3-pip \
    python3-dev \
    libbluetooth-dev \
    blueman

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user \
    pybluez \
    pygame \
    pyttsx3 \
    plyer \
    colorama

# Enable and start Bluetooth service
echo "Enabling Bluetooth service..."
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Configure Bluetooth for SPP (Serial Port Profile)
echo "Configuring Bluetooth..."

# Add user to bluetooth group
sudo usermod -a -G bluetooth $USER

# Configure Bluetooth to be discoverable
sudo tee /etc/bluetooth/main.conf > /dev/null <<EOF
[General]
Name = Pi-Bluetooth-Receiver
Class = 0x000100
DiscoverableTimeout = 0
PairableTimeout = 0
Discoverable = yes
Pairable = yes
AutoEnable = true

[Policy]
AutoEnable = true
EOF

# Create SPP configuration
sudo tee /etc/systemd/system/bluetooth-spp.service > /dev/null <<EOF
[Unit]
Description=Bluetooth SPP
After=bluetooth.service
Requires=bluetooth.service

[Service]
ExecStart=/usr/bin/sdptool add --channel=1 SP
Type=oneshot
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Enable SPP service
sudo systemctl enable bluetooth-spp
sudo systemctl start bluetooth-spp

# Configure rfcomm
echo "Configuring RFCOMM..."
sudo tee /etc/bluetooth/rfcomm.conf > /dev/null <<EOF
rfcomm0 {
    bind no;
    device 00:00:00:00:00:00;
    channel 1;
    comment "Bluetooth receiver";
}
EOF

# Restart Bluetooth service
echo "Restarting Bluetooth service..."
sudo systemctl restart bluetooth

# Check Bluetooth status
echo "Checking Bluetooth status..."
sudo systemctl status bluetooth --no-pager

# Make Pi discoverable and pairable
echo "Making Pi discoverable and pairable..."
bluetoothctl <<EOF
power on
agent on
default-agent
discoverable on
pairable on
EOF

# Get Bluetooth info
echo "========================================="
echo "Bluetooth Configuration Complete!"
echo "========================================="
echo "Bluetooth Status:"
bluetoothctl show

echo ""
echo "To pair with Android device:"
echo "1. On Android, enable Bluetooth and search for devices"
echo "2. Look for 'Pi-Bluetooth-Receiver' in the list"
echo "3. Pair with the device"
echo "4. Accept any pairing requests on both devices"
echo ""
echo "Pi Bluetooth Address: $(bluetoothctl show | grep 'Controller' | cut -d' ' -f2)"
echo "Device Name: Pi-Bluetooth-Receiver"
echo ""
echo "Next step: Run install_dependencies.sh"
echo "========================================="
