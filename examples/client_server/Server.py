#!/usr/bin/env python
# coding=utf-8

import sys
import SocketServer

class FileTransferHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        input  = self.request.makefile('r', 0)
        filename = input.readline().strip()

        print 'received', filename

        with open(filename, 'w') as file:
            file.write(input.read())

        self.request.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >>sys.stderr, "Usage: {0} <ip> <port>".format(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    server = SocketServer.TCPServer((ip, port), FileTransferHandler)
    server.serve_forever()
