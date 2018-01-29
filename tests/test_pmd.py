import logging
import unittest

from pypmd import PMD

host = '192.168.1.41'


class TestPMD(unittest.TestCase):
    def test_write_read(self):
        pmd = PMD(interface='tcp', host=host)
        pmd.send_command(axis=3, op_code=0x10, payload=(0x11111111,), payload_format='uint:32')
        pmd.send_command(axis=3, op_code=0x10, payload=(0x11223344,), payload_format='uint:32')
        result = pmd.send_command(axis=3, op_code=0x4a, return_format='uint:32')
        self.assertEqual(result[0], 0x11223344)
        pmd.close()

    def test_op_code(self):
        logging.basicConfig(level=logging.DEBUG)
        pmd = PMD(interface='tcp', host=host)
        pmd.send_command(axis=3, op_code='SetPosition', payload=(0x11111111,), payload_format='uint:32')
        pmd.send_command(axis=3, op_code='SetPosition', payload=(0x11223344,), payload_format='uint:32')
        result = pmd.send_command(axis=3, op_code='GetPosition', return_format='uint:32')
        self.assertEqual(result[0], 0x11223344)
        pmd.close()


if __name__ == '__main__':
    unittest.main()
