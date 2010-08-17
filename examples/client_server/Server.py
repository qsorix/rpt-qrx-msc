#!/usr/bin/env python

import sys
import SocketServer

class FileTransferHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        input  = self.request.makefile('r', 0)
        filename = input.readline().strip()
        print filename
        dest = open(filename, 'w')
        dest.write(input.read())
        self.request.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >>sys.stderr, "Usage: {0} <ip> <port>".format(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((ip, port), FileTransferHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
