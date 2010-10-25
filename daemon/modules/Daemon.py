#!/usr/bin/env python
# coding=utf-8

import os
import SocketServer
import logging
from threading import Thread

from database.Models import *
from modules.Manager import Manager

class Daemon:
    manager = Manager()

    def __init__(self, port, database, log, verbose):
        self._setup_database(database)
        if not os.path.isdir("./tmp"):
            os.mkdir("./tmp")
        logging.basicConfig(filename=log, level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
        if verbose:
            logger = logging.getLogger()
            logger.addHandler(logging.StreamHandler())
        
        from modules.Handler import Handler
        SocketServer.TCPServer.allow_reuse_address = True
        self.tcp_server = SocketServer.TCPServer(('localhost', port), Handler)

        from modules.Poker import Pokeler
        self.manager.poker_port = port*10+1
        self.poke_server = SocketServer.TCPServer(('localhost', self.manager.poker_port), Pokeler)

    def _setup_database(self, database):
        metadata.bind = 'sqlite:///' + database
        setup_all()
        create_all()
    
    def run(self):
        logging.info('[ Arete Slave ] Started @ %s:%d' % (self.tcp_server.server_address[0], self.tcp_server.server_address[1]))
        try:
            poke_thread = Thread(target=self.poke_server.serve_forever)
            poke_thread.setDaemon(True)
            poke_thread.start()

            self.tcp_server.serve_forever()
        except KeyboardInterrupt:
            self.tcp_server.shutdown()
            self.poke_server.shutdown()

            # FIXME Not seem to work...
            for scheduler in self.manager.schedulers.values():
                for event in scheduler.task_scheduler.queue:
                    scheduler.task_scheduler.cancel(event)
                for id in scheduler.task_threads.keys():
                    if scheduler.task_threads[id].is_alive():
                        if scheduler.pids.has_key(id):
                            os.kill(scheduler.pids[id], signal.SIGKILL)
            for id in self.manager.schedulers.keys():
                try:
                    self.manager.clean_test(id)
                except Exception:
                    pass
            logging.info('[ Arete Slave ] Ended')
    
    @classmethod
    def get_manager(cls):
        return cls.manager
    
