#!/usr/bin/env python
# coding=utf-8

import sys
import os
import SocketServer
import logging

from database.Models import *
from modules.Manager import Manager

class Daemon:
    manager = Manager()

    def __init__(self, port, database, log):
        self._setup_database(database)
        logging.basicConfig(filename=log, level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
        
        from modules.Handler import Handler
        SocketServer.TCPServer.allow_reuse_address = True
        self.tcp_server = SocketServer.TCPServer(('localhost', port), Handler)

    def _setup_database(self, database):
        metadata.bind = 'sqlite:///' + database
        setup_all()
        create_all()
    
    def run(self):
        logging.info('[ Arete Slave ] Started @ %s:%d' % (self.tcp_server.server_address[0], self.tcp_server.server_address[1]))
        try:
            self.tcp_server.serve_forever()
        except KeyboardInterrupt:
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
    