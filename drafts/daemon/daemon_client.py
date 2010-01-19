#!/usr/bin/env python

import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', int(sys.argv[1])))

def send_sth(text):
	s.send(text)
	data = s.recv(1024)
	print data
	if data.startswith('400'): sys.exit(1)


send_sth('test 235')
send_sth('schedule 2')
send_sth('0: echo "dupa"')
send_sth('5: ls -l')
send_sth('duration 6')
send_sth('start 2010-01-19 01:13:03')
send_sth('end')

s.close()
