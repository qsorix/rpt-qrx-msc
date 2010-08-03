#!/usr/bin/env python
# coding=utf-8

import sys
import os
import errno
import ConfigParser
import SocketServer

from modules.Handler import Handler
from daemon.Models import *

class DaemonHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        # TODO Only if not doing anything

        print >> sys.stderr, "[%s] Handling..." % self.client_address[0]
        handler = Handler(self)
        handler.handle()

def setup_database():
    metadata.bind = "sqlite:///daemon.db"
    #metadata.bind.echo = True
    #session.configure(autocommit=True)
    setup_all()
    create_all()

def setup_config():
    config = ConfigParser.SafeConfigParser()
    config.read('daemon.cfg')

    TMPDIR = './tmp'

    try:
        tmpdir = config.get('Daemon', 'tmpdir')
    except ConfigParser.NoSectionError:
        config.add_section('Daemon')
        config.set('Daemon', 'tmpdir', TMPDIR)
        with open('daemon.cfg', 'wb') as f:
            config.write(f)
    finally:
        try:
            os.makedirs(TMPDIR)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise