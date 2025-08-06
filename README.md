# Raspberry Pi Bluetooth Message Broadcaster

A complete implementation for Raspberry Pi 4 running Ubuntu Desktop 22.04 to receive Bluetooth messages from Android devices and broadcast them.

## Project Structure

```
rb-pi-bt/
├── README.md                    # This file
├── setup/
│   ├── initial_setup.sh         # Initial Ubuntu setup script
│   ├── bluetooth_setup.sh       # Bluetooth configuration script
│   └── install_dependencies.sh  # Install required packages
├── src/
│   ├── bluetooth_receiver.py    # Main Bluetooth message receiver
│   ├── message_broadcaster.py   # Message broadcasting module
│   ├── config.py               # Configuration settings
│   └── utils.py                # Utility functions
├── services/
│   ├── bluetooth-receiver.service # Systemd service file
│   └── install_service.sh       # Service installation script
├── android/
│   └── bluetooth_sender_guide.md # Guide for Android setup
└── logs/
    └── .gitkeep                 # Placeholder for log files
```

## Features

- Automatic Bluetooth pairing and connection
- Real-time message reception from Android devices
- Multiple broadcasting options (audio, display, log)
- Auto-start on boot via systemd service
- Comprehensive logging and error handling
- Easy configuration management

## Quick Start

1. Flash Ubuntu Desktop 22.04 to SD card
2. Boot Pi and run initial setup: `chmod +x setup/initial_setup.sh && ./setup/initial_setup.sh`
3. Pair your Android device
4. Install and start the service: `chmod +x services/install_service.sh && sudo ./services/install_service.sh`
5. Send messages from Android using Bluetooth Terminal app

## Supported Broadcasting Methods

- **Audio**: Text-to-speech using espeak
- **Display**: GUI notifications and console output
- **Logging**: Persistent message logging with timestamps

## Requirements

- Raspberry Pi 4
- Ubuntu Desktop 22.04 LTS
- Android device with Bluetooth
- Internet connection for initial setup

See individual files for detailed usage instructions.
