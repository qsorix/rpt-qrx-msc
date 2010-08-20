#!/usr/bin/evn python
# coding=utf-8

import os
import re
import ConfigParser
import subprocess
import sched
import shlex
import time
import threading
from datetime import datetime, timedelta

from database.Models import *
from modules.Scheduler import Scheduler
from common.Exceptions import DatabaseError, CommandError, SchedulerError, ResolvError

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
#        config = ConfigParser.SafeConfigParser()
#        config.read('aretes.cfg')
#        tmpdir = config.get('AreteS', 'tmpdir')
        path = './tmp/' + test_id + '_' + id
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
        if not self.schedulers.has_key(id):
            raise SchedulerError("Test '%s' hasn't been started yet." % (id))
        elif self.schedulers[id].still_running():
            raise SchedulerError("Test '%s' is still running." % (id))

    def get_results(self, test_id, command):
        if re.match('@{([a-zA-Z0-9\._]+)}', command):
            match = re.match('@{(?P<ref>[a-zA-Z0-9\._]+)}', command)
            cmd_ids  = [cmd.id for cmd in Command.query.filter_by(test_id=test_id).all()]
            file_ids = [file.id for file in File.query.filter_by(test_id=test_id).all()]

            ref = match.group('ref').split('.')
            if len(ref) is 2:
                id    = ref[0]
                param = ref[1]
                if id in cmd_ids:
                    cmd = Command.get_by(test_id=test_id, id=id)
                    if param == 'output':
                        number = len(cmd.outputs)
                        if number > 0:
                            return (number, [output.content for output in cmd.outputs])
                        else:
                            raise DatabaseError("Output for command '%s' doesn't exist." % (id))
                    elif param == 'returncode':
                        if cmd.returncode:
                            return cmd.returncode
                        else:
                            raise DatabaseError("Returncode for command '%s' doesn't exist." % (id))
#                elif id in file_ids:
#                    file = File.get_by(test_id=test_id, id=id)
#                    if param == 'output':
#                        with open(file.path, 'rb') as f:
#                            # FIXME File doesn't exist.
#                            return f.read()
                else:
#                    raise DatabaseError("Command or file named '%s' doesn't exist." % (id))
                    raise DatabaseError("Command named '%s' doesn't exist." % (id))
            elif len(ref) is 1:
                param = ref[0]
                if param in ['checks', 'setups', 'tasks', 'cleans']:
                    cmd_with_output_list = [cmd.id for cmd in Command.query.filter_by(test_id=test_id).all() if cmd.output]
                    print cmd_with_output_list
                    return cmd_with_output_list
            raise ResolvError("Cannot resolve '%s'." % (to_resolv))
        else:
            raise ParamError("You won't get your results that way.")

    def prepare_test(self, parent_id, id):
        if not Test.get_by(id=id):
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        self._run_commands(Check.query.filter_by(test_id=id).all())

    def _setup_test(self, test_id):
        self._run_commands(Setup.query.filter_by(test_id=test_id).all())

    def start_test(self, parent_id, id, run, end):
        if not Test.get_by(id=id):
            raise DatabaseError("Test '%s' doesn't exist." % (id))
       
        # FIXME Now it's running in 4 seconds
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

       
        self._setup_test(id)
                      
        task_sched.run()

        if end_type == 'duration':
            global_condition.acquire()
            while False:
                global_condition.wait()
            global_condition.release()
            
        print '[test %s] Ended @ %s' % (id, datetime.fromtimestamp(time.time()))
        print '[test %s] Duration: %f' % (id, time.time() - run_value)
            
        self._clean_test(id)

    def _clean_test(self, test_id):
        self._run_commands(Clean.query.filter_by(test_id=test_id).all())

    def stop_test(self, parent_id, id):
        # TODO Stop scheduler, empty queue, kill tasks, run _clean_test
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        if not self.schedulers.has_key(id):
            raise SchedulerError("Test '%s' hasn't been started yet." % (id))
        self.schedulers[id].end()

    def _run_commands(self, commands):
        for cmd in commands:
            args = shlex.split(str(cmd.command))
            print '[test %s] Running %s command "%s"' % (cmd.test_id, cmd.row_type, cmd.id)            
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p.wait()
            Output(command = cmd, content = p.stdout.read())
            cmd.returncode = p.returncode
            session.commit()
            if p.returncode != 0:
                raise CommandError("Command '%s' ended badly." % (cmd.id), cmd.id)

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
