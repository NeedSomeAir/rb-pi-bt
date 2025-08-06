# Android Bluetooth Sender Guide

This guide explains how to send messages from your Android device to the Raspberry Pi Bluetooth receiver.

## Method 1: Using Bluetooth Terminal Apps

### Recommended Apps:

1. **Serial Bluetooth Terminal** (by Kai Morich)
2. **Bluetooth Terminal** (by pyrus.apps)
3. **BlueTerm** (by pyrus.apps)

### Setup Instructions:

#### 1. Install a Bluetooth Terminal App

- Download "Serial Bluetooth Terminal" from Google Play Store
- This is the most reliable and user-friendly option

#### 2. Pair with Raspberry Pi

1. Enable Bluetooth on your Android device
2. Go to Settings → Connected devices → Bluetooth
3. Search for new devices
4. Look for "Pi-Bluetooth-Receiver" in the list
5. Tap to pair
6. Accept any pairing requests

#### 3. Connect via Terminal App

1. Open Serial Bluetooth Terminal app
2. Tap the "Devices" menu (usually in top-right)
3. Select "Pi-Bluetooth-Receiver" from paired devices
4. Tap "Connect"
5. You should see "Connected" status

#### 4. Send Messages

1. Type your message in the text field
2. Press "Send" or the send button
3. Your message will be broadcast on the Pi through:
   - Audio (text-to-speech)
   - Desktop notification
   - Console output
   - Log file

## Method 2: Using Custom Android App

### Simple Bluetooth Sender Code (Java/Kotlin)

```java
// Basic Android Bluetooth sender (add to your Android project)
public class BluetoothSender {
    private BluetoothAdapter bluetoothAdapter;
    private BluetoothSocket socket;
    private static final String PI_MAC_ADDRESS = "YOUR_PI_MAC_ADDRESS";
    private static final UUID SPP_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");

    public void connectToPi() {
        try {
            BluetoothDevice device = bluetoothAdapter.getRemoteDevice(PI_MAC_ADDRESS);
            socket = device.createRfcommSocketToServiceRecord(SPP_UUID);
            socket.connect();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void sendMessage(String message) {
        try {
            if (socket != null && socket.isConnected()) {
                OutputStream outputStream = socket.getOutputStream();
                outputStream.write(message.getBytes());
                outputStream.flush();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void disconnect() {
        try {
            if (socket != null) {
                socket.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

## Method 3: Using ADB (For Testing)

If you have ADB debugging enabled:

```bash
# Send via ADB command
adb shell am start -a android.bluetooth.adapter.action.REQUEST_ENABLE
```

## Troubleshooting

### Connection Issues:

1. **Can't find Pi device:**

   - Ensure Pi Bluetooth is discoverable
   - Run on Pi: `bluetoothctl discoverable on`
   - Restart Bluetooth on both devices

2. **Pairing fails:**

   - Clear Bluetooth cache on Android
   - Remove device and re-pair
   - Check Pi logs: `journalctl -u bluetooth-receiver -f`

3. **Can't connect after pairing:**

   - Ensure the receiver service is running on Pi
   - Check service status: `sudo systemctl status bluetooth-receiver`
   - Try different Bluetooth terminal app

4. **Messages not received:**
   - Check Pi logs for errors
   - Verify service is listening on correct port
   - Test with simple message first

### Android Permissions:

Make sure your Android app has these permissions in AndroidManifest.xml:

```xml
<uses-permission android:name="android.permission.BLUETOOTH" />
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
```

For Android 12+, also add:

```xml
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
<uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
```

## Testing Messages

### Test Messages to Try:

1. "Hello from Android"
2. "Testing audio broadcast"
3. "This is a longer message to test the text-to-speech functionality"
4. "Emoji test: 😀🔵📱"

### Expected Behavior:

- Message appears on Pi console immediately
- TTS speaks the message aloud
- Desktop notification shows (if GUI available)
- Message logged to file with timestamp

## Pi Bluetooth Address

To find your Pi's Bluetooth address:

```bash
bluetoothctl show
# or
hciconfig hci0
```

Use this address in your custom Android apps.

## Advanced Features

### Message Commands:

You can send special commands to control the Pi:

- `!status` - Get system status
- `!volume 50` - Set volume to 50%
- `!test` - Test all broadcasting methods

### Multiple Devices:

The Pi can accept connections from multiple Android devices, but handles them one at a time.

## Security Notes

- Only paired devices can send messages
- Messages are logged with sender information
- Consider implementing message filtering for production use
- The connection is not encrypted beyond Bluetooth's built-in security
