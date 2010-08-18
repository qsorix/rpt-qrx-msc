#!/usr/bin/evn python
# coding=utf-8

import os
import ConfigParser
import subprocess
import sched
import shlex
import time
import threading
from datetime import datetime, timedelta

from database.Models import *
from modules.Scheduler import Scheduler
from common.Exceptions import DatabaseError, CheckError, SchedulerError

class Manager:
    def __init__(self):
        self.schedulers = {}

    def _id_exists(self, test_id, id):
        return Command.get_by(test_id=test_id, id=id) or File.get_by(test_id=test_id, id=id)

    def create_test(self, parent_id, id):
        if Test.get_by(id=id):
            raise DatabaseError("Test '%s' already exists." % (id))
        test = Test(id=id)
        session.commit()

    def delete_test(self, parent_id , id):
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        session.delete(test)
        session.commit()

    def add_check_command(self, test_id, id, command):
        if self._id_exists(test_id, id):
            raise DatabaseError("Command or file named '%s' already exists." % (id))
        cmd = Check(test_id=test_id, id=id, command=command)
        session.commit()

    def add_setup_command(self, test_id, id, command):
        if self._id_exists(test_id, id):
            raise DatabaseError("Command or file named '%s' already exists." % (id))
        cmd = Setup(test_id=test_id, id=id, command=command)
        session.commit()

    def add_task_command(self, test_id, id, run, command):
        if self._id_exists(test_id, id):
            raise DatabaseError("Command or file named '%s' already exists." % (id))
        cmd = Task(test_id=test_id, id=id, command=command, run=run)
        session.commit()
 
    def add_clean_command(self, test_id, id, command):
        if self._id_exists(test_id, id):
            raise DatabaseError("Command or file named '%s' already exists." % (id))
        cmd = Clean(test_id=test_id, id=id, command=command)
        session.commit()

    def add_file(self, test_id, id, size):
        if self._id_exists(test_id, id):
            raise DatabaseError("File or command named '%s' already exists." % (id))
        config = ConfigParser.SafeConfigParser()
        config.read('daemon.cfg')
        tmpdir = config.get('Daemon', 'tmpdir')
        path = tmpdir + '/' + test_id + '_' + id
        file = File(test_id=test_id, id=id, size=size, path=path)
        session.commit()
        return (path, size)

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

    def open_results(self, parent_id, id):
        if not Test.get_by(id=id):
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        # FIXME Only allow getting results if the test ended.
        if not self.schedulers.has_key(id):
            raise SchedulerError("Test '%s' hasn't been started yet." % (id))
        elif self.schedulers[id].still_running():
            raise SchedulerError("Test '%s' is still running." % (id))

    def get_results(self, test_id, id):
        cmd = Command.get_by(test_id=test_id, id=id)
        if not cmd:
            file = File.get_by(test_id=test_id, id=id)
            if not file:
                raise DatabaseError("Command or file named '%s' doesn't exist." % (id))
            else:
                size = int(os.path.getsize(file.path))
                with open(file.path, 'rb') as f:
                    # TODO File doesn't exist.
                    return f.read()
        else:
            if cmd.output:
                return cmd.output
            else:
                raise DatabaseError("Output for command named '%s' doesn't exist." % (id))

    def prepare_test(self, parent_id, id):
        if not Test.get_by(id=id):
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
        if not Test.get_by(id=id):
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

