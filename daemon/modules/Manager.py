#!/usr/bin/evn python
# coding=utf-8

import os
import ConfigParser

from daemon.Models import *
from modules.Scheduler import Scheduler
from common.Exceptions import DatabaseError, CheckError

class Manager:
    def __init__(self, handler):
        self.handler = handler
        self.schedulers = {}

    def create_test(self, parent_id, id):
        if not Test.get_by(id=id):
            test = Test(id=id)
            session.commit()
        else:
            raise DatabaseError("Test '%s' already exists." % (id))

    def delete_test(self, parent_id , id):
        test = Test.get_by(id=id)
        if test:
            session.delete(test)
            session.commit()
        else:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        self.handler.send_ok()

    def add_check_command(self, test_id, id, command):
        if not Command.get_by(test_id=test_id, id=id):
            if not File.get_by(test_id=test_id, id=id):
                cmd = Check(test_id=test_id, id=id, command=command)
                session.commit()
            else:
                raise DatabaseError("Command or file named '%s' already exists." % (id))
        else:
            raise DatabaseError("Command or file named '%s' already exists." % (id))
        self.handler.send_ok()

    def add_setup_command(self, test_id, id, command):
        if not Command.get_by(test_id=test_id, id=id):
            if not File.get_by(test_id=test_id, id=id):
                cmd = Setup(test_id=test_id, id=id, command=command)
                session.commit()
            else:
                raise DatabaseError("Command or file named '%s' already exists." % (id))
        else:
            raise DatabaseError("Command or file named '%s' already exists." % (id))
        self.handler.send_ok()

    def add_task_command(self, test_id, id, run, command):
        if not Command.get_by(test_id=test_id, id=id):
            if not File.get_by(test_id=test_id, id=id):
                cmd = Task(test_id=test_id, id=id, command=command, run=run)
                session.commit()
            else:
                raise DatabaseError("Command or file named '%s' already exists." % (id))
        else:
            raise DatabaseError("Command or file named '%s' already exists." % (id))
        self.handler.send_ok()
 
    def add_clean_command(self, test_id, id, command):
        if not Command.get_by(test_id=test_id, id=id):
            if not File.get_by(test_id=test_id, id=id):
                cmd = Clean(test_id=test_id, id=id, command=command)
                session.commit()
            else:
                raise DatabaseError("Command or file named '%s' already exists." % (id))
        else:
            raise DatabaseError("Command or file named '%s' already exists." % (id))
        self.handler.send_ok()

    def add_file(self, test_id, id, size):
        if not File.get_by(test_id=test_id, id=id):
            if not Command.get_by(test_id=test_id, id=id):
                config = ConfigParser.SafeConfigParser()
                config.read('daemon.cfg')
                tmpdir = config.get('Daemon', 'tmpdir')
                path = tmpdir + '/' + test_id + '_' + id
                file = File(test_id=test_id, id=id, size=size, path=path)
                session.commit()
                with open(path, 'wb') as f:
                    while size > 1024:
                        data = self.handler.conn.request.recv(1024)
                        f.write(data)
                        size -= 1024
                    data = self.handler.conn.request.recv(size)
                    f.write(data)
            else:
                raise DatabaseError("File or command named '%s' already exists." % (id))
        else:
            raise DatabaseError("File or command named '%s' already exists." % (id))
        self.handler.send_ok()

    def delete_command_or_file(self, test_id, id):
        if not Command.get_by(test_id=test_id, id=id):
            if not File.get_by(test_id=test_id, id=id):
                raise DatabaseError("Command or file named '%s' doesn't exist." % (id))
            else:
                os.remove(file.path)
                session.delete(file)
        else:
            session.delete(cmd)
        session.commit()
        self.handler.send_ok()

    def get_results(self, test_id, id):
        cmd = Command.get_by(test_id=test_id, id=id)
        if not cmd:
            file = File.get_by(test_id=test_id, id=id)
            if not file:
                raise DatabaseError("Command or file named '%s' doesn't exist." % (id))
            else:
                size = int(os.path.getsize(file.path))
                self.handler.send_ok(size=size)
                with open(file.path, 'rb') as f:
                    # TODO File doesn't exist.
                    while size > 1024:
                        data = f.read(1024)
                        self.handler.conn.wfile.write(data)
                        size -= 1024
                    data = f.read(1024)
                    self.handler.conn.wfile.write(data)
        else:
            if cmd.output:
                self.handler.send_ok(size=len(cmd.output))
                self.handler.conn.wfile.write(cmd.output)
            else:
                raise DatabaseError("Output for command named '%s' doesn't exist." % (id))
                self.handler.send_bad_request()

    def prepare_test(self, parent_id, id):
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        if not self.schedulers.has_key(id):
            self.schedulers[id] = Scheduler(test)
        try:
            self.schedulers[id].prepare()
        except CheckError:
            self.handler.send_check_error()
        else:
            self.handler.send_ok()

    def start_test(self, parent_id, id, run, end):
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        if not self.schedulers.has_key(id):
            self.schedulers[id] = Scheduler(test)
        self.schedulers[id].start(run, end)
        self.handler.send_ok()

    def stop_test(self, parent_id, id):
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        self.scheduler.stop()
        self.handler.send_ok()

