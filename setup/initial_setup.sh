#!/bin/bash

# Initial setup script for Raspberry Pi 4 with Ubuntu Desktop 22.04
# This script performs the initial system configuration and updates

echo "========================================="
echo "Raspberry Pi Bluetooth Setup - Part 1"
echo "Initial Ubuntu Configuration"
echo "========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please run this script as a regular user (not root)"
    exit 1
fi

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Set timezone (adjust as needed)
echo "Setting timezone to UTC (change if needed)..."
sudo timedatectl set-timezone UTC

# Set hostname for easier identification
echo "Setting hostname to 'pi-bluetooth'..."
sudo hostnamectl set-hostname pi-bluetooth

# Create project directories
echo "Creating project directories..."
mkdir -p ~/bluetooth_project/logs
cd ~/bluetooth_project

# Enable SSH for remote access (optional)
echo "Enabling SSH service..."
sudo systemctl enable ssh
sudo systemctl start ssh

# Install basic utilities
echo "Installing basic utilities..."
sudo apt install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    tree \
    unzip

# Configure automatic login (optional - for headless operation)
read -p "Do you want to enable automatic login? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl edit getty@tty1.service
    echo "Add the following lines to the override file:"
    echo "[Service]"
    echo "ExecStart="
    echo "ExecStart=-/sbin/agetty --autologin ubuntu --noclear %I \$TERM"
fi

# Disable unnecessary services to save resources
echo "Optimizing system services..."
sudo systemctl disable snapd.service
sudo systemctl disable snapd.socket

# Configure firewall
echo "Configuring firewall..."
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow from 192.168.0.0/16 to any port 22

# Create swap file for better performance
echo "Creating swap file (1GB)..."
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Set up log rotation
echo "Configuring log rotation..."
sudo tee /etc/logrotate.d/bluetooth-project > /dev/null <<EOF
/home/ubuntu/bluetooth_project/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

echo "========================================="
echo "Initial setup completed successfully!"
echo "========================================="
echo "Next steps:"
echo "1. Reboot the system: sudo reboot"
echo "2. Run bluetooth_setup.sh after reboot"
echo "3. Current hostname: $(hostname)"
echo "4. Current IP: $(hostname -I | cut -d' ' -f1)"
echo "========================================="

# Ask if user wants to reboot now
read -p "Reboot now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo reboot
fi
