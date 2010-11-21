#!/usr/bin/env python
# coding=utf-8

import socket

class Poker:
    def poke(self, test_id, name, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        sock.connect(('localhost', port))
        _out = sock.makefile('w', 0)
        _out.write('poke %s:%s\n' % (test_id, name))
        sock.close()

