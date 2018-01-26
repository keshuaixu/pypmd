import logging
import pickle

import bitstring

from pypmd.tcp_transport import TCPTransport
from pypmd.op_codes import *

import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
mystery_code_path = os.path.join(__location__, 'mystery_code.pickle')

with open(mystery_code_path, 'rb') as f:
    mystery_code = pickle.load(f)


class PMD:
    def __init__(self, interface='tcp', **kwargs):
        transport_interfaces = {'tcp': TCPTransport}
        self.transport = transport_interfaces[interface](**kwargs)

    def send_command(self, axis=0, op_code=None, payload=(), payload_format='', return_format=None):
        payload_bits = bitstring.pack(payload_format, *payload)
        payload_bits.byteswap(2)
        command = bitstring.pack('0x62, 0x40, uint:8, uint:4, uint:4, bits', op_code, mystery_code[op_code], axis,
                                 payload_bits)
        self.transport.send(command.bytes)
        logging.debug(f'sent {command.bytes}')
        result = self.transport.receive()
        logging.debug(f'received {result}')
        if len(result) < 4:
            logging.error('PMD is not responding')
        # if result[3] != 0x40:
        #     TODO: handle non normal status code
        if return_format:
            result_bits = bitstring.BitArray(result)
            result_bits.byteswap(2)
            return result_bits[32:].unpack(return_format)
