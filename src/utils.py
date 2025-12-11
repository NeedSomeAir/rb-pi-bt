# Utility functions for Bluetooth Message Broadcaster
# utils.py

import os
import re
import subprocess
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BluetoothUtils:
    """Utility functions for Bluetooth operations"""
    
    # Cache for Bluetooth availability check (cached for 30 seconds)
    _bt_available_cache = {'value': None, 'timestamp': 0}
    _CACHE_DURATION = 30  # seconds
    
    @staticmethod
    def is_bluetooth_available():
        """Check if Bluetooth is available and enabled"""
        try:
            current_time = time.time()
            cache = BluetoothUtils._bt_available_cache
            
            # Use cached value if still valid
            if cache['value'] is not None and (current_time - cache['timestamp']) < BluetoothUtils._CACHE_DURATION:
                return cache['value']
            
            result = subprocess.run(['hciconfig', 'hci0'], 
                                  capture_output=True, text=True, timeout=5)
            is_available = 'UP RUNNING' in result.stdout
            
            # Update cache
            cache['value'] = is_available
            cache['timestamp'] = current_time
            
            return is_available
        except Exception as e:
            logger.error(f"Error checking Bluetooth status: {e}")
            return False
    
    # Cache for paired devices (cached for 60 seconds)
    _paired_devices_cache = {'value': None, 'timestamp': 0}
    
    @staticmethod
    def get_paired_devices():
        """Get list of paired Bluetooth devices"""
        try:
            current_time = time.time()
            cache = BluetoothUtils._paired_devices_cache
            
            # Use cached value if still valid
            if cache['value'] is not None and (current_time - cache['timestamp']) < 60:
                return cache['value']
            
            result = subprocess.run(['bluetoothctl', 'paired-devices'], 
                                  capture_output=True, text=True, timeout=10)
            devices = []
            for line in result.stdout.split('\n'):
                if line.startswith('Device'):
                    parts = line.split(' ', 2)
                    if len(parts) >= 3:
                        address = parts[1]
                        name = parts[2] if len(parts) > 2 else "Unknown"
                        devices.append({'address': address, 'name': name})
            
            # Update cache
            cache['value'] = devices
            cache['timestamp'] = current_time
            
            return devices
        except Exception as e:
            logger.error(f"Error getting paired devices: {e}")
            return []
    
    @staticmethod
    def make_discoverable():
        """Make the Pi discoverable for pairing"""
        try:
            # Use a single bluetoothctl call with multiple commands for efficiency
            commands = 'power on\nagent on\ndefault-agent\ndiscoverable on\npairable on\n'
            
            subprocess.run(['bluetoothctl'], 
                         input=commands,
                         capture_output=True, 
                         text=True,
                         timeout=10)
            
            logger.info("Pi is now discoverable and pairable")
            return True
        except Exception as e:
            logger.error(f"Error making Pi discoverable: {e}")
            return False
    
    # Cache for Bluetooth info (cached for 120 seconds)
    _bt_info_cache = {'value': None, 'timestamp': 0}
    
    @staticmethod
    def get_bluetooth_info():
        """Get Bluetooth adapter information"""
        try:
            current_time = time.time()
            cache = BluetoothUtils._bt_info_cache
            
            # Use cached value if still valid
            if cache['value'] is not None and (current_time - cache['timestamp']) < 120:
                return cache['value']
            
            result = subprocess.run(['bluetoothctl', 'show'], 
                                  capture_output=True, text=True, timeout=10)
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            # Update cache
            cache['value'] = info
            cache['timestamp'] = current_time
            
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
            # Use /proc/meminfo which is faster than running 'free' command
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                mem_total = mem_available = 0
                for line in lines:
                    if line.startswith('MemTotal:'):
                        mem_total = int(line.split()[1])
                    elif line.startswith('MemAvailable:'):
                        mem_available = int(line.split()[1])
                    if mem_total and mem_available:
                        break
                
                if mem_total > 0:
                    used = mem_total - mem_available
                    return round((used / mem_total) * 100, 1)
        except Exception:
            pass
        return 0
    
    @staticmethod
    def get_disk_usage():
        """Get disk usage percentage"""
        try:
            # Use os.statvfs which is faster than running df command
            stat = os.statvfs('/')
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_bfree * stat.f_frsize
            used = total - free
            percent = int((used / total) * 100)
            return str(percent)
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
    
    # Pre-compile regex for better performance (excludes newlines, tabs, carriage returns)
    _CONTROL_CHAR_PATTERN = re.compile(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]')
    
    @staticmethod
    def clean_message(message):
        """Clean and sanitize incoming message"""
        if not message:
            return ""
        
        # Remove control characters using pre-compiled regex (faster)
        # Preserves \n (0x0a), \r (0x0d), \t (0x09)
        cleaned = MessageUtils._CONTROL_CHAR_PATTERN.sub('', message)
        
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
