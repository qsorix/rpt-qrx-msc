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
        self._run_commands(Check.query.filter_by(test_id=id).all())

    def _setup_test(self, test_id):
        print '[test %s] Setup' % (test_id)
        self._run_commands(Setup.query.filter_by(test_id=test_id).all())
        # FIXME What if setup commands will fail?

    def start_test(self, parent_id, id, run, end):
        if not Test.get_by(id=id):
            raise DatabaseError("Test '%s' doesn't exist." % (id))
       
        # CREATE TASK SCHEDULER (to run in 4 seconds)
        run_type, run_value = self._resolv_test_run(run)
        run_value += 4
        print 'should start at:', datetime.fromtimestamp(run_value)
        
        end_type, end_value = self._resolv_test_end(end)
        global_condition = threading.Condition()
        if end_type == 'duration':
            task_sched = Scheduler(id, run_value, global_condition, duration=end_value)
        else:
            task_sched = Scheduler(id, run_value)
        self.schedulers[id] = task_sched

        # RUN SETUP        
        self._setup_test(id)
                
        print '[test %s] Tasks' % (id)       
        task_sched.run()

        if end_type == 'duration':
            global_condition.acquire()
            while False:
                global_condition.wait()
            global_condition.release()

#        time.sleep(0.01)
#        while task_sched.still_running():
#            time.sleep(0.01)
            
        print '[test %s] Ended @ %s' % (id, datetime.fromtimestamp(time.time()))
        print 'duration:', time.time() - run_value
            
        # RUN CLEAN UP
        self._clean_test(id)
        
#        print "after cleanup:", self.time_from_start()

    def _clean_test(self, test_id):
        print '[test %s] Clean' % (test_id)
        self._run_commands(Clean.query.filter_by(test_id=test_id).all())

    def stop_test(self, parent_id, id):
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
#        self.scheduler.stop()

    def _run_commands(self, commands):
        for cmd in commands:
            args = shlex.split(str(cmd.command))
            print '[test %s] Running command "%s"' % (cmd.test_id, cmd.id)            
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p.wait()
            cmd.output = p.stdout.read()
            cmd.returncode = p.returncode
            session.commit()
            if p.returncode != 0 and isinstance(cmd, Check):
                raise CheckError("Command '%s' ended badly." % (cmd.id))
                # FIXME Should remaining commands be executed?
                # FIXME Should Master know which command ended badly?
                # FIXME Should it be only for Check commands?

    def _resolv_test_run(self, run):
        run = run.split(' ')
#        if run[0] in ['in']:
#            return (run[0], int(run[1]))
        if run[0] in ['at']:
            dt = datetime.strptime(run[1], '%Y-%m-%dT%H:%M:%S.%f')
            epoch = time.mktime(dt.timetuple()) + float(dt.microsecond)/10**6
            return (run[0], epoch)

    def _resolv_test_end(self, end):
        end = end.split(' ')
        if end[0] in ['duration']:
            return (end[0], int(end[1]))
        # TODO Do sth about other possible ends in here
