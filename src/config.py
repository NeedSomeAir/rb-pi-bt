# Configuration settings for Bluetooth Message Broadcaster
# config.py

import os
import logging
from datetime import datetime

class Config:
    """Configuration class for the Bluetooth receiver application"""
    
    # Bluetooth settings
    BLUETOOTH_PORT = 1  # RFCOMM channel
    BUFFER_SIZE = 1024  # Buffer size for receiving data
    
    # Paths
    BASE_DIR = os.path.expanduser("~/bluetooth_project")
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    
    # Ensure directories exist
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Logging settings
    LOG_FILE = os.path.join(LOG_DIR, f"bluetooth_receiver_{datetime.now().strftime('%Y%m%d')}.log")
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Broadcasting settings
    ENABLE_AUDIO_BROADCAST = True    # Enable text-to-speech
    ENABLE_DISPLAY_BROADCAST = True  # Enable GUI notifications
    ENABLE_CONSOLE_OUTPUT = True     # Enable console output
    ENABLE_FILE_LOGGING = True       # Enable file logging
    
    # Audio settings
    TTS_RATE = 150          # Speech rate (words per minute)
    TTS_VOLUME = 0.8        # Volume level (0.0 to 1.0)
    TTS_VOICE = 'english'   # Voice language
    
    # Display settings
    NOTIFICATION_TIMEOUT = 5000  # Notification timeout in milliseconds
    NOTIFICATION_TITLE = "Bluetooth Message"
    
    # Connection settings
    MAX_RECONNECT_ATTEMPTS = 5
    RECONNECT_DELAY = 5  # seconds
    
    # Message filtering
    IGNORE_EMPTY_MESSAGES = True
    MIN_MESSAGE_LENGTH = 1
    MAX_MESSAGE_LENGTH = 1000
    
    # Security settings
    ALLOWED_DEVICES = []  # Empty list means allow all devices
    REQUIRE_PAIRING = True
    
    @classmethod
    def setup_logging(cls):
        """Set up logging configuration"""
        logging.basicConfig(
            level=cls.LOG_LEVEL,
            format=cls.LOG_FORMAT,
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    @classmethod
    def get_bluetooth_address(cls):
        """Get the Pi's Bluetooth address"""
        try:
            import subprocess
            result = subprocess.run(['hciconfig', 'hci0'], 
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'BD Address:' in line:
                    return line.split('BD Address: ')[1].split(' ')[0]
        except Exception:
            pass
        return None
    
    @classmethod
    def validate_message(cls, message):
        """Validate incoming message"""
        if cls.IGNORE_EMPTY_MESSAGES and not message.strip():
            return False
        
        if len(message) < cls.MIN_MESSAGE_LENGTH:
            return False
            
        if len(message) > cls.MAX_MESSAGE_LENGTH:
            return False
            
        return True
