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
    reply = sock.recv(1024).strip()
    if data == 'tasks' or data == 'cmds':
        for i in range(int(reply)):
            print sock.recv(1024).strip()
            print '...output...'
 #           line = sock.recv(1024)
    else:
        print reply
    if reply.startswith('40') or reply.startswith('60'):
        sock.close()
        sys.exit(1)
