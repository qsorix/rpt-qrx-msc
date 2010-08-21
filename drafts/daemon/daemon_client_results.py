#!/usr/bin/env python
# coding=utf-8

import socket
import sys
from time import sleep

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', int(sys.argv[1])))

def send_sth(text):
	s.send(text)
	data = s.recv(1024)
	print data
	if data.startswith('400'): sys.exit(1)

send_sth('results 235')

print s.recv(1024)
print s.recv(1024)
print s.recv(1024)
print s.recv(1024)

s.close()
