import serial, os, math
from time import sleep

PORT = '/dev/ttyUSB0'
FILE = '../app/firmware.bin'

REQ_ENTER = [0xde, 0xad, 0xbe, 0xef]
ACK  = [0xaa, 0xbb]
NACK = [0xde, 0xad]
BLOCK_SIZE = 64

def crc8_update(data, crc):
    crc ^= data
    for i in xrange(8):
        if crc & 0x80 != 0:
            crc = (crc << 1) ^ 0x07
        else:
            crc <<= 1
    return crc & 0xFF

def get_crc():
    crc = 0
    data = open(FILE, 'rb')
    with data as f:
        chunk = bytearray(f.read(BLOCK_SIZE))
        while chunk:
            chunk.extend([0xFF] * (BLOCK_SIZE - len(chunk)))
            for i in chunk:
                crc = crc8_update(i, crc)
            chunk = bytearray(f.read(BLOCK_SIZE))
    return crc

def bootloader_enter(ser):
    req = bytearray(REQ_ENTER)
    chunks = os.path.getsize(FILE)
    chunks = int(math.ceil(float(chunks) / BLOCK_SIZE))
    print 'Need to send', chunks, 'chunks'
    crc = get_crc()
    req.extend([chunks, crc, crc])
    ser.write(req)
    ser.flushOutput()
    return ser

def bootloader_write():
    ser = serial.Serial(PORT, 115200, timeout=1.0)
    bootloader_enter(ser)
    data = open(FILE, 'rb')
    total = 0
    with data as f:
        chunk = bytearray(f.read(BLOCK_SIZE))
        while chunk:
            rx = ser.read(2)
            if len(rx) != 2:
                print 'Timeout'
                return
            total += len(chunk)
            print total
            chunk.extend([0xFF] * (BLOCK_SIZE - len(chunk)))
            ser.write(chunk)
            ser.flushOutput()
            chunk = bytearray(f.read(BLOCK_SIZE))
        ack = ser.read(2)
        if ack == bytearray(NACK):
            print 'CRC mismatch'
            return
        print 'Done'
    ser.close()

if __name__ == "__main__":
    bootloader_write()
