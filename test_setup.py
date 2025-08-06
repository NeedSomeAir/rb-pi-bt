#!/usr/bin/env python3
# Test script to verify the Bluetooth receiver setup
# test_setup.py

import os
import sys
import subprocess
import importlib.util

def test_imports():
    """Test if all required Python modules can be imported"""
    print("🔍 Testing Python imports...")
    
    required_modules = [
        'bluetooth',
        'logging',
        'threading',
        'signal',
        'subprocess',
        'time',
        'datetime',
        'configparser'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} - FAILED")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed imports: {failed_imports}")
        print("   Run: pip3 install --user pybluez")
        return False
    else:
        print("✅ All required modules imported successfully")
        return True

def test_bluetooth_service():
    """Test if Bluetooth service is running"""
    print("\n🔍 Testing Bluetooth service...")
    
    try:
        result = subprocess.run(['systemctl', 'is-active', 'bluetooth'], 
                              capture_output=True, text=True)
        if result.stdout.strip() == 'active':
            print("   ✅ Bluetooth service is active")
            return True
        else:
            print(f"   ❌ Bluetooth service status: {result.stdout.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Error checking Bluetooth service: {e}")
        return False

def test_bluetooth_adapter():
    """Test if Bluetooth adapter is available"""
    print("\n🔍 Testing Bluetooth adapter...")
    
    try:
        result = subprocess.run(['hciconfig', 'hci0'], 
                              capture_output=True, text=True)
        if 'UP RUNNING' in result.stdout:
            print("   ✅ Bluetooth adapter is UP and RUNNING")
            return True
        else:
            print("   ❌ Bluetooth adapter is not running")
            print(f"   Output: {result.stdout}")
            return False
    except Exception as e:
        print(f"   ❌ Error checking Bluetooth adapter: {e}")
        return False

def test_audio_system():
    """Test if audio system is working"""
    print("\n🔍 Testing audio system...")
    
    # Test espeak
    try:
        result = subprocess.run(['espeak', '--version'], 
                              capture_output=True, text=True, timeout=5)
        print("   ✅ espeak is available")
        
        # Test actual speech
        subprocess.run(['espeak', '-s', '150', 'Audio test successful'], 
                      capture_output=True, timeout=10)
        print("   ✅ Text-to-speech test completed")
        return True
    except subprocess.TimeoutExpired:
        print("   ⚠️  espeak timeout - audio may not be configured")
        return False
    except Exception as e:
        print(f"   ❌ espeak error: {e}")
        return False

def test_notifications():
    """Test if desktop notifications work"""
    print("\n🔍 Testing desktop notifications...")
    
    try:
        result = subprocess.run(['notify-send', '--version'], 
                              capture_output=True, text=True)
        print("   ✅ notify-send is available")
        
        # Send test notification
        subprocess.run(['notify-send', '-t', '3000', 'Bluetooth Test', 'Notification system working'], 
                      capture_output=True)
        print("   ✅ Test notification sent")
        return True
    except Exception as e:
        print(f"   ❌ Notification error: {e}")
        return False

def test_project_files():
    """Test if all project files are in place"""
    print("\n🔍 Testing project files...")
    
    base_dir = os.path.expanduser("~/bluetooth_project")
    required_files = [
        'src/bluetooth_receiver.py',
        'src/config.py',
        'src/utils.py',
        'src/message_broadcaster.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All project files found")
        return True

def test_permissions():
    """Test if user has required permissions"""
    print("\n🔍 Testing user permissions...")
    
    # Check if user is in bluetooth group
    try:
        result = subprocess.run(['groups'], capture_output=True, text=True)
        groups = result.stdout.strip().split()
        
        if 'bluetooth' in groups:
            print("   ✅ User is in bluetooth group")
        else:
            print("   ❌ User is NOT in bluetooth group")
            print("   Run: sudo usermod -a -G bluetooth $USER")
            return False
        
        if 'audio' in groups:
            print("   ✅ User is in audio group")
        else:
            print("   ⚠️  User is NOT in audio group (audio may not work)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking groups: {e}")
        return False

def test_service_installation():
    """Test if systemd service is properly installed"""
    print("\n🔍 Testing service installation...")
    
    service_file = "/etc/systemd/system/bluetooth-receiver.service"
    
    if os.path.exists(service_file):
        print("   ✅ Service file exists")
        
        try:
            result = subprocess.run(['systemctl', 'is-enabled', 'bluetooth-receiver'], 
                                  capture_output=True, text=True)
            if result.stdout.strip() == 'enabled':
                print("   ✅ Service is enabled")
            else:
                print(f"   ⚠️  Service status: {result.stdout.strip()}")
            
            return True
        except Exception as e:
            print(f"   ❌ Error checking service status: {e}")
            return False
    else:
        print("   ❌ Service file not found")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("🔵 Raspberry Pi Bluetooth Receiver - Setup Test")
    print("="*60)
    
    tests = [
        ("Python Imports", test_imports),
        ("Bluetooth Service", test_bluetooth_service),
        ("Bluetooth Adapter", test_bluetooth_adapter),
        ("Audio System", test_audio_system),
        ("Desktop Notifications", test_notifications),
        ("Project Files", test_project_files),
        ("User Permissions", test_permissions),
        ("Service Installation", test_service_installation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ {test_name} failed with exception: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📋 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\n🚀 Next steps:")
        print("   1. Start service: sudo systemctl start bluetooth-receiver")
        print("   2. Pair Android device with 'Pi-Bluetooth-Receiver'")
        print("   3. Send messages using Bluetooth Terminal app")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("   - Install missing packages: sudo apt install bluetooth bluez python3-bluez")
        print("   - Add user to groups: sudo usermod -a -G bluetooth,audio $USER")
        print("   - Enable Bluetooth: sudo systemctl enable bluetooth")
        print("   - Restart after group changes: logout and login again")
    
    print("="*60)
    return failed

if __name__ == "__main__":
    sys.exit(main())
