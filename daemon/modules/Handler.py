#!/usr/bin/env python
# coding=utf-8

import socket
import SocketServer
import logging
import datetime

try:
    import paramiko
    has_ssh_support = True
except:
    has_ssh_support = False

from modules.Parser import parse
from common.Exceptions import *

class SSHServer (paramiko.ServerInterface):
    def __init__(self, authorized_keys):
        self.authorized_keys = authorized_keys

    def check_auth_publickey(self, username, key):
        if key in self.authorized_keys:
            logging.info("[ SSH ] User %s authenticated using pubkey." % (username))
            return paramiko.AUTH_SUCCESSFUL

        logging.warn("[ SSH ] Pubkey authentication failed for %s" % (username))
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind=='session':
            logging.warn("[ SSH ] Opening channel %s" % (kind))
            return paramiko.OPEN_SUCCEEDED

        logging.warn("[ SSH ] Request for unknown channel kind %s" % (kind))
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return 'pubkey'

class Handler(SocketServer.StreamRequestHandler):
    def setup(self):
        if self.server.use_ssh:
            if not has_ssh_support:
                raise RuntimeError("Can't use SSH. Missing library paramiko.")

            transport = paramiko.Transport(self.request)
            transport.add_server_key(self.server.host_key)
            transport.start_server(server=SSHServer(self.server.authorized_keys))

            channel = transport.accept()
            if not channel:
                raise RuntimeError("Can't establish SSH communication.")

            logging.info("[ SSH ] Connection established.")

            self.rfile = channel.makefile('r', 0)
            self.wfile = channel.makefile('w', 0)

        else:
            self.rfile = self.request.makefile('r', 0)
            self.wfile = self.request.makefile('w', 0)

    def finish(self):
        # try-except blogs are because of paramiko sometimes throwing
        # exceptions from close() methods.
        try:
            self.wfile.close()
        except:
            pass

        try:
            self.rfile.close()
        except:
            pass

        try:
            if self.server.use_ssh:
                channel.close()
        except:
            pass


    def handle(self):
        from modules.Daemon import Daemon
        manager = Daemon.get_manager()

        try:
            line = self.receive()
            if line == '':
                raise socket.error
            elif line.startswith('poke'):
                line = unicode(line[5:]).split(':')
                test_id = line[0]
                poke_name = line[1]
                logging.info("[ Test %s ] Running poke: %s" % (test_id, poke_name))
                manager.run_poke(test_id, poke_name)
            else:
                logging.info("[ Connection %s ] Handling" % self.client_address[0])

                parent = None
                parent_id = None

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
                    'trigger'     : manager.run_trigger,
                    'time'        : self.send_time
                }

                while 1:
                    if line:
                        logging.info("[ Connection %s ] Received: %s" % (self.client_address[0], line))
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
                                f.write(self.rfile.read(size))
                        if type == 'results_get':
                            type = result[0]
                            to_send = result[1]
                            if type == 'multi':
                                kind = result[2]
                                size_list = []
                                for output in to_send:
                                    if output != None:
                                        if kind == 'duration':
                                            output = str(float(output.seconds)+(output.microseconds/1000000))
                                        elif kind == 'returncode':
                                            output = str(output)
                                        elif kind == 'start_time':
                                            output = output.isoformat()
                                        output_len = len(output)
                                        size_list.append(output_len)
                                    else:
                                        size_list.append(-1)
                                self.send_ok(sizes=size_list)
                                for output in to_send:
                                    if output != None:
                                        if kind == 'duration':
                                            output = str(float(output.seconds)+(output.microseconds/1000000))
                                        elif kind == 'returncode':
                                            output = str(output)
                                        elif kind == 'start_time':
                                            output = output.isoformat()
                                        self.wfile.write(output)
                            elif type == 'list':
                                self.send_list(to_send)
                            else:
                                if to_send != None:
                                    self.send_ok(sizes=[len(to_send)])
                                    self.wfile.write(to_send)
                                else:
                                    self.send_ok(sizes=[-1])
                        else:
                            if type not in ['trigger', 'time']:
                                self.send_ok()
                            if type == 'start':
                                manager.register_handler(params['id'], self.send_100)
                                manager.start_tasks(parent_id, **params)
                    line = self.receive()
                    if line == '':
                        raise socket.error

        except socket.error, IOError:
            logging.info("[ Connection %s ] Dropped" % self.client_address[0])

    def receive(self):
        data = self.rfile.readline().strip()
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

    def send_time(self, test_id=None):
        self.send('200 OK ' + datetime.datetime.now().isoformat())
