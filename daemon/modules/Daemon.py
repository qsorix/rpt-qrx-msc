#!/usr/bin/env python
# coding=utf-8

import os
import SocketServer
import logging

from database.Models import *
from modules.Manager import Manager

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class Daemon:
    manager = Manager()

    def __init__(self, port, database, log, verbose, ssh=False, authorized_keys=None, host_key=None):
        self._setup_database(database)

        #FIXME: tmp-path in arguments
        if not os.path.isdir("./tmp"): 
            os.mkdir("./tmp")
        logging.basicConfig(filename=log, level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
        if verbose:
            logger = logging.getLogger()
            logger.addHandler(logging.StreamHandler())
        
        from modules.Handler import Handler
        SocketServer.TCPServer.allow_reuse_address = True
        self.tcp_server = ThreadedTCPServer(('', port), Handler)
        self.tcp_server.daemon_threads = True
        self.tcp_server.use_ssh = ssh
        if ssh:
            self.tcp_server.authorized_keys = authorized_keys
            self.tcp_server.host_key = host_key

        self.manager.port = port

    def _setup_database(self, database):
        metadata.bind = 'sqlite:///' + database
        setup_all()
        create_all()
    
    def run(self):
        logging.info('[ Arete Slave ] Started @ %s:%d' % (self.tcp_server.server_address[0], self.tcp_server.server_address[1]))
        try:
            self.tcp_server.serve_forever()
        except KeyboardInterrupt:
            self.tcp_server.shutdown()

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
    
