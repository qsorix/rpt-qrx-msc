from controller.ConnectionPlugin import ConnectionPlugin

import socket

class TCPConnection(ConnectionPlugin):
    connection_type = 'tcp'
    needed_attributes = ['ip', 'connection_port' ]

    def __init__(self, host):
        self._host = host
        ip = host.device['ip']
        port = host.device['connection_port']

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((ip, int(port)))
        self._in  = self._socket.makefile('r', 0)
        self._out = self._socket.makefile('w', 0)

    def close(self):
        self._out.close()
        self._in.close()
        self._socket.close()

    def input(self):
        return self._in

    def output(self):
        return self._out

