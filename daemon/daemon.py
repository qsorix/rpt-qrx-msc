#!/usr/bin/env python
# coding=utf-8

import sys
from scheduler import TaskScheduler
from test import Task, Test
import re
from datetime import datetime
from models import *
import SocketServer
SocketServer.TCPServer.allow_reuse_address = True

class DaemonHandler(SocketServer.StreamRequestHandler):

    def send(self, msg):
        print >> sys.stderr, "[%s] Sending: %s" % (self.client_address[0], msg)
        self.wfile.write(msg + '\n')

    def send_ok(self):
        self.send('200 OK')

    def send_bad_request(self):
        self.send('400 Bad Request')

    def send_already_exists(self):
        self.send('401 Already exists')

    def send_end(self):
        self.send('600 The End')

    def receive(self):
        data = self.rfile.readline().strip()
        if data:
            print >> sys.stderr, "[%s] Received: %s" % (self.client_address[0], data)
        return data

    def handle(self):
        # FIXME Closing connection
        while 1:
            print >> sys.stderr, "[%s] Handling..." % self.client_address[0]
            line = self.receive()

            if re.search('^test [0-9]+$', line):
                if not self.recv_test(int(line[5:])):
                    break
#            elif re.search('^results [0-9]+$', line):
#                if not self.send_results(int(line[8:])):
#                    break
            else:
                self.send_bad_request()
 
    # TODO Sending results
#    def send_results(self, test_nr):
#        test = self.daemon.tests.get(test_nr)
#    
#        print 'Sending results for test', test_nr
#
#        for task in test.results_tasks:
#            self.send(test.results_tasks.get(task))
#
#        for cmd in test.results_cmds:
#            self.send(test.results_cmds.get(cmd))

        return 0

    def recv_test(self, test_nr):
        if Test.query.filter_by(id=test_nr).all() != []:
            self.send_already_exists()
            return 1
        else:
            self.send_ok()
            test = Test(id=test_nr)

        rstart = re.compile('^start (?P<datetime>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})$')
        rdur   = re.compile('^duration (?P<duration>[0-9]+)$')
        rfile  = re.compile('^file \{(?P<name>.+)\} (?P<size>[0-9]+)$')
        rtask  = re.compile('^task (?P<start>[0-9]+)( \{(?P<name>.+)\})? (?P<command>.+)$')
        rcmd   = re.compile('^cmd (?P<command>.+)$')
        rend   = re.compile('^end$')

        line = self.receive()
        while not rend.match(line):
            if rfile.match(line):
                m = rfile.match(line)
                name = unicode(m.group('name'))

                file = File(name=name, test=test)
                self.send_ok()

                # TODO Receive file content

            elif rtask.match(line):
                m = rtask.match(line)
                command = unicode(m.group('command'))
                start = int(m.group('start'))
                name = m.group('name')

                if Task.query.filter_by(command=command, start=start, test=test).all() != []:
                    self.send_already_exists()
                else:
                    if name:
                        task = Task(command=command, start=start, name=unicode(name), test=test)
                    else:
                        task = Task(command=command, start=start, test=test)
                    self.send_ok()

            elif rcmd.match(line):
                m = rcmd.match(line)
                command = unicode(m.group('command'))
 
                if Command.query.filter_by(command=command, test=test).all() != []:
                    self.send_already_exists()
                else:
                    cmd = Command(command=command, test=test)
                    self.send_ok()

            elif rstart.match(line):
                m = rstart.match(line)

                test.start = datetime.strptime(m.group('datetime'), '%Y-%m-%d %H:%M:%S')
                self.send_ok()

            elif rdur.match(line):
                m = rdur.match(line)

                test.duration = int(m.group('duration'))
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

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    setup_all()
    create_all()

    daemon = SocketServer.TCPServer((HOST, PORT), DaemonHandler)
    daemon.serve_forever()
