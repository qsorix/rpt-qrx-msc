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
        while 1:
            print >> sys.stderr, "handle..."
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

        line = self.receive()
        while not re.search('^end$', line):
            if re.search('^file \{.+\} [0-9]+$', line):
                filename = line.split(' ')[1][1:-1]
                file = File(name=unicode(filename), test=test)

                self.send_ok()

                # TODO Receive file content

            # TODO Tasks
#            elif re.search('^schedule [0-9]+$', line):
#                test.tasks = []
#                self.send_ok()

#                for i in range(0, int(line.split(' ')[1])):
#                    task_line = self.receive()

#                    if not re.search('^[0-9]+\: .+$', task_line):
#                        self.send_bad_request()
#                        return

#                    task = task_line.split(':')
#                    test.tasks.append(Task(int(task[0]), task[1][1:]))

#                    self.send_ok()

            elif re.search('^start [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$', line):
                test.start = datetime.strptime(line[6:], "%Y-%m-%d %H:%M:%S")

                self.send_ok()

            elif re.search('^duration [0-9]+$', line):
                test.duration = int(line[9:])

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
            return 0

#            self.daemon.tests[test.id] = test
#            ts = TaskScheduler(test)
#            ts.run()

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    setup_all()
    create_all()

    daemon = SocketServer.TCPServer((HOST, PORT), DaemonHandler)
    daemon.serve_forever()
