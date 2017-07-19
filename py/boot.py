import serial, os, math
from time import sleep
from binascii import crc_hqx

PORT = '/dev/ttyUSB0'

REQ_ENTER = bytearray([0xde, 0xad, 0xbe, 0xef])
CHUNK_SIZE = 64

def fl_open():
    chunks = os.path.getsize('firmware.bin')
    chunks = int(math.ceil(float(chunks) / CHUNK_SIZE))
    print 'Need to send', chunks, 'chunks'
    REQ_ENTER.append(chunks)

    ser = serial.Serial(PORT, 115200, timeout=1.0)
    ser.write(REQ_ENTER)
    ser.flushOutput()
    return ser

def bootloader_write():
    ser = fl_open()
    data = open('firmware.bin', 'rb')

    total = 0
    with data as f:
        chunk = bytearray(f.read(CHUNK_SIZE))
        while chunk:
            rx = ser.read(2)
            total += len(chunk)
            print total
            chunk.extend([0xFF] * (CHUNK_SIZE - len(chunk)))
            ser.write(chunk)
            ser.flushOutput()
            chunk = bytearray(f.read(CHUNK_SIZE))

bootloader_write()
print 'Done'
