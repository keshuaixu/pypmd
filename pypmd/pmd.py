import logging

import bitstring

from pypmd.tcp_transport import TCPTransport
from pypmd.op_codes import *


class PMD:
    def __init__(self, interface='tcp', **kwargs):
        transport_interfaces = {'tcp': TCPTransport}
        self.transport = transport_interfaces[interface](**kwargs)

    def send_command(self, axis=0, op_code=None, payload=(), payload_format='', return_format=None):
        payload_bits = bitstring.pack(payload_format, *payload)
        payload_bits.byteswap(2)
        command = bitstring.pack('0x62, 0x40, uint:8, uint:4, uint:4, bits', op_code, mystery_code[op_code], axis, payload_bits)
        self.transport.send(command.bytes)
        result = self.transport.receive()
        print(len(result))
        if len(result) < 4:
            logging.error('PMD is not responding')
        # if result[3] != 0x40:
        #     TODO: handle non normal status code
        if return_format:
            result_bits = bitstring.BitArray(result)
            result_bits.byteswap(2)
            return result_bits[4:].unpack(return_format)


if __name__ == '__main__':
    pmd = PMD(interface='tcp', host='192.168.1.41')
    result = pmd.send_command(axis=3, op_code=0x10, payload=(0x11223344,), payload_format='uint:32')
    result = pmd.send_command(axis=3, op_code=PMDOPGetPosition[0], return_format='uint:32')
    # print(result)
