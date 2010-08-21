#!/usr/bin/env python
# coding=utf-8

import socket
import sys
from time import sleep

HOST, PORT = "localhost", 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

def send_sth(text):
	sock.send(text)
	data = sock.recv(1024)
	print data
	if data.startswith('400'): sys.exit(1)

send_sth('test 234\n')
send_sth('schedule 2')
send_sth('0: {iperf-server} iperf -u -s')
send_sth('5: kill {iperf-server}')
send_sth('cmds 3')
send_sth('0: uname -a')
send_sth('0: date')
send_sth('0: iperf -v')
send_sth('duration 10')
send_sth('start 2010-01-19 01:13:03')
send_sth('end')

sock.close()
