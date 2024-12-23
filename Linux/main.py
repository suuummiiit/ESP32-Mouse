import bluetooth
import os
import time
import math
import uinput

movment_factor = 1.5

# Create new virtual mouse device
device = uinput.Device([
    uinput.BTN_LEFT,
    uinput.BTN_RIGHT,
    uinput.REL_X,
    uinput.REL_Y,
])

def disconnect_bluetooth(mac_address):
    os.system(f"echo -e 'disconnect {mac_address}' | bluetoothctl")
    print(f"Disconnected from {mac_address}")

def connect_bluetooth(mac_address):
    try:
        server_mac_address = mac_address
        port = 1
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((server_mac_address, port))
        print("Connected to ESP32!")

        return sock
    except bluetooth.btcommon.BluetoothError as e:
        # Try to disconnect and reconnect
        print(f"Bluetooth error: {e}")
        print("Disconnecting from ESP32...")
        disconnect_bluetooth(mac_address)
        print("Connecting to ESP32...")
        time.sleep(3)
        sock = connect_bluetooth(mac_address)
        return sock

def receive_data(sock):
    try:
        data = sock.recv(1024).decode("utf-8").strip()
        # print(data)
        values = data.replace("\r", "").split(",")  # Clean and split values
        return values
    except KeyboardInterrupt:
        print("Exiting...")
        sock.close()
        exit()
    except bluetooth.btcommon.BluetoothError as e:
        print(f"Bluetooth error: {e}")
        # return None, None, None
        sock = connect_bluetooth(mac_address)
        return receive_data(sock)

def move_cursor(values):
    # Clean up values by stripping unwanted characters including newlines, spaces, etc.
    values = [v.strip() for v in values]  # Remove any leading/trailing whitespace and newlines
    values = list(map(lambda v: float(v.replace('\n', '').replace('\r', '')), values))  # Remove newlines and carriage returns

    for i in range(len(values)):
        if abs(values[i]) < 3:
            values[i] = 0
        else:
            values[i] = round(values[i] * movment_factor)

    # Use values for cursor movement
    x = -values[2]
    y = values[1]
    print(x, y)
    
    # Emit mouse movements
    device.emit(uinput.REL_X, x)
    device.emit(uinput.REL_Y, y)


if __name__ == "__main__":
    mac_address = "Enter your ESP32 MAC ADDRESS"
    sock = connect_bluetooth(mac_address)
    try:
        while True:
            data = receive_data(sock)            
            id = data[0]
            values =  data[1:]
            if id == "0":
                if len(values) != 3: # Check for unexpected data length or data loss
                    print("Invalid data received")
                    continue
                move_cursor(values)
            
            time.sleep(0.001)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        sock.close()
