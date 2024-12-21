import bluetooth
import os
import time
import math

movment_factor = 1

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
        print(f"Bluetooth error: {e}")
        print("Disconnecting from ESP32...")
        disconnect_bluetooth(mac_address)
        print("Reconnecting to ESP32...")
        connect_bluetooth(mac_address)


def receive_data(sock):
    try:
        data = sock.recv(1024).decode("utf-8").strip()
        print(data)
        # extract the values from the received data
        values = data.split(",")
        print(len(values))
        if len(values) != 4:
            print("Invalid data received")
            return "Error"
        return values

    except KeyboardInterrupt:
        print("Exiting...")
        return None, None, None
    except bluetooth.btcommon.BluetoothError as e:
        print(f"Bluetooth error: {e}")
        return None, None, None

def handle_mouse_data():
    pass



if __name__ == "__main__":
    mac_address = "Your ESP32 Mac Address"
    sock = connect_bluetooth(mac_address)
    try:
        while True:
            data = receive_data(sock)
            print(data)

            time.sleep(0.001)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        sock.close()
