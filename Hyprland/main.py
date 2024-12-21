import bluetooth
import os
import time
import math

movment_factor = 2

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
        print(data)
        values = data.replace("\r", "").split(",")  # Clean and split values
        print(len(values))
        if len(values) != 4: # Check for unexpected data length or data loss
            print("Invalid data received")
            return "Error"
        return values
    except KeyboardInterrupt:
        print("Exiting...")
        return "Error"
    except bluetooth.btcommon.BluetoothError as e:
        print(f"Bluetooth error: {e}")
        # return None, None, None
        sock = connect_bluetooth(mac_address)
        return receive_data(sock)

def handle_mouse_data(values):
    # Clean up values to handle unexpected characters
    values = [v.strip() for v in values]
    values = list(map(float, values)) 
    print(values)

    for i in range(len(values)):
        if abs(values[i]) < 3:
            values[i] = 0
        else:
            values[i] = round(values[i] * movment_factor)
    # print(values)
    
    current_cursor_position = os.popen("hyprctl cursorpos").read().strip().split(",")
    x, y = int(current_cursor_position[0]), int(current_cursor_position[1])
    
    print(x, y)
    x -= values[2]
    y += values[1]
    os.system(f"hyprctl dispatch movecursor {x} {y}")

if __name__ == "__main__":
    mac_address = "F8:B3:B7:34:51:56"
    sock = connect_bluetooth(mac_address)
    try:
        while True:
            data = receive_data(sock)
            print(data)
            id = data[0]
            values =  data[1:]

            if id == "0":
                handle_mouse_data(values)

            time.sleep(0.001)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        sock.close()
