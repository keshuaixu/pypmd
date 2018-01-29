import logging
import pickle
import re

import bitstring

from pypmd.tcp_transport import TCPTransport

import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'mystery_code.pickle'), 'rb') as f:
    rx_length = pickle.load(f)

with open(os.path.join(__location__, 'op_codes.pickle'), 'rb') as f:
    op_codes = pickle.load(f)

with open(os.path.join(__location__, 'err_codes.pickle'), 'rb') as f:
    err_codes = pickle.load(f)


class PMDNoResponseException(Exception):
    pass


class PMDError(Exception):
    pass


class PMD:
    def __init__(self, interface='tcp', **kwargs):
        transport_interfaces = {'tcp': TCPTransport}
        self.transport = transport_interfaces[interface](**kwargs)
        self.close = self.transport.close

    def send_command(self, axis=0, op_code=None, payload=(), payload_format='', return_format=None):
        try:
            if isinstance(op_code, str):
                op_code = op_codes[op_code]
        except KeyError:
            logging.exception(f'cannot find op code: {op_code}')
            raise

        payload_bits = bitstring.pack(payload_format, *payload)
        payload_bits.byteswap(2)
        command = bitstring.pack('0x62, 0x40, uint:8, uint:2, uint:6, bits', op_code, rx_length[op_code], axis,
                                 payload_bits)
        self.transport.send(command.bytes)
        logging.debug(f'sent {command.bytes}')
        result = self.transport.receive()
        logging.debug(f'received {result}')
        if len(result) < 4:
            logging.error('PMD is not responding')
            raise PMDNoResponseException()
        err_code = (result[3] & 0b00110000) >> 4 != 0x00
        if err_code != 0x00:
            logging.error(f'PMD responded with error: {err_codes[err_code]}')
            raise PMDError()
        if return_format:
            result_bits = bitstring.BitArray(result)
            result_bits.byteswap(2)
            return result_bits[32:].unpack(return_format)

    def parse_script_line(self, line: str):
        axis_regex = re.compile(r'#(?:Axis) (\d)')
        axis_match = axis_regex.match(line)
        splitted_line = line.split(' ')

        if axis_match:
            self.script_parser_axis = axis_match.group(1)
        elif
            pass # fix me
