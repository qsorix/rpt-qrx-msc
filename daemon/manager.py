#!/usr/bin/evn python
# coding=utf-8

from models import *

class Manager:
    def __init__(self, handler):
        self.handler = handler

    def create_test(self, parent_id, params):
        id = params['id']
        test = Test.get_by(id=id)
        if not test:
            test = Test(id=id)
        self.handler.send_ok()

    def delete_test(self, parent_id , params):
        id = params['id']
        test = Test.get_by(id=id)
        if test:
            for command in test.commands:
                command.delete()
            test.delete()
        else:
            raise ManagerError
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
            else:
                raise ManagerError
        elif isinstance(cmd, Check):
            cmd.command = command
        else:
            raise ManagerError
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
            else:
                raise ManagerError
        elif isinstance(cmd, Setup):
            cmd.command = command
        else:
            raise ManagerError
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
#        if params.haskey('output'):
#            output = params['output']
        command = params['command']
        cmd = Command.get_by(test=test, id=id)
        if not cmd:
            file = File.get_by(test=test, id=id)
            if not file:
                cmd = Task(test=test, id=id, command=command, trigger_type=trigger_type, trigger_value=trigger_value)
            else:
                raise ManagerError
        elif isinstance(cmd, Task):
            cmd.command = command
            cmd.trigger_type = trigger_type
            cmd.trigger_value = trigger_value
        else:
            raise ManagerError
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
            else:
                raise ManagerError
        elif isinstance(cmd, Clean):
            cmd.command = command
        else:
            raise ManagerError
        self.handler.send_ok()

    def add_file(self, test_id, params):
        id = params['id']
#        if params.haskey('output'):
#            output = params['output']
 
    def delete_command(self, test_id, params):
        id = params['id']
        Command.get_by(test=Test.query.get_by(id=test_id), id=id).delete()

    def get_results(self, test_id, params):
        id = params['id']
        test = Test.get_by(id=test_id)
        cmd = Command.get_by(test=test, id=id)
        if not cmd:
            file = File.get_by(test=test, id=id)
            if not file:
                raise ManagerError
            else:
                # TODO Send file here
                pass
        else:
            self.send_sending(len(cmd.output))
            self.handler.conn.wfile.write(cmd.output)

    def prepare_test(self, parent_id, params):
        pass

    def start_test(self, parent_id, params):
        pass

    def stop_test(self, parent_id, params):
        pass

class ManagerError(Exception):
    pass
