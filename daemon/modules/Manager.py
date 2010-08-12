#!/usr/bin/evn python
# coding=utf-8

import os
import ConfigParser

from daemon.Models import *
from modules.Scheduler import Scheduler
from common.Exceptions import DatabaseError

class Manager:
    def __init__(self, handler):
        self.handler = handler
        self.schedulers = {}

    def create_test(self, parent_id, id):
        test = Test.get_by(id=id)
        if not test:
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
        test = Test.get_by(id=test_id)
        cmd = Command.get_by(test=test, id=id)
        if not cmd:
            file = File.get_by(test=test, id=id)
            if not file:
                cmd = Check(test=test, id=id, command=command)
                session.commit()
            else:
                raise DatabaseError("Command or file named '%s' already exists." % (id))
        else:
            raise DatabaseError("Command or file named '%s' already exists." % (id))
        self.handler.send_ok()

    def add_setup_command(self, test_id, id, command):
        test = Test.get_by(id=test_id)
        cmd = Command.get_by(test=test, id=id)
        if not cmd:
            file = File.get_by(test=test, id=id)
            if not file:
                cmd = Setup(test=test, id=id, command=command)
                session.commit()
            else:
                raise DatabaseError("Command or file named '%s' already exists." % (id))
        else:
            raise DatabaseError("Command or file named '%s' already exists." % (id))
        self.handler.send_ok()

    def add_task_command(self, test_id, id, run, command):
        test = Test.get_by(id=test_id)
        cmd = Command.get_by(test=test, id=id)
        if not cmd:
            file = File.get_by(test=test, id=id)
            if not file:
                cmd = Task(test=test, id=id, command=command, run=run)
                session.commit()
            else:
                raise DatabaseError("Command or file named '%s' already exists." % (id))
        else:
            raise DatabaseError("Command or file named '%s' already exists." % (id))
        self.handler.send_ok()
 
    def add_clean_command(self, test_id, id, command):
        test = Test.get_by(id=test_id)
        cmd = Command.get_by(test=test, id=id)
        if not cmd:
            file = File.get_by(test=test, id=id)
            if not file:
                cmd = Clean(test=test, id=id, command=command)
                session.commit()
            else:
                raise DatabaseError("Command or file named '%s' already exists." % (id))
        else:
            raise DatabaseError("Command or file named '%s' already exists." % (id))
        self.handler.send_ok()

    def add_file(self, test_id, id, size):
        test = Test.get_by(id=test_id)
        file = File.get_by(test=test, id=id)
        if not file:
            cmd = Command.get_by(test=test, id=id)
            if not cmd:
                config = ConfigParser.SafeConfigParser()
                config.read('daemon.cfg')
                tmpdir = config.get('Daemon', 'tmpdir')
                path = tmpdir + '/' + test_id + '_' + id
                file = File(test=test, id=id, size=size, path=path)
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
        test = Test.get_by(id=test_id)
        cmd = Command.get_by(test=test, id=id)
        if not cmd:
            file = File.get_by(test=test, id=id)
            if not file:
                raise DatabaseError("Command or file named '%s' doesn't exist." % (id))
            else:
                os.remove(file.path)
                session.delete(file)
        else:
            session.delete(cmd)
        session.commit()
        self.handler.send_ok()

    def get_results(self, test_id, id):
        test = Test.get_by(id=test_id)
        cmd = Command.get_by(test=test, id=id)
        if not cmd:
            file = File.get_by(test=test, id=id)
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
        self.schedulers[id].prepare()
        self.handler.send_ok()

    def start_test(self, parent_id, id):
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        if not self.schedulers.has_key(id):
            self.schedulers[id] = Scheduler(test)
        if params.haskey('at'):
            self.schedulers[id].start(at_time=params['at'])
        elif params.haskey('in'):
            self.schedulers[id].start(in_time=params['in'])
        self.handler.send_ok()

    def stop_test(self, parent_id, id):
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        self.scheduler.stop()
        self.handler.send_ok()

