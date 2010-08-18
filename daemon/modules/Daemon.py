#!/usr/bin/env python
# coding=utf-8

import sys
import os
import errno
import ConfigParser
import SocketServer

from database.Models import *
from modules.Manager import Manager

class Daemon:
    manager = Manager()
        
    def __init__(self, port=4567, database='aretes.db', config='aretes.cfg'):
        self.config_filename = config
        self.database_filename = database
        self._setup_database(database)
        self._setup_config(config)
        
        from modules.Handler import Handler
        SocketServer.TCPServer.allow_reuse_address = True
        self.tcp_server = SocketServer.TCPServer(('localhost', port), Handler)

    def _setup_database(self, database):
        metadata.bind = 'sqlite:///' + database
        setup_all()
        create_all()
    
    def _setup_config(self, config):
        config = ConfigParser.SafeConfigParser()
        config.read(str(config))
    
        # Default settings:
        TMPDIR = './tmp'
    
        try:
            tmpdir = config.get('AreteS', 'tmpdir')
        except ConfigParser.NoSectionError:
            config.add_section('AreteS')
            config.set('AreteS', 'tmpdir', TMPDIR)
            with open(str(config), 'wb') as f:
                config.write(f)
        finally:
            try:
                os.makedirs(TMPDIR)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    pass
                else:
                    raise
    
    def run(self):
        self.tcp_server.serve_forever()
    
    @classmethod
    def get_manager(self):
        return self.manager