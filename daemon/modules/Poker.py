#!/usr/bin/env python
# coding=utf-8

import socket
import SocketServer
import logging
import sys

class Pokeler(SocketServer.StreamRequestHandler):
    def handle(self):
        line = self.rfile.readline().strip()

        line = unicode(line).split(':')
        test_id = line[0]
        poke_name = line[1]
        logging.info("[ Test %s ] Received poke: %s" % (test_id, poke_name))

        from modules.Daemon import Daemon
        manager = Daemon.get_manager()

        manager.run_poke(test_id, poke_name)

class Poker:
    def poke(self, test_id, name):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 91827))
        sock.send('%s:%s' % (test_id, name))
        sock.close()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        test_id = sys.argv[1]
        poke_name = sys.argv[2]
        poker = Poker()
        poker.poke(test_id, poke_name)
    else:
        print 'Poke FAILED'
        exit(1)

