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
        
    def __init__(self, host='localhost', port=4567, database='aretes.db', config='aretes.cfg'):
        self.config_filename = config
        self.database_filename = database
        self._setup_database()
#        self._setup_config()
        
        from modules.Handler import Handler
        SocketServer.TCPServer.allow_reuse_address = True
        self.tcp_server = SocketServer.TCPServer((host, port), Handler)

    def _setup_database(self):
        metadata.bind = 'sqlite:///' + self.database_filename
        setup_all()
        create_all()
    
    def _setup_config(self):
        config = ConfigParser.SafeConfigParser()
        config.read(self.config_filename)
    
        # Default settings:
        TMPDIR = './tmp'
        DBFILE = self.database_filename
    
        try:
            tmpdir = config.get('AreteS', 'tmpdir')
        except ConfigParser.NoSectionError:
            config.add_section('AreteS')
            config.set('AreteS', 'tmpdir', TMPDIR)
            config.set('AreteS', 'dbfile', DBFILE)
            with open(self.config_filename, 'wb') as f:
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
        print '[Arete Slave] Started @ %s:%d' % (self.tcp_server.server_address[0], self.tcp_server.server_address[1])
        try:
            self.tcp_server.serve_forever()
        except KeyboardInterrupt:
            print '\n[Arete Slave] Ended'
    
    @classmethod
    def get_manager(self):
        return self.manager        
        