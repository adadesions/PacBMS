import serial
import serial.rs485
import struct
from pymodbus.client.sync import ModbusSerialClient
from lab_firestore import send_to_firestore


def interprete_temp(temp_x):
    return format(temp_x*4/85, '.2f')


def interprete_current(current_x):
    dec_I = int(current_x, 16)
    check_len = len(str(dec_I))

    charging_status =  'Charging' if str(dec_I)[0] == '0' else 'Discharge'
    try:
        I = format(int(str(dec_I)[1:])/490, '.2f')
    except ValueError:
        I = 0

    return (I, charging_status)


def ada_interpreter(buffer):
    labels = ['CELL_NUM', 'RUN_TIME', 'HSOC', 'VOLTAGE', 'CURCADC', 'TEMP1', 'TEMP2', 'TEMP3', 'TEMP4', 'TEMP5', 'TEMP6',
    'T_MAX', 'T_MIN', 'V_MAX', 'V_MIN', 'VMAX_VMIN_NO', 'RSOC', 'FCC', 'RC', 'CYCLE_COUNT', 'PROTECT', 'ALARM', 'PACK_STATUS',
    'V_CELL1', 'V_CELL2', 'V_CELL3', 'V_CELL4', 'V_CELL5', 'V_CELL6', 'V_CELL7', 'V_CELL8', 'V_CELL9', 'V_CELL10', 'V_CELL11', 'V_CELL12', 'V_CELL13', 'V_CELL14', 'V_CELL15', 'V_CELL16', 'V_CELL17', 'V_CELL18', 'V_CELL19', 'V_CELL20', 'V_CELL21', 'V_CELL22', 'V_CELL23', 'V_CELL24', 'V_CELL25', 'V_CELL26', 'V_CELL27', 'V_CELL28', 'V_CELL29', 'V_CELL30', 'V_CELL31', 'V_CELL32']
    semantic_data = dict()
    sep = 4
    no_head = buffer[6:]
    d_len = len(no_head)//sep
    sep_data = [no_head[i*sep:sep*(i+1)] for i in range(d_len)]

    for (i, data) in enumerate(sep_data):
        try:
            if 'CURCADC' in labels[i]:
                current = interprete_current(data)
                semantic_data[labels[i]] = current[0]
                semantic_data['CHARGING_STATUS'] = current[1]
                continue

            semantic_data[labels[i]] = int(data, 16)

            if 'V_' in labels[i]:
                semantic_data[labels[i]] = format(semantic_data[labels[i]]*0.01, '.2f')
            if 'TEMP' in labels[i]:
                semantic_data[labels[i]] = interprete_temp(semantic_data[labels[i]])
        except IndexError:
            continue

    semantic_data['VOLTAGE'] = format(semantic_data['VOLTAGE']*0.01, '.2f')
    semantic_data['T_MAX'] = interprete_temp(semantic_data['T_MAX'])
    semantic_data['T_MIN'] = interprete_temp(semantic_data['T_MIN'])
    semantic_data['FCC'] = semantic_data['FCC']*0.01
    semantic_data['RC'] = semantic_data['RC']*0.01

    return semantic_data


if __name__ == "__main__":
    serial_init = {
        "port": "COM5",
        "baudrate": "9600",
        "parity": serial.PARITY_NONE,
        "stopbits": serial.STOPBITS_ONE,
        "bytesize": serial.EIGHTBITS
    }
    HEAD_PROTOCOL = '01036e'

    command = b'\x01\x03\x10\x00\x00\x37\x00\xdc'
    wakeup_code = b'\x01\x03\x00\x00\x00\x0a\xc5\xcd'
    # command = b'01 03 10 00 00 37 00 DC'
    ser485 = serial.rs485.RS485(port=serial_init["port"], baudrate=serial_init["baudrate"], timeout=3.0)
    ser485.rs485_mode = serial.rs485.RS485Settings(True, False)

    if ser485.is_open:
        print("Port opened")
    else:
        ser485.open()

    counter = 0
    isWake = False

    while True:
        buffer = ''

        ser485.write(command)
        response = ser485.readline()

        if not response:
            ser485.timeout = 0.1
            ser485.write(wakeup_code)
            print('===== SENT WAKEUP CODE =====')
            if ser485.readline():
                isWake = True
                ser485.timeout = 3.0 
                print('BMS WOKE UP, Try again!!!')
            continue

        hex_data = response.hex()

        if HEAD_PROTOCOL == '01036e':
            buffer = hex_data
            ser485.write(command)
            next_line = ser485.readline()
            buffer = ''.join([buffer, next_line.hex()])


            print(buffer)

            semantic_data = ada_interpreter(buffer)

            if semantic_data['CELL_NUM'] < 32:
                print('===== RX-000{} ====='.format(counter))
                print(semantic_data)
                send_to_firestore(semantic_data)
                counter += 1
