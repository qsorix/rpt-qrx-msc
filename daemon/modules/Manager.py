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

    def create_test(self, parent_id, params):
        id = params['id']
        test = Test.get_by(id=id)
        if not test:
            test = Test(id=id)
            session.commit()
        else:
            raise DatabaseError("Test '%s' already exists." % (id))

    def delete_test(self, parent_id , params):
        id = params['id']
        test = Test.get_by(id=id)
        if test:
            for command in test.commands:
                command.delete()
            for file in test.files:
                os.remove(file.path)
                file.delete()
            test.delete()
            session.commit()
        else:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        self.handler.send_ok()

    def add_check_command(self, test_id, params):
        id = params['id']
        test = Test.get_by(id=test_id)
        command = params['command']
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

    def add_setup_command(self, test_id, params):
        id = params['id']
        test = Test.get_by(id=test_id)
        command = params['command']
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

    def add_task_command(self, test_id, params):
        id = params['id']
        test = Test.get_by(id=test_id)
        if params.haskey('at'):
            trigger_type  = 'at'
            trigger_value = params['at']
        elif params.haskey('every'):
            trigger_type  = 'every'
            trigger_value = params['every']
        command = params['command']
        cmd = Command.get_by(test=test, id=id)
        if not cmd:
            file = File.get_by(test=test, id=id)
            if not file:
                cmd = Task(test=test, id=id, command=command, trigger_type=trigger_type, trigger_value=trigger_value)
                session.commit()
            else:
                raise DatabaseError("Command or file named '%s' already exists." % (id))
        else:
            raise DatabaseError("Command or file named '%s' already exists." % (id))
        self.handler.send_ok()
 
    def add_clean_command(self, test_id, params):
        id = params['id']
        test = Test.get_by(id=test_id)
        command = params['command']
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

    def add_file(self, test_id, params):
        id = params['id']
        test = Test.get_by(id=test_id)
        size = params['size']
#        if params.haskey('output'):
#            output = params['output']
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

    def delete_command_or_file(self, test_id, params):
        id = params['id']
        test = Test.get_by(id=test_id)
        cmd = Command.get_by(test=test, id=id)
        if not cmd:
            file = File.get_by(test=test, id=id)
            if not file:
                raise DatabaseError("Command or file named '%s' doesn't exist." % (id))
            else:
                os.remove(file.path)
                file.delete()
        else:
            cmd.delete()
        session.commit()
        self.handler.send_ok()

    def get_results(self, test_id, params):
        id = params['id']
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
                    while size > 1024:
                        data = f.read(1024)
                        self.handler.conn.wfile.write(data)
                        size -= 1024
                    data = f.read(1024)
                    self.handler.conn.wfile.write(data)
        else:
            self.handler.send_ok(size=len(cmd.output))
            self.handler.conn.wfile.write(cmd.output)

    def prepare_test(self, parent_id, params):
        id = params['id']
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        if not self.schedulers.haskey(id):
            self.schedulers[id] = Scheduler(test)
        self.scheduler.prepare()
        self.handler.send_ok()

    def start_test(self, parent_id, params):
        id = params['id']
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        if not self.schedulers.haskey(id):
            self.schedulers[id] = Scheduler(test)
        if params.haskey('at'):
            self.scheduler.start(at_time=params['at'])
        elif params.haskey('in'):
            self.scheduler.start(in_time=params['in'])
        self.handler.send_ok()

    def stop_test(self, parent_id, params):
        id = params['id']
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        self.scheduler.stop()
        self.handler.send_ok()

