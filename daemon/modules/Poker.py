#!/usr/bin/env python
# coding=utf-8

import socket
import SocketServer
import logging
import sys

class Poker:
    def poke(self, test_id, name, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        sock.connect(('localhost', port))
        _out = sock.makefile('w', 0)
        _out.write('poke %s:%s\n' % (test_id, name))
        sock.close()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        test_id = sys.argv[1]
        poke_name = sys.argv[2]
        port = sys.argv[3]
        poker = Poker()
        poker.poke(test_id, poke_name, int(port))
    else:
        print 'Poke FAILED'
        exit(1)

