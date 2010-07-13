#!/usr/bin/env python
# coding=utf-8

import sys
import os
from datetime import datetime

from parser import Parser
from models import *
import utilz

class Handler:
    def __init__(self, conn):
        self.conn = conn

    def handle(self):
        parser = Parser()

        while 1:
            line = self.receive()
            name, match = parser.parse(line)

            if name == 'test':
                name = unicode(match.group('name'))
                start = datetime.strptime(match.group('start'), '%Y-%m-%d %H:%M:%S')
                duration = int(match.group('duration'))

                self.recv_test(name, start, duration)

            elif name == 'rslt':
                name = unicode(match.group('name'))

                self.send_results(name)

            elif name == 'close':
                self.send_end()
                break;
            elif name == 'check':
                pass
            elif name == 'start':
                pass
#                self.send_end()
#                break
            else:
                self.send_bad_request()

    def receive(self):
        data = self.conn.rfile.readline().strip()
        if data:
            print >> sys.stderr, "[%s] Received: %s" % (self.conn.client_address[0], data)
        return data

    def recv_file(self, test, name, size, output):
        file = File.query.filter_by(name=name, test=test).first()
        if not file:
            if utilz.name_exists(test, name):
                self.send_bad_request()
                return
            file = File(name=name, test=test, size=size)
        else:
            file.size = size
        if output:
            file.file_output = True
            file.file_path = unicode(output)

        self.send_ok()

        if output:
            with open(utilz.subst(test, unicode(output)), 'wb') as f:
                while size > 1024:
                    data = self.conn.rfile.read(1024)
                    f.write(data)
                    size -= 1024
                data = self.conn.rfile.read(size)
                f.write(data)
        else:
            tmp = ''
            while size > 1024:
                data = self.conn.request.recv(1024)
                tmp += data
                size -= 1024
            data = self.conn.request.recv(size)
            tmp += data

            file.content = tmp

        self.send_complete()

    def recv_task(self, test, name, start, output, command):
        task = Task.query.filter_by(name=name, test=test).first()
        if not task:
            if utilz.name_exists(test, name):
                self.send_bad_request()
                return
            task = Task(command=command, start=start, name=name, test=test)
        else:
            task.start = start
            task.command = command
        if output:
            task.file_output = True
            task.file_path = unicode(output)

        self.send_ok()

    def recv_cmd(self, test, name, command):
        cmd = Command.query.filter_by(command=command, name=name, test=test).first()
        if not cmd:
            if utilz.name_exists(test, name):
                self.send_bad_request()
                return
            cmd = Command(command=command, test=test, name=name)
        else:
            cmd.command = command
        self.send_ok()

    def recv_test(self, name, start, duration):
        test = Test.query.filter_by(name=name).first()
        if not test:
            test = Test(name=name, start=start, duration=duration)
        else:
            test.start = start
            test.duration = duration
        self.send_ok()

        parser = Parser()

        line = self.receive()
        name, match = parser.parse(line)
        while not name == 'end':
            if name == 'file':
                name = unicode(match.group('name'))
                size = int(match.group('size'))
                output = match.group('output')

                self.recv_file(test, name, size, output)

            elif name == 'task':
                name = unicode(match.group('name'))
                start = int(match.group('start'))
                command = unicode(match.group('command'))
                output = match.group('output')

                self.recv_task(test, name, start, output, command)

            elif name == 'cmd':
                name = unicode(match.group('name'))
                command = unicode(match.group('command'))

                self.recv_cmd(test, name, command)

            else:
                self.send_bad_request()

            line = self.receive()
            name, match = parser.parse(line)

        self.send_ok()

    def send_task(self, test, name):
        task = Task.query.filter_by(name=name, test=test).first()
        if task:
            if not task.file_output:
                size = len(task.output)
                self.send_ready(size)
                self.wfile.write(task.output)
            else:
                path = utilz.subst(test, task.file_path)
                size = int(os.path.getsize(path))
                self.send_ready(size)

                with open(path, 'rb') as file:
                    self.wfile.write(file.read())

        else:
            self.send_bad_request()

    def send_cmd(self, test, name):
        cmd = Command.query.filter_by(name=name, test=test).first()
        if cmd:
            size = len(cmd.output)
            self.send_ready(size)
            self.wfile.write(cmd.output)

        else:
            self.send_bad_request()

    def send_file(self, test, name):
        file = File.query.filter_by(name=name, test=test).first()
        if file:
            size = len(file.content)
            self.send_ready(size)
            self.wfile.write(file.content)
        else:
            self.send_bad_request()

    def send_results(self, name):
        test = Test.query.filter_by(name=name).first()
        if not test:
            self.send_bad_request()
        else:
            self.send_ok()

        parser = Parser()

        line = self.receive()
        name, match = parser.parse(line)
        while not name == 'end':
            if name == 'task':
                name = unicode(match.group('name'))

                self.send_task(test, name)

            elif name == 'cmd':
                name = unicode(match.group('name'))

                self.send_cmd(test, name)

            elif name == 'file':
                name = unicode(match.group('name'))

                self.send_file(test, name)

            else:
                self.send_bad_request()

            line = self.receive()
            name, match = parser.parse(line)

        self.send_ok()

    def send(self, msg):
        print >> sys.stderr, "[%s] Sending: %s" % (self.conn.client_address[0], msg)
        self.conn.wfile.write(msg + '\n')

    def send_ok(self):
        self.send('200 OK')

    def send_complete(self):
        self.send('201 Complete')

    def send_ready(self, size):
        self.send('202 Ready ' + str(size))

    def send_end(self):
        self.send('600 The End')

    def send_bad_request(self):
        self.send('400 Bad Request')

    def check(self, test):
        pass

    def start(self, name, time):
#        if not test.duration > 0 or test.start is None:
#            session.rollback()
#            self.sender.send_bad_request()
#            return 1
#        else:
#            self.send_end()
            
        ts = TaskScheduler(test)
        ts.run()
