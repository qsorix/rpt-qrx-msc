#!/usr/bin/env python
# coding=utf-8

import sys
import os
from datetime import datetime

from parser import *
from manager import *
from models import *
import utilz

class Handler:
    def __init__(self, conn):
        self.conn = conn

    def handle(self):
        parser = Parser()
        parent = None
        parent_id = None
        manager = Manager(self)
        types_and_actions = {
            'test'        : manager.create_test,
            'test_check'  : manager.add_check_command,
            'test_setup'  : manager.add_setup_command,
            'test_task'   : manager.add_task_command,
            'test_clean'  : manager.add_clean_command,
            'test_file'   : manager.add_file,
            'test_delete' : manager.delete_command,
            'results_get' : manager.get_results,
            'delete'      : manager.delete_test,
            'prepare'     : manager.prepare_test,
            'start'       : manager.start_test,
            'stop'        : manager.stop_test
        }

        while 1:
            line = self.receive()
            try:
                type, params = parser.parse(line, parent)
                if types_and_actions.get(type):
                    result = types_and_actions.get(type)(parent_id, params)
 
                if type.endswith('close'):
                    self.send_end()
                    break;
                if type in ['test', 'results']:
                    parent = type
                    parent_id = params['id']
                if type.endswith('test_end'):
                    parent = None
                    parent_id = None
                    
            except (LineError, ParentError, TypeError, ParamError, ValueError):
                self.send_bad_request()
            except (ManagerError):
                self.send_error()

    def receive(self):
        data = self.conn.rfile.readline().strip()
        if data:
            print >> sys.stderr, "[%s] Received: %s" % (self.conn.client_address[0], data)
        return data

    def send(self, msg):
        print >> sys.stderr, "[%s] Sending: %s" % (self.conn.client_address[0], msg)
        self.conn.wfile.write(msg + '\n')

    def send_ok(self):
        self.send('200 OK')

    def send_sending(self, size):
        self.send('201 Sending ' + str(size))

    def send_bad_request(self):
        self.send('400 Bad Request')

    def send_end(self):
        self.send('600 The End')

