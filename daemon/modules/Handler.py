#!/usr/bin/env python
# coding=utf-8

import sys
import socket
import SocketServer

from modules.Parser import parse
from common.Exceptions import *

class Handler(SocketServer.StreamRequestHandler):       
    def handle(self):
        print >> sys.stderr, "[%s] Handling connection" % self.client_address[0]
        parent = None
        parent_id = None
        
        from modules.Daemon import Daemon
        manager = Daemon.get_manager()
        
        types_and_actions = {
            'test'        : manager.create_test,
            'test_check'  : manager.add_check_command,
            'test_setup'  : manager.add_setup_command,
            'test_task'   : manager.add_task_command,
            'test_clean'  : manager.add_clean_command,
            'test_file'   : manager.add_file,
            'test_delete' : manager.delete_command_or_file,
            'results'     : manager.open_results,
            'results_get' : manager.get_results,
            'delete'      : manager.delete_test,
            'prepare'     : manager.prepare_test,
            'start'       : manager.start_test,
            'stop'        : manager.stop_test
        }

        try:
            while 1:
                line = self.receive()
                if line == '':
                    raise socket.error
                try:
                    type, params = parse(line, parent)
                    if types_and_actions.get(type):
                        result = types_and_actions.get(type)(parent_id, **params)
                except DaemonError as de:
                    print >> sys.stderr, de
                    if isinstance(de, CheckError):
                        self.send_check_error()
                    else:
                        self.send_bad_request()
                else:
                    if type in ['test', 'results']:
                        parent = type
                        parent_id = params['id']
                    if type.endswith('end'):
                        parent = None
                        parent_id = None
                    if type == 'test_file':
                        path = result[0]
                        size = result[1]
                        with open(path, 'wb') as f:
                            f.write(self.request.recv(size))
                    if type == 'results_get':
                        output = result
                        self.send_ok(size=len(output))
                        self.wfile.write(output)
                    else:
                        self.send_ok()
        except socket.error, IOError:
            print >> sys.stderr, "[%s] Connection dropped" % self.client_address[0]

    def receive(self):
        data = self.rfile.readline().strip()
        if data:
            print >> sys.stderr, "[%s] Received: %s" % (self.client_address[0], data)
        return data

    def send(self, msg):
        print >> sys.stderr, "[%s] Sending: %s" % (self.client_address[0], msg)
        self.wfile.write(msg + '\n')

    def send_ok(self, size=None):
        msg = '200 OK'
        if size:
            msg += ' %d' % size
        self.send(msg)

    def send_bad_request(self):
        self.send('400 Bad Request')

    def send_check_error(self):
        self.send('401 Check Error')

    # TODO: send this if test end policy is set to 'complete' and scheduler has executed all tasks
    def send_test_finished(self):
        self.send('100 Test Finished')

    def send_end(self):
        self.send('600 The End')

