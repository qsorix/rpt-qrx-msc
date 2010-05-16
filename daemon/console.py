#!/usr/bin/env python
# coding=utf-8

import socket
import sys

HOST, PORT = "localhost", 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

while 1:
    data = raw_input('> ')
    if data == 'q' or data == 'quit' or data == 'exit':
        sock.close()
        sys.exit(0)
    elif data == 'help' or data == 'h':
        print 'help'
    else:
        sock.send(data + '\n')
        print sock.recv(1024),
