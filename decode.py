def decodeBMS(byte_data):
    # encode = str(b"\x01\x03n\x00\x10\x00\x00\x00c\x14a'\x10\x02\xe9\x02\xee\x03\x15\x00\x00\x00\x00\x00\x00\x03\x15\x02\xe9\x13\xff\x06")
    splited_data = byte_data.split('\\x')
    my_hex = splited_data[1:]
    print(my_hex)
    for code in my_hex:
        if len(code) > 2:
            code = code.replace("'", "")[:-1]
        hex2int = int(code, 16)
        print(hex2int)