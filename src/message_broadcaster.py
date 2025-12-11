# Message Broadcasting Module
# message_broadcaster.py

import logging
import subprocess
import threading
import time
import os
from datetime import datetime
from config import Config
from utils import AudioUtils, MessageUtils

logger = logging.getLogger(__name__)

class MessageBroadcaster:
    """Handles broadcasting received messages through various channels"""
    
    def __init__(self):
        self.config = Config()
        self.audio_queue = []
        self.audio_lock = threading.Lock()
        self.is_audio_playing = False
        
        # Initialize audio
        if self.config.ENABLE_AUDIO_BROADCAST:
            self._init_audio()
    
    def _init_audio(self):
        """Initialize audio system"""
        try:
            # Test if espeak is available
            subprocess.run(['espeak', '--version'], 
                         capture_output=True, check=True)
            logger.info("Audio system initialized successfully")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("espeak not available, disabling audio broadcast")
            self.config.ENABLE_AUDIO_BROADCAST = False
    
    def broadcast_message(self, message, sender_info=None):
        """Broadcast a message through all enabled channels"""
        if not message or not Config.validate_message(message):
            return
        
        cleaned_message = MessageUtils.clean_message(message)
        
        # Broadcast through different channels
        if self.config.ENABLE_CONSOLE_OUTPUT:
            self._broadcast_to_console(cleaned_message, sender_info)
        
        if self.config.ENABLE_AUDIO_BROADCAST:
            self._broadcast_to_audio(cleaned_message)
        
        if self.config.ENABLE_DISPLAY_BROADCAST:
            self._broadcast_to_display(cleaned_message, sender_info)
        
        if self.config.ENABLE_FILE_LOGGING:
            self._broadcast_to_file(cleaned_message, sender_info)
    
    def _broadcast_to_console(self, message, sender_info=None):
        """Print message to console with formatting"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            separator = '='*50
            
            # Print efficiently
            print(f"\n{separator}")
            print("📱 BLUETOOTH MESSAGE RECEIVED")
            print(separator)
            print(f"Time: {timestamp}")
            if sender_info:
                print(f"From: {sender_info}")
            print(f"Message: {message}")
            print(f"{separator}\n")
        except Exception as e:
            logger.error(f"Error broadcasting to console: {e}")
    
    def _broadcast_to_audio(self, message):
        """Convert message to speech using espeak"""
        def speak_message():
            try:
                # Limit message length for TTS
                speak_text = message[:200] + "... message truncated" if len(message) > 200 else message
                
                # Use espeak for text-to-speech
                cmd = [
                    'espeak',
                    '-s', str(self.config.TTS_RATE),
                    '-a', str(int(self.config.TTS_VOLUME * 200)),
                    speak_text
                ]
                
                subprocess.run(cmd, capture_output=True, timeout=30)
                logger.info("Message spoken successfully")
                
            except subprocess.TimeoutExpired:
                logger.warning("TTS timeout - message too long")
            except Exception as e:
                logger.error(f"Error in text-to-speech: {e}")
            finally:
                self.is_audio_playing = False
        
        # Run TTS in separate thread to avoid blocking
        if not self.is_audio_playing:
            self.is_audio_playing = True
            threading.Thread(target=speak_message, daemon=True).start()
    
    def _broadcast_to_display(self, message, sender_info=None):
        """Show desktop notification"""
        try:
            title = self.config.NOTIFICATION_TITLE
            if sender_info:
                title += f" from {sender_info}"
            
            # Limit message length for notification
            display_message = message[:100] + "..." if len(message) > 100 else message
            
            # Use notify-send for desktop notifications
            cmd = [
                'notify-send',
                '-t', str(self.config.NOTIFICATION_TIMEOUT),
                '-i', 'bluetooth',
                title,
                display_message
            ]
            
            subprocess.run(cmd, capture_output=True, timeout=5)
            logger.info("Desktop notification sent")
            
        except Exception as e:
            logger.error(f"Error showing desktop notification: {e}")
    
    def _broadcast_to_file(self, message, sender_info=None):
        """Log message to file with buffering"""
        try:
            log_message = MessageUtils.format_message_for_log(message, sender_info)
            
            # Write to daily log file
            log_file = os.path.join(
                self.config.LOG_DIR, 
                f"messages_{datetime.now().strftime('%Y%m%d')}.log"
            )
            
            # Use buffered writing for better performance
            with open(log_file, 'a', encoding='utf-8', buffering=8192) as f:
                f.write(log_message + '\n')
            
            logger.info(f"Message logged to {log_file}")
            
        except Exception as e:
            logger.error(f"Error logging message to file: {e}")
    
    def broadcast_system_event(self, event_type, details=None):
        """Broadcast system events (connection, disconnection, etc.)"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            message = f"System Event: {event_type}"
            
            if details:
                message += f" - {details}"
            
            if self.config.ENABLE_CONSOLE_OUTPUT:
                print(f"\n[{timestamp}] 🔔 {message}")
            
            if self.config.ENABLE_FILE_LOGGING:
                log_message = MessageUtils.format_message_for_log(
                    message, event_type=event_type
                )
                
                log_file = os.path.join(
                    self.config.LOG_DIR, 
                    f"system_{datetime.now().strftime('%Y%m%d')}.log"
                )
                
                # Use buffered writing for better performance
                with open(log_file, 'a', encoding='utf-8', buffering=8192) as f:
                    f.write(log_message + '\n')
            
            logger.info(f"System event: {event_type}")
            
        except Exception as e:
            logger.error(f"Error broadcasting system event: {e}")
    
    def test_all_outputs(self):
        """Test all broadcasting methods"""
        test_message = "This is a test message from Bluetooth receiver"
        
        print("Testing all broadcast methods...")
        
        # Test console output
        if self.config.ENABLE_CONSOLE_OUTPUT:
            print("✓ Testing console output...")
            self._broadcast_to_console(test_message, "Test Device")
        
        # Test audio output
        if self.config.ENABLE_AUDIO_BROADCAST:
            print("✓ Testing audio output...")
            self._broadcast_to_audio("Audio test successful")
            time.sleep(2)  # Wait for audio to finish
        
        # Test display notification
        if self.config.ENABLE_DISPLAY_BROADCAST:
            print("✓ Testing display notification...")
            self._broadcast_to_display(test_message, "Test Device")
        
        # Test file logging
        if self.config.ENABLE_FILE_LOGGING:
            print("✓ Testing file logging...")
            self._broadcast_to_file(test_message, "Test Device")
        
        print("✓ All tests completed!")

# Create global broadcaster instance
broadcaster = MessageBroadcaster()

if __name__ == "__main__":
    # Test the broadcaster
    print("Testing Message Broadcaster...")
    broadcaster.test_all_outputs()
