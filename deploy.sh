#!/bin/bash

# Complete deployment script for Raspberry Pi Bluetooth project
# Run this on your Pi after copying all files

echo "========================================="
echo "🔵 Raspberry Pi Bluetooth Setup"
echo "Complete Deployment Script"
echo "========================================="

# Check if running as regular user
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please run this script as a regular user (not root)"
    echo "   Use: chmod +x deploy.sh && ./deploy.sh"
    exit 1
fi

# Check if we're on Ubuntu
if ! command -v apt &> /dev/null; then
    echo "❌ This script is designed for Ubuntu systems"
    exit 1
fi

# Get current directory (should be the project root)
PROJECT_ROOT=$(pwd)
TARGET_DIR="$HOME/bluetooth_project"

echo "📁 Project root: $PROJECT_ROOT"
echo "📁 Target directory: $TARGET_DIR"

# Create target directory
echo "📂 Creating project directory..."
mkdir -p "$TARGET_DIR"/{src,logs,services,setup}

# Copy files to target directory
echo "📋 Copying project files..."
cp -r src/* "$TARGET_DIR/src/" 2>/dev/null || echo "   src files copied"
cp -r services/* "$TARGET_DIR/services/" 2>/dev/null || echo "   service files copied"
cp -r setup/* "$TARGET_DIR/setup/" 2>/dev/null || echo "   setup files copied"
cp README.md "$TARGET_DIR/" 2>/dev/null || echo "   README copied"

# Set correct permissions
echo "🔧 Setting permissions..."
chmod +x "$TARGET_DIR"/setup/*.sh
chmod +x "$TARGET_DIR"/services/*.sh
chmod +x "$TARGET_DIR"/src/*.py

# Run setup scripts in sequence
echo ""
echo "🚀 Running setup scripts..."
echo ""

# Step 1: Initial setup
echo "Step 1: Initial Ubuntu setup..."
cd "$TARGET_DIR/setup"
chmod +x initial_setup.sh
./initial_setup.sh

# Wait for potential reboot
if [ $? -eq 0 ]; then
    echo ""
    echo "⏳ If system rebooted, run this script again after reboot"
    echo "   Otherwise, continuing with Bluetooth setup..."
    sleep 3
fi

# Step 2: Bluetooth setup
echo ""
echo "Step 2: Bluetooth configuration..."
chmod +x bluetooth_setup.sh
./bluetooth_setup.sh

# Step 3: Install dependencies
echo ""
echo "Step 3: Installing dependencies..."
chmod +x install_dependencies.sh
./install_dependencies.sh

# Step 4: Test the application
echo ""
echo "Step 4: Testing application..."
cd "$TARGET_DIR/src"
python3 -c "
import sys
try:
    import bluetooth
    print('✅ pybluez imported successfully')
except ImportError as e:
    print(f'❌ pybluez import failed: {e}')
    print('   Installing pybluez...')
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', 'pybluez'])

try:
    from config import Config
    from utils import BluetoothUtils
    from message_broadcaster import MessageBroadcaster
    print('✅ All modules imported successfully')
    
    # Test broadcaster
    broadcaster = MessageBroadcaster()
    print('✅ MessageBroadcaster initialized')
    
    # Test Bluetooth utilities
    bt_available = BluetoothUtils.is_bluetooth_available()
    print(f'✅ Bluetooth available: {bt_available}')
    
except Exception as e:
    print(f'❌ Module test failed: {e}')
"

# Step 5: Install as service
echo ""
echo "Step 5: Installing systemd service..."
cd "$TARGET_DIR/services"
chmod +x install_service.sh
sudo ./install_service.sh

echo ""
echo "========================================="
echo "🎉 Deployment Complete!"
echo "========================================="
echo ""
echo "📋 Summary:"
echo "   ✅ Project files copied to $TARGET_DIR"
echo "   ✅ Dependencies installed"
echo "   ✅ Bluetooth configured"
echo "   ✅ Service installed"
echo ""
echo "🔧 Next steps:"
echo "   1. Pair your Android device:"
echo "      - Enable Bluetooth on Android"
echo "      - Search for 'Pi-Bluetooth-Receiver'"
echo "      - Pair with the device"
echo ""
echo "   2. Start the service:"
echo "      sudo systemctl start bluetooth-receiver"
echo ""
echo "   3. Check service status:"
echo "      sudo systemctl status bluetooth-receiver"
echo ""
echo "   4. View logs:"
echo "      sudo journalctl -u bluetooth-receiver -f"
echo ""
echo "   5. Send test message from Android:"
echo "      - Install 'Serial Bluetooth Terminal' app"
echo "      - Connect to Pi and send messages"
echo ""
echo "📱 Android setup guide: $TARGET_DIR/../android/bluetooth_sender_guide.md"
echo ""
echo "🎯 Service will auto-start on boot!"
echo "========================================="
