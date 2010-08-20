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
from common.Exceptions import *

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
                            return ('multi', (number, [output.content for output in cmd.outputs]))
                        else:
                            raise DatabaseError("Output for command '%s' doesn't exist." % (id))
                    elif param == 'returncode':
                        if cmd.returncode != None:
                            return ('single', str(cmd.returncode))
                        else:
                            raise DatabaseError("Returncode for command '%s' doesn't exist." % (id))
                    elif param == 'started_at':
                        if cmd.started_at:
                            return ('single', cmd.started_at.isoformat())
                        else:
                            raise DatabaseError("Start datetime for command '%s' doesn't exist." % (id))
                    elif param == 'duration':
                        if cmd.duration != None:
                            return ('single', str(cmd.duration))
                        else:
                            raise DatabaseError("Duration for command '%s' doesn't exist." % (id))                        
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
                    list = [cmd.id for cmd in Command.query.filter_by(test_id=test_id, row_type=param[:-1]).all() if len(cmd.outputs) > 0]
                    return ('list', list)
                elif param == 'started_at':
                    return ('single', Test.get_by(id=test_id).started_at.isoformat())
                elif param == 'duration':
                    return ('single', str(Test.get_by(id=test_id).duration))
            raise ResolvError("Cannot resolve '%s'." % (to_resolv))
        else:
            raise ParamError("You won't get your results that way.")

    def prepare_test(self, parent_id, id):
        if not Test.get_by(id=id):
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        self._run_commands(Check.query.filter_by(test_id=id).all(), id)

    def _setup_test(self, test_id):
        self._run_commands(Setup.query.filter_by(test_id=test_id).all(), test_id)

    def start_test(self, parent_id, id, run, end):
        if not Test.get_by(id=id):
            raise DatabaseError("Test '%s' doesn't exist." % (id))

        run_type, run_value = self._resolv_test_run(run)
        
        self._setup_test(id)
        
        if (run_value - time.time()) <= 0.5:
            raise SetupTooLongError("Setup for '%s' took too much time." % (id))
 
    def start_tasks(self, parent_id, id, run, end):
        run_type, run_value = self._resolv_test_run(run)
        end_type, end_value = self._resolv_test_end(end)
        global_condition = threading.Condition()
        if end_type == 'duration':
            task_sched = Scheduler(id, run_value, condition=global_condition, duration=end_value)
        elif end_type == 'complete':
            task_sched = Scheduler(id, run_value)
        self.schedulers[id] = task_sched
                      
        task_sched.run()

        if end_type == 'duration':
            global_condition.acquire()
            while False:
                global_condition.wait()
            global_condition.release()
        elif end_type == 'complete':
            time.sleep(0.01)
            while self.schedulers[id].still_running():
                time.sleep(0.01)
        
        end_time = datetime.now()
        td = end_time - self.schedulers[id].started_at
        duration = float(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
        test = Test.get_by(id=id)
        test.duration = duration
        print '[test %s] Ended @ %s' % (id, end_time)
        print '[test %s] Duration: %f' % (id, test.duration)
        session.commit()
        
        self.clean_test(id)

    def clean_test(self, test_id):
        self._run_commands(Clean.query.filter_by(test_id=test_id).all(), test_id)

    def stop_test(self, parent_id, id):
        # FIXME See if that works.
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("Test '%s' doesn't exist." % (id))
        if not self.schedulers.has_key(id):
            raise SchedulerError("Test '%s' hasn't been started yet." % (id))
        self.clean_test(id)
        self.schedulers[id].end()

    def _run_commands(self, commands, test_id):
        for cmd in commands:
            try:
                command = str(cmd.command)
                if re.search('@{(?P<ref>[a-zA-Z0-9\._]+)}', command):
                    command = Scheduler.subst(command, test_id)
                args = shlex.split(command)
                print '[test %s] Running %s command "%s" : %s' % (cmd.test_id, cmd.row_type, cmd.id, command)
                dt = datetime.now()            
                p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                p.wait()
                td = datetime.now() - dt
                duration = float(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
                Output(command = cmd, content = p.stdout.read().strip())
                cmd.started_at = dt
                cmd.duration = duration
                cmd.returncode = p.returncode
                session.commit()
                if p.returncode != 0:
                    raise CommandError("Command '%s' ended badly." % (cmd.id), cmd.id)
            except (OSError, ResolvError) as e:
                print '[Arete Slave]', e

    def _resolv_test_run(self, run):
        run = run.split(' ')
        if run[0] in ['at']:
            dt = datetime.strptime(run[1], '%Y-%m-%dT%H:%M:%S.%f')
            epoch = time.mktime(dt.timetuple()) + float(dt.microsecond)/10**6
            return (run[0], epoch)

    def _resolv_test_end(self, end):
        end = end.split(' ')
        if end[0] == 'duration':
            return (end[0], int(end[1]))
        elif end[0] == 'complete':
            return (end[0], None)
