#!/usr/bin/env python
# coding=utf-8

import socket
import sys
import os

HOST, PORT = "localhost", 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

FILENAME = '/home/rpt/tmp/a.out'

def results():
    while 1:
        input = raw_input('> ')
    
        if input.startswith('task') or input.startswith('cmd') or input.startswith('file'):
            sock.send(input + '\n')
            reply = sock.recv(1024).strip()
            isittheend(reply)

            size = int(reply.split(' ')[2])

            tmp = ''
            received = 0
            while received < size:
                tmp += sock.recv(1024)
                received += 1024

            print tmp

        else:
            sock.send(input + '\n')
            reply = sock.recv(1024).strip()
            isittheend(reply)

def isittheend(reply):
    print reply
    if reply.startswith('60'):
        sock.close()
        sys.exit(1)

while 1:
    input = raw_input('> ')
    
    if input.startswith('file'):
        size = int(os.path.getsize(FILENAME))
        sock.send(input + ' @{size=' + str(size) + '}\n')
#        reply = sock.recv(1024).strip()
#        isittheend(reply)
        
        if reply.startswith('20'):
            with open(FILENAME, 'rb') as f:
                while size > 1024:
                    data = f.read(1024)
                    sock.send(data)
                    size -= 1024
                data = f.read(1024)
                sock.send(data)
            reply = sock.recv(1024).strip()
            isittheend(reply)

    elif input.startswith('results'):
        sock.send(input + '\n')
        reply = sock.recv(1024).strip()
        isittheend(reply)
        results()

    else:
        sock.send(input + '\n')
        reply = sock.recv(1024).strip()
        isittheend(reply)

