import bitstring
from pypmd.tcp_transport import TCPTransport

class PMD:
    def __init__(self, interface='tcp', **kwargs):
        transport_interfaces = {'tcp': TCPTransport}
        self.transport = transport_interfaces[interface](**kwargs)

    def send_command(self, axis=0, op_code=None, payload=(), payload_format='', return_format=None):
        payload_bits = bitstring.pack(payload_format, *payload)
        payload_bits.byteswap(2)
        command = bitstring.pack('0x62, 0x40, uint:8, uint:4, uint:4, bits', op_code, 0b1000,axis, payload_bits)
        self.transport.send(command.bytes)
        if return_format:
            result = self.transport.receive()
            result_bits = bitstring.BitArray(result)
            result_bits.byteswap(2)
            return result_bits.unpack(return_format)


if __name__ == '__main__':
    pmd = PMD(interface='tcp', host='192.168.1.41')
    result = pmd.send_command(axis=2, op_code=0x4c, return_format='int:32')
    print(result)
