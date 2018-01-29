import socket


class TCPTransport:
    def __init__(self, host: str, port: int = 40100, **kwargs):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.s.setblocking(False)
        self.s.connect((host, port))
        self.close = self.s.close

    def send(self, data: bytearray):
        self.s.sendall(data)

    def receive(self, length=64) -> bytearray:
        return self.s.recv(length)
