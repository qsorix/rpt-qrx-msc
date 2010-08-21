#!/usr/bin/env python
# coding=utf-8

import sys
import socket

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print >>sys.stderr, "Usage: {0} <ip> <port> <file> <destname>".format(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
    destname = sys.argv[4]

    file = open(filename, 'r')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    sock.send(destname+'\n')
    sock.sendall(file.read())

    sock.close()
    file.close()

    print 'transfer done'
