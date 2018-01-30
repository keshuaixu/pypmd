import logging
import unittest
from unittest.mock import patch, Mock, MagicMock

import time

from pypmd import PMD

host = '192.168.1.41'


class TestPMD(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        time.sleep(0.1)

    def test_write_read(self):
        pmd = PMD(interface='tcp', host=host)
        pmd.send_command(axis=3, op_code=0x10, payload=(0x11111111,), payload_format='uint:32')
        pmd.send_command(axis=3, op_code=0x10, payload=(0x11223344,), payload_format='uint:32')
        result = pmd.send_command(axis=3, op_code=0x4a, return_format='int:32')
        self.assertEqual(result[0], 0x11223344)
        pmd.close()

    def test_op_code(self):
        logging.basicConfig(level=logging.DEBUG)
        pmd = PMD(interface='tcp', host=host)
        pmd.send_command(axis=3, op_code='SetPosition', payload=(0x11111111,), payload_format='uint:32')
        pmd.send_command(axis=3, op_code='SetPosition', payload=(0x11223344,), payload_format='uint:32')
        result = pmd.send_command(axis=3, op_code='GetPosition', return_format='int:32')
        self.assertEqual(result[0], 0x11223344)
        pmd.close()

    def test_c_motion_basic(self):
        logging.basicConfig(level=logging.DEBUG)
        pmd = PMD(interface='tcp', host=host)
        pmd.SetPosition(3, 0x11223344)
        result = pmd.GetPosition(3)
        pmd.Update()
        self.assertEqual(result[0], 0x11223344)
        pmd.close()

    @patch('socket.socket')
    @patch('pypmd.pmd.PMD.send_command')
    def test_c_motion_mocked(self, mock_send_command, mock_socket):
        logging.basicConfig(level=logging.DEBUG)
        pmd = PMD(interface='tcp', host=host)
        with open('c_motion_script.txt', 'r') as f:
            lines = f.readlines()
            list(map(pmd.parse_script_line, lines))
        print(mock_send_command.mock_calls)
        pmd.close()
        # self.assertEqual(True, True)

    def test_c_motion_parse(self):
        logging.basicConfig(level=logging.DEBUG)
        pmd = PMD(interface='tcp', host=host)
        with open('c_motion_script.txt', 'r') as f:
            lines = f.readlines()
            list(map(pmd.parse_script_line, lines))
        pmd.close()

    def test_c_motion_loopback(self):
        logging.basicConfig(level=logging.DEBUG)
        pmd = PMD(interface='tcp', host=host)
        lines = '#Axis 2', 'SetPosition -332211'
        list(map(pmd.parse_script_line, lines))
        result = pmd.GetPosition(2)
        self.assertEqual(result[0], -332211)
        pmd.close()


if __name__ == '__main__':
    unittest.main()
