# Utility functions for Bluetooth Message Broadcaster
# utils.py

import os
import subprocess
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BluetoothUtils:
    """Utility functions for Bluetooth operations"""
    
    @staticmethod
    def is_bluetooth_available():
        """Check if Bluetooth is available and enabled"""
        try:
            result = subprocess.run(['hciconfig', 'hci0'], 
                                  capture_output=True, text=True)
            return 'UP RUNNING' in result.stdout
        except Exception as e:
            logger.error(f"Error checking Bluetooth status: {e}")
            return False
    
    @staticmethod
    def get_paired_devices():
        """Get list of paired Bluetooth devices"""
        try:
            result = subprocess.run(['bluetoothctl', 'paired-devices'], 
                                  capture_output=True, text=True)
            devices = []
            for line in result.stdout.split('\n'):
                if line.startswith('Device'):
                    parts = line.split(' ', 2)
                    if len(parts) >= 3:
                        address = parts[1]
                        name = parts[2] if len(parts) > 2 else "Unknown"
                        devices.append({'address': address, 'name': name})
            return devices
        except Exception as e:
            logger.error(f"Error getting paired devices: {e}")
            return []
    
    @staticmethod
    def make_discoverable():
        """Make the Pi discoverable for pairing"""
        try:
            commands = [
                'power on',
                'agent on',
                'default-agent',
                'discoverable on',
                'pairable on'
            ]
            
            for cmd in commands:
                subprocess.run(['bluetoothctl', cmd], 
                             capture_output=True, text=True)
            
            logger.info("Pi is now discoverable and pairable")
            return True
        except Exception as e:
            logger.error(f"Error making Pi discoverable: {e}")
            return False
    
    @staticmethod
    def get_bluetooth_info():
        """Get Bluetooth adapter information"""
        try:
            result = subprocess.run(['bluetoothctl', 'show'], 
                                  capture_output=True, text=True)
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            return info
        except Exception as e:
            logger.error(f"Error getting Bluetooth info: {e}")
            return {}

class AudioUtils:
    """Utility functions for audio operations"""
    
    @staticmethod
    def test_audio():
        """Test if audio output is working"""
        try:
            subprocess.run(['speaker-test', '-t', 'sine', '-f', '1000', '-l', '1'], 
                         timeout=3, capture_output=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def set_volume(level):
        """Set system volume level (0-100)"""
        try:
            subprocess.run(['amixer', 'set', 'Master', f'{level}%'], 
                         capture_output=True)
            return True
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False
    
    @staticmethod
    def get_volume():
        """Get current volume level"""
        try:
            result = subprocess.run(['amixer', 'get', 'Master'], 
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if '[' in line and '%' in line:
                    start = line.find('[') + 1
                    end = line.find('%')
                    return int(line[start:end])
        except Exception:
            pass
        return 50  # Default volume

class SystemUtils:
    """Utility functions for system operations"""
    
    @staticmethod
    def get_system_info():
        """Get system information"""
        info = {
            'hostname': os.uname().nodename,
            'timestamp': datetime.now().isoformat(),
            'uptime': SystemUtils.get_uptime(),
            'memory_usage': SystemUtils.get_memory_usage(),
            'disk_usage': SystemUtils.get_disk_usage()
        }
        return info
    
    @staticmethod
    def get_uptime():
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return int(uptime_seconds)
        except Exception:
            return 0
    
    @staticmethod
    def get_memory_usage():
        """Get memory usage percentage"""
        try:
            result = subprocess.run(['free'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if line.startswith('Mem:'):
                    parts = line.split()
                    total = int(parts[1])
                    used = int(parts[2])
                    return round((used / total) * 100, 1)
        except Exception:
            pass
        return 0
    
    @staticmethod
    def get_disk_usage():
        """Get disk usage percentage"""
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    return parts[4].replace('%', '')
        except Exception:
            pass
        return '0'
    
    @staticmethod
    def is_service_running(service_name):
        """Check if a systemd service is running"""
        try:
            result = subprocess.run(['systemctl', 'is-active', service_name], 
                                  capture_output=True, text=True)
            return result.stdout.strip() == 'active'
        except Exception:
            return False

class MessageUtils:
    """Utility functions for message processing"""
    
    @staticmethod
    def clean_message(message):
        """Clean and sanitize incoming message"""
        if not message:
            return ""
        
        # Remove control characters
        cleaned = ''.join(char for char in message if ord(char) >= 32 or char in '\n\r\t')
        
        # Strip whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    @staticmethod
    def format_message_for_display(message, sender_info=None):
        """Format message for display with timestamp and sender info"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if sender_info:
            return f"[{timestamp}] {sender_info}: {message}"
        else:
            return f"[{timestamp}] Received: {message}"
    
    @staticmethod
    def format_message_for_log(message, sender_info=None, event_type="MESSAGE"):
        """Format message for logging"""
        timestamp = datetime.now().isoformat()
        if sender_info:
            return f"{timestamp} | {event_type} | {sender_info} | {message}"
        else:
            return f"{timestamp} | {event_type} | {message}"
