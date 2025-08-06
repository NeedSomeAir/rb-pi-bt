#!/usr/bin/env python3
# Main Bluetooth Message Receiver
# bluetooth_receiver.py

import bluetooth
import logging
import signal
import sys
import threading
import time
from datetime import datetime
from config import Config
from message_broadcaster import MessageBroadcaster
from utils import BluetoothUtils, SystemUtils

class BluetoothReceiver:
    """Main Bluetooth message receiver class"""
    
    def __init__(self):
        self.logger = Config.setup_logging()
        self.config = Config()
        self.broadcaster = MessageBroadcaster()
        self.server_socket = None
        self.client_socket = None
        self.is_running = False
        self.connected_devices = {}
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start the Bluetooth receiver service"""
        self.logger.info("Starting Bluetooth Message Receiver...")
        
        # Check if Bluetooth is available
        if not BluetoothUtils.is_bluetooth_available():
            self.logger.error("Bluetooth is not available or not enabled")
            return False
        
        # Make Pi discoverable
        BluetoothUtils.make_discoverable()
        
        # Get Bluetooth info
        bt_info = BluetoothUtils.get_bluetooth_info()
        self.logger.info(f"Bluetooth adapter info: {bt_info}")
        
        # Start server
        self.is_running = True
        self.broadcaster.broadcast_system_event("SERVICE_STARTED", "Bluetooth receiver started")
        
        try:
            self._start_server()
        except Exception as e:
            self.logger.error(f"Error starting server: {e}")
            self.stop()
            return False
        
        return True
    
    def _start_server(self):
        """Start the Bluetooth server socket"""
        try:
            # Create server socket
            self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.server_socket.bind(("", self.config.BLUETOOTH_PORT))
            self.server_socket.listen(1)
            
            self.logger.info(f"Listening for connections on RFCOMM channel {self.config.BLUETOOTH_PORT}")
            
            # Start status monitoring thread
            threading.Thread(target=self._monitor_status, daemon=True).start()
            
            while self.is_running:
                try:
                    self.logger.info("Waiting for Bluetooth connection...")
                    self.broadcaster.broadcast_system_event("WAITING_CONNECTION", "Ready to accept connections")
                    
                    # Accept connection
                    client_socket, client_info = self.server_socket.accept()
                    self.client_socket = client_socket
                    
                    client_address = client_info[0]
                    self.logger.info(f"Accepted connection from {client_address}")
                    self.broadcaster.broadcast_system_event("CONNECTION_ESTABLISHED", f"Connected to {client_address}")
                    
                    # Handle the connection
                    self._handle_client(client_socket, client_address)
                    
                except bluetooth.btcommon.BluetoothError as e:
                    if self.is_running:
                        self.logger.error(f"Bluetooth error: {e}")
                        time.sleep(5)  # Wait before retrying
                except Exception as e:
                    if self.is_running:
                        self.logger.error(f"Unexpected error: {e}")
                        time.sleep(5)
                finally:
                    if self.client_socket:
                        try:
                            self.client_socket.close()
                        except:
                            pass
                        self.client_socket = None
        
        except Exception as e:
            self.logger.error(f"Error in server: {e}")
        finally:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass
    
    def _handle_client(self, client_socket, client_address):
        """Handle messages from a connected client"""
        self.connected_devices[client_address] = {
            'connected_at': datetime.now(),
            'messages_received': 0
        }
        
        try:
            while self.is_running:
                try:
                    # Receive data
                    data = client_socket.recv(self.config.BUFFER_SIZE)
                    
                    if not data:
                        self.logger.info("Client disconnected")
                        break
                    
                    # Decode message
                    try:
                        message = data.decode('utf-8').strip()
                    except UnicodeDecodeError:
                        message = data.decode('utf-8', errors='ignore').strip()
                    
                    if message:
                        self.logger.info(f"Received message from {client_address}: {message}")
                        
                        # Update statistics
                        self.connected_devices[client_address]['messages_received'] += 1
                        
                        # Broadcast the message
                        self.broadcaster.broadcast_message(message, client_address)
                        
                        # Send acknowledgment back to client (optional)
                        try:
                            ack = f"Message received at {datetime.now().strftime('%H:%M:%S')}"
                            client_socket.send(ack.encode('utf-8'))
                        except:
                            pass  # Don't fail if can't send acknowledgment
                
                except bluetooth.btcommon.BluetoothError as e:
                    self.logger.warning(f"Bluetooth error with client {client_address}: {e}")
                    break
                except Exception as e:
                    self.logger.error(f"Error handling client {client_address}: {e}")
                    break
        
        finally:
            self.broadcaster.broadcast_system_event("CONNECTION_CLOSED", f"Disconnected from {client_address}")
            if client_address in self.connected_devices:
                stats = self.connected_devices[client_address]
                self.logger.info(f"Client {client_address} statistics: {stats['messages_received']} messages received")
                del self.connected_devices[client_address]
    
    def _monitor_status(self):
        """Monitor system status and log periodically"""
        while self.is_running:
            try:
                time.sleep(300)  # Log status every 5 minutes
                
                if self.is_running:
                    system_info = SystemUtils.get_system_info()
                    paired_devices = BluetoothUtils.get_paired_devices()
                    
                    status_info = {
                        'uptime': system_info['uptime'],
                        'memory_usage': system_info['memory_usage'],
                        'paired_devices': len(paired_devices),
                        'connected_clients': len(self.connected_devices)
                    }
                    
                    self.logger.info(f"Status check: {status_info}")
            
            except Exception as e:
                self.logger.error(f"Error in status monitoring: {e}")
    
    def stop(self):
        """Stop the Bluetooth receiver service"""
        self.logger.info("Stopping Bluetooth receiver...")
        self.is_running = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.broadcaster.broadcast_system_event("SERVICE_STOPPED", "Bluetooth receiver stopped")
        self.logger.info("Bluetooth receiver stopped")
    
    def get_status(self):
        """Get current status of the receiver"""
        return {
            'is_running': self.is_running,
            'connected_devices': self.connected_devices,
            'bluetooth_available': BluetoothUtils.is_bluetooth_available(),
            'system_info': SystemUtils.get_system_info()
        }

def main():
    """Main function"""
    print("="*60)
    print("🔵 Raspberry Pi Bluetooth Message Receiver")
    print("="*60)
    print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuration: {Config.BASE_DIR}")
    print("="*60)
    
    # Test broadcaster first
    print("Testing message broadcaster...")
    broadcaster = MessageBroadcaster()
    broadcaster.test_all_outputs()
    
    print("\nStarting Bluetooth receiver...")
    
    # Create and start receiver
    receiver = BluetoothReceiver()
    
    try:
        if receiver.start():
            print("✅ Bluetooth receiver started successfully!")
            print("📱 Ready to receive messages from Android devices")
            print("Press Ctrl+C to stop")
            
            # Keep the main thread alive
            while receiver.is_running:
                time.sleep(1)
        else:
            print("❌ Failed to start Bluetooth receiver")
            return 1
    
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    finally:
        receiver.stop()
    
    print("👋 Bluetooth receiver shutdown complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
