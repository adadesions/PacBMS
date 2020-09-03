import serial
import serial.rs485
from pymodbus.client.sync import ModbusSerialClient


def decodeBMS(byte_data):
    # encode = str(b"\x01\x03n\x00\x10\x00\x00\x00c\x14a'\x10\x02\xe9\x02\xee\x03\x15\x00\x00\x00\x00\x00\x00\x03\x15\x02\xe9\x13\xff\x06")
    data = str(byte_data)
    splited_data = data.split('\\x')
    my_hex = splited_data[1:]

    for code in my_hex:
        code = code.replace("'", "").replace("\\n", "").replace("\\t", "")
        if len(code) > 2:
            code = code[:-1]
        try:
            hex2int = int(code, 16)
        except ValueError:
            print("Can't convert:", code)
        print(hex2int, end="-")
    print()


if __name__ == "__main__":
    serial_init = {
        "port": "COM5",
        "baudrate": "9600",
        "parity": serial.PARITY_NONE,
        "stopbits": serial.STOPBITS_ONE,
        "bytesize": serial.EIGHTBITS
    }

    command = b'\x01\x03\x10\x00\x00\x37\x00\xDC'
    # command = b'01 03 10 00 00 37 00 DC'
    ser485 = serial.rs485.RS485(port=serial_init["port"], baudrate=serial_init["baudrate"], timeout=2.0)
    ser485.rs485_mode = serial.rs485.RS485Settings(True, True)
    ser485.write(command)

    if ser485.is_open:
        print("Port opened")
    else:
        ser485.open()

    while True:
        print("Reading:", end=" ")
        response = ser485.readline()
        print(response)
        decodeBMS(response)
        # try:
        #     decodeBMS(response)
        # except e:
        #     print('ERROR:', e)

        ser485.write(command)
