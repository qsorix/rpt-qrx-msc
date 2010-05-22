#!/usr/bin/env python
# coding=utf-8

import sys
import os
from scheduler import TaskScheduler
from test import Task, Test
import re
from datetime import datetime
from models import *
import ConfigParser
import SocketServer
SocketServer.TCPServer.allow_reuse_address = True

class DaemonHandler(SocketServer.StreamRequestHandler):

    def send(self, msg):
        print >> sys.stderr, "[%s] Sending: %s" % (self.client_address[0], msg)
        self.wfile.write(msg + '\n')

    def send_ok(self):
        self.send('200 OK')

    def send_complete(self):
        self.send('201 Transfer Complete')

    def send_end(self):
        self.send('600 The End')

    def send_bad_request(self):
        self.send('400 Bad Request')

    def send_already_exists(self):
        self.send('401 Already Exists')

    def receive(self):
        data = self.rfile.readline().strip()
        if data:
            print >> sys.stderr, "[%s] Received: %s" % (self.client_address[0], data)
        return data

    def handle(self):
        rtest = re.compile('^test\s+\@\{name=(?P<name>.+)\}\s+\@\{start=(?P<start>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\}\s+\@\{duration=(?P<duration>[0-9]+)\}$')
        rresults = re.compile('^results\s+\@\{name=(?P<name>.+)\}')

        # TODO Only if not doing anything
        # FIXME Closing connection

        while 1:
            print >> sys.stderr, "[%s] Handling..." % self.client_address[0]
            line = self.receive()

            if rtest.match(line):
                m = rtest.match(line)
                name = unicode(m.group('name'))
                start = datetime.strptime(m.group('start'), '%Y-%m-%d %H:%M:%S')
                duration = int(m.group('duration'))
                if not self.recv_test(name, start, duration):
                    break
            elif rresults.match(line):
                m = rresults.match(line)
                name = unicode(m.group('name'))
                if not self.send_results(name):
                    break
            else:
                self.send_bad_request()
 
    def send_results(self, name):
        test = Test.query.filter_by(name=name).first()
        if not test:
            self.send_bad_request()
            return 1
        else:
            self.send_ok()

        rtask = re.compile('^task \@\{name=(?P<name>.+)\}$')
        rcmd  = re.compile('^cmd \@\{name=(?P<name>.+)\}$')
        rfile = re.compile('^file \@\{name=(?P<name>.+)\}$')
        rend  = re.compile('^end$')

        line = self.receive()
        while not rend.match(line):
            if rtask.match(line):
                m = rtask.match(line)
                name = unicode(m.group('name'))

                task = Task.query.filter_by(name=name, test=test).first()
                if task:
                    self.send_ok()
                    size = len(task.output)
                    self.send(str(size) + '\n')
                else:
                    self.send_bad_request()

            else:
                self.send_bad_request()

            line = self.receive()

        self.send_end()
        return 0

    def recv_test(self, name, start, duration):
        if Test.query.filter_by(name=name).first():
            self.send_already_exists()
            return 1
        else:
            test = Test(name=name, start=start, duration=duration)
            self.send_ok()

        rfile  = re.compile('^file\s+\@\{name=(?P<name>.+)\}\s+\@\{size=(?P<size>[0-9]+)\}$')
        rtask  = re.compile('^task\s+\@\{name=(?P<name>.+)\}\s+\@\{at=(?P<start>[0-9]+)\}\s*(\@\{output=(?P<output>.+)\})?\s+(?P<command>.+)$')
        rcmd   = re.compile('^cmd\s+\@\{name=(?P<name>.+)\}\s+(?P<command>.+)$')
        rend   = re.compile('^end$')

        line = self.receive()
        while not rend.match(line):
            if rfile.match(line):
                m = rfile.match(line)
                name = unicode(m.group('name'))
                size = int(m.group('size'))

                file = File(name=name, test=test, size=size)
                # FIXME Some other options
                self.send_ok()

                with open(name, 'wb') as f:
                    while size > 1024:
                        data = self.request.recv(1024)
                        f.write(data)
                        size -= 1024
                    data = self.request.recv(size)
                    f.write(data)
                self.send_complete()

            elif rtask.match(line):
                m = rtask.match(line)
                name = unicode(m.group('name'))
                start = int(m.group('start'))
                command = unicode(m.group('command'))

 #               if Task.query.filter_by(name=name, test=test).all() != []:
 #                   self.send_already_exists()
 #               else:

                task = Task(command=command, start=start, name=name, test=test)
                self.send_ok()

            elif rcmd.match(line):
                m = rcmd.match(line)
                name = unicode(m.group('name'))
                command = unicode(m.group('command'))
 
#                if Command.query.filter_by(command=command, name=name, test=test).all() != []:
#                    self.send_already_exists()
#                else:
                cmd = Command(command=command, test=test, name=name)
                self.send_ok()

            else:
                self.send_bad_request()

            line = self.receive()

        if not test.duration > 0 or test.start is None:
            session.rollback()
            self.send_bad_request()
            return 1
        else:
            session.commit()
            self.send_end()
            
            ts = TaskScheduler(test)
            ts.run()

            return 0

def database():
    metadata.bind = "sqlite:///daemon.db"
    #metadata.bind.echo = True
    session.configure(autoflush=False)
    setup_all()
    create_all()

def config():
    config = ConfigParser.SafeConfigParser()
    config.read('daemon.cfg')

    try:
        tmpdir = config.get('Daemon', 'tmpdir')
    except ConfigParser.NoSectionError:
        config.add_section('Daemon')
        config.set('Daemon', 'tmpdir', './')
        with open('daemon.cfg', 'wb') as f:
            config.write(f)


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Setup database
    database()

    # Setup config
    config()

    daemon = SocketServer.TCPServer((HOST, PORT), DaemonHandler)
    daemon.serve_forever()
