#!/usr/bin/env python
# coding=utf-8

import socket
import sys

HOST, PORT = "localhost", 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

while 1:
    data = raw_input('> ')
    sock.send(data + '\n')
    reply = sock.recv(1024)
    print reply,
    if reply.startswith('600'):
        sys.exit(1)
