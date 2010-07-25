#!/usr/bin/evn python
# coding=utf-8

import os
from models import *
import ConfigParser

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
            raise DatabaseError
        self.handler.send_ok()

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
            raise DatabaseError
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
                raise DatabaseError
        else:
            raise DatabaseError
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
                raise DatabaseError
        else:
            raise DatabaseError
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
                raise DatabaseError
        else:
            raise DatabaseError
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
                raise DatabaseError
        else:
            raise DatabaseError
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
                raise DatabaseError
        else:
            raise DatabaseError
        self.handler.send_ok()

    def delete_command_or_file(self, test_id, params):
        id = params['id']
        test = Test.get_by(id=test_id)
        cmd = Command.get_by(test=test, id=id)
        if not cmd:
            file = File.get_by(test=test, id=id)
            if not file:
                raise DatabaseError
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
                raise DatabaseError
            else:
                # TODO Send file here
                pass
        else:
            self.send_sending(len(cmd.output))
            self.handler.conn.wfile.write(cmd.output)

    def prepare_test(self, parent_id, params):
        # TODO Run check commands
        pass

    def start_test(self, parent_id, params):
        # TODO Start test
        pass

    def stop_test(self, parent_id, params):
        # TODO Stop test
        pass

class DatabaseError(Exception):
    pass
