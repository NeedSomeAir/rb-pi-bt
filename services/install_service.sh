#!/bin/bash

# Service installation script for Bluetooth Message Receiver

echo "========================================="
echo "Installing Bluetooth Receiver Service"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root (use sudo)"
    exit 1
fi

# Define paths
PROJECT_DIR="/home/ubuntu/bluetooth_project"
SERVICE_NAME="bluetooth-receiver"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Create project directory if it doesn't exist
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Creating project directory..."
    mkdir -p $PROJECT_DIR/{src,logs}
    chown -R ubuntu:ubuntu $PROJECT_DIR
fi

# Copy service file
echo "Installing systemd service..."
cp ./bluetooth-receiver.service $SERVICE_FILE

# Set correct permissions
chmod 644 $SERVICE_FILE

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable service
echo "Enabling service to start on boot..."
systemctl enable $SERVICE_NAME

# Create log directory and set permissions
mkdir -p $PROJECT_DIR/logs
chown -R ubuntu:bluetooth $PROJECT_DIR/logs
chmod 775 $PROJECT_DIR/logs

# Add ubuntu user to required groups
echo "Adding ubuntu user to required groups..."
usermod -a -G bluetooth ubuntu
usermod -a -G audio ubuntu

# Test service configuration
echo "Testing service configuration..."
systemctl status $SERVICE_NAME --no-pager

echo ""
echo "========================================="
echo "Service Installation Complete!"
echo "========================================="
echo "Service name: $SERVICE_NAME"
echo "Service file: $SERVICE_FILE"
echo "Project directory: $PROJECT_DIR"
echo ""
echo "To start the service:"
echo "  sudo systemctl start $SERVICE_NAME"
echo ""
echo "To check service status:"
echo "  sudo systemctl status $SERVICE_NAME"
echo ""
echo "To view service logs:"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "To stop the service:"
echo "  sudo systemctl stop $SERVICE_NAME"
echo ""
echo "To disable auto-start:"
echo "  sudo systemctl disable $SERVICE_NAME"
echo "========================================="

# Ask if user wants to start the service now
read -p "Start the service now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting service..."
    systemctl start $SERVICE_NAME
    sleep 2
    echo "Service status:"
    systemctl status $SERVICE_NAME --no-pager
fi
