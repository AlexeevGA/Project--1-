import serial.tools.list_ports

def list_serial_ports():
    """Lists available serial ports."""
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return

    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"{i+1}: {port.device} - {port.description}")

if __name__ == "__main__":
    list_serial_ports()