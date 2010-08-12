from controller.ConnectionPlugin import ConnectionPlugin

import socket

class TCPConnection(ConnectionPlugin):
    connection_type = 'tcp'
    needed_attributes = ['ip', 'connection_port' ]

    def __init__(self, host):
        self._ip = host.device['ip']
        self._port = host.device['connection_port']
        self._socket = None

    def connect(self):
        assert not self._socket

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._ip, int(self._port)))
        self._in  = self._socket.makefile('r', 0)
        self._out = self._socket.makefile('w', 0)

    def close(self):
        assert self._socket

        self._out.close()
        self._in.close()
        self._socket.close()

        self._socket = None
        self._out    = None
        self._in     = None

    def input(self):
        assert self._in
        return self._in

    def output(self):
        assert self._out
        return self._out

