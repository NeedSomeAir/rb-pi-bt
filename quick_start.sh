#!/bin/bash

# Quick start script for Raspberry Pi Bluetooth setup
# This script provides a guided setup process

echo "========================================="
echo "🔵 Raspberry Pi Bluetooth Quick Start"
echo "========================================="

# Check if we're on the Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  This doesn't appear to be a Raspberry Pi"
    echo "   Continuing anyway..."
fi

# Check Ubuntu version
if command -v lsb_release &> /dev/null; then
    UBUNTU_VERSION=$(lsb_release -r -s)
    echo "📋 Detected Ubuntu: $UBUNTU_VERSION"
    
    if [[ ! "$UBUNTU_VERSION" =~ ^22\. ]]; then
        echo "⚠️  This script is optimized for Ubuntu 22.04"
        echo "   Your version: $UBUNTU_VERSION"
        read -p "   Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Exiting..."
            exit 1
        fi
    fi
fi

# Menu system
show_menu() {
    echo ""
    echo "📋 Setup Options:"
    echo "1. 🚀 Full automatic setup (recommended)"
    echo "2. 🔧 Step-by-step manual setup"
    echo "3. 🧪 Test current setup"
    echo "4. 📱 View Android setup guide"
    echo "5. 🔍 Check service status"
    echo "6. 📋 Show useful commands"
    echo "7. ❌ Exit"
    echo ""
}

full_setup() {
    echo "🚀 Starting full automatic setup..."
    
    # Check if deploy script exists
    if [ -f "./deploy.sh" ]; then
        chmod +x deploy.sh
        ./deploy.sh
    else
        echo "❌ deploy.sh not found in current directory"
        echo "   Make sure you're in the project root directory"
        return 1
    fi
}

manual_setup() {
    echo "🔧 Manual setup selected"
    echo ""
    echo "Run these scripts in order:"
    echo "1. chmod +x setup/initial_setup.sh && ./setup/initial_setup.sh"
    echo "2. chmod +x setup/bluetooth_setup.sh && ./setup/bluetooth_setup.sh"
    echo "3. chmod +x setup/install_dependencies.sh && ./setup/install_dependencies.sh"
    echo "4. sudo chmod +x services/install_service.sh && sudo ./services/install_service.sh"
    echo ""
    read -p "Press Enter to continue..."
}

test_setup() {
    echo "🧪 Testing current setup..."
    
    if [ -f "./test_setup.py" ]; then
        python3 test_setup.py
    else
        echo "❌ test_setup.py not found"
        echo "   Running basic tests..."
        
        # Basic tests
        echo "Checking Bluetooth service..."
        systemctl is-active bluetooth
        
        echo "Checking Bluetooth adapter..."
        hciconfig hci0
        
        echo "Checking project files..."
        ls -la ~/bluetooth_project/src/
    fi
}

show_android_guide() {
    echo "📱 Android Setup Guide:"
    echo ""
    echo "1. Install 'Serial Bluetooth Terminal' from Play Store"
    echo "2. Enable Bluetooth on Android"
    echo "3. Pair with 'Pi-Bluetooth-Receiver'"
    echo "4. Open Serial Bluetooth Terminal app"
    echo "5. Connect to Pi device"
    echo "6. Send test message"
    echo ""
    echo "Expected behavior:"
    echo "- Message appears on Pi console"
    echo "- Text-to-speech announces message"
    echo "- Desktop notification (if GUI available)"
    echo "- Message logged to file"
    echo ""
    
    if [ -f "android/bluetooth_sender_guide.md" ]; then
        read -p "View full guide? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cat android/bluetooth_sender_guide.md | head -50
            echo "... (see android/bluetooth_sender_guide.md for full guide)"
        fi
    fi
}

check_service() {
    echo "🔍 Checking service status..."
    echo ""
    
    echo "📊 Bluetooth service:"
    systemctl status bluetooth --no-pager | head -10
    echo ""
    
    echo "📊 Bluetooth receiver service:"
    if systemctl is-active bluetooth-receiver &>/dev/null; then
        systemctl status bluetooth-receiver --no-pager | head -10
        echo ""
        echo "📋 Recent logs:"
        journalctl -u bluetooth-receiver --no-pager -n 10
    else
        echo "❌ Service not running or not installed"
        echo ""
        echo "To start: sudo systemctl start bluetooth-receiver"
        echo "To install: sudo ./services/install_service.sh"
    fi
    
    echo ""
    echo "📊 Bluetooth adapter info:"
    bluetoothctl show 2>/dev/null || echo "❌ bluetoothctl not available"
}

show_commands() {
    echo "📋 Useful Commands:"
    echo ""
    echo "🔧 Service Management:"
    echo "  sudo systemctl start bluetooth-receiver    # Start service"
    echo "  sudo systemctl stop bluetooth-receiver     # Stop service"
    echo "  sudo systemctl restart bluetooth-receiver  # Restart service"
    echo "  sudo systemctl status bluetooth-receiver   # Check status"
    echo ""
    echo "📋 Logs:"
    echo "  sudo journalctl -u bluetooth-receiver -f   # Follow service logs"
    echo "  tail -f ~/bluetooth_project/logs/*.log     # Follow application logs"
    echo ""
    echo "🔵 Bluetooth:"
    echo "  bluetoothctl                              # Bluetooth control"
    echo "  bluetoothctl discoverable on              # Make discoverable"
    echo "  bluetoothctl paired-devices               # List paired devices"
    echo "  hciconfig hci0                           # Adapter status"
    echo ""
    echo "🧪 Testing:"
    echo "  python3 test_setup.py                    # Test setup"
    echo "  python3 ~/bluetooth_project/src/bluetooth_receiver.py  # Manual run"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "  sudo systemctl restart bluetooth         # Restart Bluetooth"
    echo "  sudo rfkill unblock bluetooth           # Unblock Bluetooth"
    echo "  sudo hciconfig hci0 up                  # Bring adapter up"
}

# Main loop
while true; do
    show_menu
    read -p "Choose option (1-7): " choice
    
    case $choice in
        1)
            full_setup
            ;;
        2)
            manual_setup
            ;;
        3)
            test_setup
            ;;
        4)
            show_android_guide
            ;;
        5)
            check_service
            ;;
        6)
            show_commands
            ;;
        7)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-7."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
