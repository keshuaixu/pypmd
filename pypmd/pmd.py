import logging
import pickle
import re
import json
from threading import Lock

import bitstring

from pypmd.tcp_transport import TCPTransport

import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'op_codes.pickle'), 'rb') as f:
    op_codes = pickle.load(f)

with open(os.path.join(__location__, 'err_codes.pickle'), 'rb') as f:
    err_codes = pickle.load(f)

with open(os.path.join(__location__, 'c_motion_functions.json'), 'r') as f:
    c_motion_functions = json.load(f)

axis_regex = re.compile(r'#(?:Axis) (\d)')


class PMDNoResponseException(Exception):
    pass


class PMDError(Exception):
    pass


def make_c_motion_function(params):
    def c_motion_function(self, axis=0, *payload):
        return self.send_command(axis, params['op_code'], payload, params['input_format'], params['output_format'])

    return c_motion_function


class PMD:
    def __init__(self, interface='tcp', **kwargs):
        self.transport_lock = Lock()
        transport_interfaces = {'tcp': TCPTransport}
        self.transport = transport_interfaces[interface](**kwargs)
        self.close = self.transport.close
        self.script_parser_axis = 0
        for name, params in c_motion_functions.items():
            setattr(PMD, name, make_c_motion_function(params))
        try:
            self.read_analogs()
        except bitstring.ReadError:
            pass

    def send_command(self, axis=0, op_code=None, payload=(), payload_format='', return_format=None):
        try:
            if isinstance(op_code, str):
                op_code = op_codes[op_code]
        except KeyError:
            logging.exception(f'cannot find op code: {op_code}')
            raise

        payload_bits = bitstring.pack(payload_format, *payload)
        payload_bits.byteswap(2)
        try:
            rx_length = sum(tuple(zip(*bitstring.tokenparser(return_format)[1]))[1]) // 16
        except (AttributeError, IndexError):
            rx_length = 0
            pass
        command = bitstring.pack('0x62, 0x40, uint:8, uint:2, uint:6, bits', op_code, rx_length, axis,
                                 payload_bits)
        with self.transport_lock:
            self.transport.send(command.bytes)
            logging.debug(f'sent {command.bytes.hex()}')
            result = self.transport.receive()
            logging.debug(f'received {result.hex()}')
        if len(result) < 4:
            logging.error('PMD is not responding')
            raise PMDNoResponseException()
        err_code = (result[3] & 0b00110000) >> 4 != 0x00
        if err_code not in (0x00, 0x01):
            logging.error(f'PMD responded with error: {err_codes[err_code]}')
            raise PMDError()
        if return_format:
            result_bits = bitstring.BitArray(result)
            result_bits.byteswap(2)
            return result_bits[32:].unpack(return_format)

    def parse_script_line(self, line: str, ignore_unknown_command=True):
        axis_match = axis_regex.match(line)
        split_line = line.strip().split()
        function_name = split_line[0]
        args = split_line[1:]
        if axis_match:
            self.script_parser_axis = int(axis_match.group(1))
        else:
            logging.debug(
                f'parsing {line.strip()}. command {function_name}. axis {self.script_parser_axis}. args {args}')
            try:
                return getattr(self, function_name)(self.script_parser_axis, *map(lambda x: int(x, 0), args))
            except AttributeError:
                if ignore_unknown_command:
                    logging.warning(
                        f'ignored line {line} in script because function {function_name} does not exist in PMD class')
                else:
                    logging.exception(f'unable to find function {function_name}')
                    raise

    def parse_script(self, file):
        with open(file, 'r') as f:
            lines = f.readlines()
            [self.parse_script_line(line) for line in lines]

    def SetCurrentLoop(self, axis, selector, value):
        return self.send_command(axis, op_codes['SetCurrentLoop'], (selector, value), payload_format='int:16, int:16')

    def read_analogs(self, unit='v'):
        command = 0x68_80_02_00_40_03_00_00_08_00_00_00.to_bytes(12, 'big')
        with self.transport_lock:
            self.transport.send(command)
            result = self.transport.receive()
        logging.debug(f'received {result.hex()}')
        if len(result) < 4:
            logging.error('PMD is not responding')
            raise PMDNoResponseException()
        err_code = (result[3] & 0b00110000) >> 4 != 0x00
        if err_code not in (0x00, 0x01):
            logging.error(f'PMD responded with error: {err_codes[err_code]}')
            raise PMDError()
        result_bits = bitstring.BitArray(result)
        result_adc_count = result_bits[32:].unpack('<8h')
        if unit == 'count':
            return result_adc_count
        elif unit == 'v':
            return [x * 10 / 32767 for x in result_adc_count]

    def read_encoder_position(self, axis):
        return self.GetActualPosition(axis)[0]

    def read_encoder_velocity(self, axis):
        return self.GetActualVelocity(axis)[0]

    def set_motor_current(self, axis, current, full_scale_current=1.5):
        current_command = 1310 * current
        return self.SetMotorCommand(axis, int(current_command))

    def read_motor_current(self, axis, full_scale_current=1.5):
        result = self.send_command(axis, 'GetCurrentLoopValue', payload=(0x00, 0x01), payload_format='int:8, int:8',
                                   return_format='int:32')[0]
        current = result / (2 ** 14) * full_scale_current
        return current

    def set_operating_mode(self, axis, axis_enabled=False, motor_output_enabled=False, current_control_enabled=False,
                           position_loop_enabled=False, trajectory_enabled=False):
        mode = axis_enabled << 0 | motor_output_enabled << 1 | current_control_enabled << 2 \
               | position_loop_enabled << 4 | trajectory_enabled << 5
        return self.SetOperatingMode(axis, mode)

    def multi_update(self, mask=0b1111):
        self.MultiUpdate(0, mask)
