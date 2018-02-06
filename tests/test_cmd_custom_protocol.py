import socket
import time
import unittest

import struct


class TestPMD(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        time.sleep(0.1)

    # def test_loopback(self):
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #         s.connect(('192.168.1.42', 18021))
    #         for i in range(10):
    #             s.sendall(b'helloworl' + f'{i}'.encode())
    #             print(s.recv(10))
    #
    # def test_byteorder(self):
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #         s.settimeout(1)
    #         s.connect(('192.168.1.42', 18021))
    #         s.sendall(b'helloworl' + '1'.encode())
    #         result = s.recv(8)
    #         unpacked = struct.unpack('<ll', result)
    #         print(unpacked)

    def test_protocol(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # s.settimeout(1)
            s.bind((' ', 18021))
            # s.bind((' ', 18021))

            while 1:
                result = s.recv(112)
                # print(result)
                try:
                    unpacked = struct.unpack('<4L12l12L', result)
                    print(unpacked)
                except struct.error:
                    print(result)


                send_fmt = '<L4l4L4l'
                send_vals = (0,) + (0,)*4 + (0b111,) *4 + (-0,) *4
                s.sendto(struct.pack(send_fmt, *send_vals), ('192.168.1.42', 18021))
                #
                # result = s.recv(128)
                # print(len(result))
                # unpacked = struct.unpack('<4L12l12L', result)
                # print(unpacked)


if __name__ == '__main__':
    unittest.main()