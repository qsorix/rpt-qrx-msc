#!/usr/bin/env python

from daemon.connection import Conn
from threading import Thread
import sys
import socket

class Daemon:
	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind(('', int(sys.argv[1])))
		self.sock.listen(1)

		self.tests = {}

		while 1:
			c_sock, addr = self.sock.accept()
			conn = Conn(c_sock, addr, self)
			conn.start()

		self.sock.close()

daemon = Daemon()
