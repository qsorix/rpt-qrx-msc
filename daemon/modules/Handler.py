#!/usr/bin/env python
# coding=utf-8

import sys
import socket
import SocketServer
import logging
import thread

from modules.Parser import parse
from common.Exceptions import *

class Handler(SocketServer.StreamRequestHandler):       
    def handle(self):
        logging.info("[ Connection %s ] Handling" % self.client_address[0])
        parent = None
        parent_id = None
        
        from modules.Daemon import Daemon
        manager = Daemon.get_manager()
#        logging.basicConfig(filename=Daemon.get_logfile(), level=logging.DEBUG)
        
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
            'stop'        : manager.stop_test,
            'trigger'     : manager.run_trigger
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
                except (DaemonError, CommandError) as e:
                    logging.error(e)
                    if isinstance(e, CommandError):
                       self.send_cmd_error(e.cmd_id)
                    elif isinstance(e, SetupTooLongError):
                       self.send_setup_too_long()
                    else:
                        self.send_bad_request()
                    if type == 'start':
                        try:
                            manager.clean_test(params['id'])
                        except CommandError as ce:
                            logging.error(ce)
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
                        type = result[0]
                        to_send = result[1]
                        if type == 'multi':
                            number = to_send[0]
                            output_list = to_send[1]
                            size_list = [len(output) for output in output_list]
                            self.send_ok(sizes=size_list)
                            for output in output_list:
                                self.wfile.write(output)
                        elif type == 'list':
                            self.send_list(to_send)
                        else:
                            self.send_ok(sizes=[len(to_send)])
                            self.wfile.write(to_send)
                    else:
                        if type != 'trigger':
                            self.send_ok()
                        if type == 'start':
                            manager.register_handler(params['id'], self.send_100)
#                            thread.start_new_thread(manager.start_tasks, (parent_id, params['id'], params['run'], params['end']))
                            manager.start_tasks(parent_id, **params)
#                            if params['end'] == 'complete':
#                                self.send_test_finished()
        except socket.error, IOError:
            logging.info("[ Connection %s ] Dropped" % self.client_address[0])

    def receive(self):
        data = self.rfile.readline().strip()
        if data:
            logging.info("[ Connection %s ] Received: %s" % (self.client_address[0], data))
        return data

    def send(self, msg):
        logging.info("[ Connection %s ] Sending: %s" % (self.client_address[0], msg))
        self.wfile.write(msg + '\n')

    def notify(self, test_id, trigger):
        self.send('100 Notify ' + test_id + ' ' + trigger)

    def send_ok(self, sizes=None):
        msg = '200 OK'
        if sizes:
            for size in sizes:
                msg += ' %d' % size
        self.send(msg)
        
    def send_list(self, list):
        msg = '201 List'
        for e in list:
            msg += ' %s' % str(e)
        self.send(msg)

    def send_bad_request(self):
        self.send('400 Bad Request')

    def send_cmd_error(self, cmd_id):
        self.send('401 Command Failed: %s' % cmd_id)
        
    def send_setup_too_long(self):
        self.send('402 Setup Too Long')

    def send_test_finished(self):
        self.send('100 Test Finished')

    def send_100(self, test_id=None, trigger=None):
        if trigger and test_id:
            self.notify(test_id, trigger)
        else:
            self.send_test_finished()
