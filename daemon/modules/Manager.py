#!/usr/bin/evn python
# coding=utf-8

import os
import re
import logging
import subprocess
import shlex
import time
import threading
import thread
import uuid
from datetime import datetime

from database.Models import *
from modules.Scheduler import Scheduler
from common.Exceptions import *

class Manager:
    def __init__(self):
        self.schedulers = {}
        self.notify_handlers = {}

    def _id_exists(self, test_id, id):
        return Command.get_by(test_id=test_id, id=id) or File.get_by(test_id=test_id, id=id)

    def create_test(self, parent_id, id):
        if Test.get_by(id=id):
            raise DatabaseError("[ Test %s ] Test already exists." % (id))
        Test(id=id)
        session.commit()

    def delete_test(self, parent_id , id):
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("[ Test %s ] Test doesn't exist." % (id))
        session.delete(test)
        session.commit()

    def add_check_command(self, test_id, id, command):
        if self._id_exists(test_id, id):
            raise DatabaseError("[ Test %s ] Command or file named '%s' already exists." % (test_id, id))
        Check(test_id=test_id, id=id, command=command)
        session.commit()

    def add_setup_command(self, test_id, id, command):
        if self._id_exists(test_id, id):
            raise DatabaseError("[ Test %s ] Command or file named '%s' already exists." % (test_id, id))
        Setup(test_id=test_id, id=id, command=command)
        session.commit()

    def add_task_command(self, test_id, id, run, type, command):
        if self._id_exists(test_id, id):
            raise DatabaseError("[ Test %s ] Command or file named '%s' already exists." % (test_id, id))
        Task(test_id=test_id, id=id, command=command, run=run, cmd_type=type)
        session.commit()

    def add_clean_command(self, test_id, id, command):
        if self._id_exists(test_id, id):
            raise DatabaseError("[ Test %s ] Command or file named '%s' already exists." % (test_id, id))
        Clean(test_id=test_id, id=id, command=command)
        session.commit()

    def add_file(self, test_id, id, size):
        if self._id_exists(test_id, id):
            raise DatabaseError("[ Test %s ] File or command named '%s' already exists." % (test_id, id))
        path = './tmp/' + id + str(uuid.uuid1())
        File(test_id=test_id, id=id, size=size, path=path)
        session.commit()
        return (path, size)

    def delete_command_or_file(self, test_id, id):
        if not Command.get_by(test_id=test_id, id=id):
            if not File.get_by(test_id=test_id, id=id):
                raise DatabaseError("[ Test %s ] Command or file named '%s' doesn't exist." % (test_id, id))
            else:
                os.remove(file.path)
                session.delete(file)
        else:
            session.delete(cmd)
        session.commit()

    def open_results(self, parent_id, id):
        if not Test.get_by(id=id):
            raise DatabaseError("[ Test %s ] Test doesn't exist." % (id))
        if not self.schedulers.has_key(id):
            raise SchedulerError("[ Test %s ] Test hasn't been started yet." % (id))
        elif self.schedulers[id].still_running():
            raise SchedulerError("[ Test %s ] Test is still running." % (id))

    def get_results(self, test_id, command):
        if re.match('@{([a-zA-Z0-9\s\-\._]+)}', command):
            match = re.match('@{(?P<ref>[a-zA-Z0-9\s\-\._]+)}', command)
            cmd_ids  = [cmd.id for cmd in Command.query.filter_by(test_id=test_id).all()]

            ref = match.group('ref').split('.')
            if len(ref) is 2:
                id    = ref[0]
                param = ref[1]
                if id in cmd_ids:
                    cmd = Command.get_by(test_id=test_id, id=id)
                    if param == 'output':
                        if len(cmd.invocations) > 0:
                            return ('multi', [invocation.output for invocation in cmd.invocations], 'output')
                        else:
                            raise DatabaseError("[ Test %s ] Output for command '%s' doesn't exist." % (test_id, id))
                    elif param == 'returncode':
                        if len(cmd.invocations) > 0:
                            return ('multi', [invocation.return_code for invocation in cmd.invocations], 'returncode')
                        else:
                            raise DatabaseError("[ Test %s ] Returncode for command '%s' doesn't exist." % (test_id, id))
                    elif param == 'start_time':
                        if len(cmd.invocations) > 0:
                            return ('multi', [invocation.start_time for invocation in cmd.invocations], 'start_time')
                        else:
                            raise DatabaseError("[ Test %s ] Start datetime for command '%s' doesn't exist." % (test_id, id))
                    elif param == 'duration':
                        if len(cmd.invocations) > 0:
                            return ('multi', [invocation.duration for invocation in cmd.invocations], 'duration')
                        else:
                            raise DatabaseError("[ Test %s ] Duration for command '%s' doesn't exist." % (test_id, id)) 
                    raise DatabaseError("[ Test %s ] Command named '%s' doesn't exist." % (test_id, id))
            elif len(ref) is 1:
                param = ref[0]
                if param in ['checks', 'setups', 'tasks', 'cleans']:
                    list = [cmd.id for cmd in Command.query.filter_by(test_id=test_id, row_type=param[:-1]).all() if len(cmd.invocations) > 0]
                    return ('list', list)
                elif param == 'start_time':
                    return ('single', Test.get_by(id=test_id).start_time.isoformat())
                elif param == 'duration':
                    return ('single', str(Test.get_by(id=test_id).duration))
            raise ResolvError("[ Test %s ] Cannot resolve '%s'." % (test_id, to_resolv))
        else:
            raise ParamError("[ Test %s ] You won't get your results that way." % (test_id))

    def run_poke(self, test_id, name):
        pokes = [task for task in Task.query.filter_by(test_id=test_id).all() if task.run == 'poke ' + name]
        self._run_commands(pokes, test_id)

    def run_trigger(self, parent_id, id, name):
        triggers = [task for task in Task.query.filter_by(test_id=id).all() if task.run == 'trigger ' + name]
        self._run_commands(triggers, id)

    def prepare_test(self, parent_id, id):
        if not Test.get_by(id=id):
            raise DatabaseError("[ Test %s ] Test doesn't exist." % (id))
        self._run_commands(Check.query.filter_by(test_id=id).all(), id)

    def _setup_test(self, test_id):
        self._run_commands(Setup.query.filter_by(test_id=test_id).all(), test_id)

    def start_test(self, parent_id, id, run, end):
        if not Test.get_by(id=id):
            raise DatabaseError("[ Test %s ] Test doesn't exist." % (id))

        run_type, run_value = self._resolv_test_run(run)
        
        self._setup_test(id)
        
        if (run_value - time.time()) <= 0.5:
            raise SetupTooLongError("[ Test %s ] Setup took too much time." % (id))
 
    def start_tasks(self, parent_id, id, run, end):
        run_type, run_value = self._resolv_test_run(run)
        end_type, end_value = self._resolv_test_end(end)
        global_condition = threading.Condition()
        if end_type == 'duration':
            task_sched = Scheduler(id, run_value, condition=global_condition, duration=end_value)
        elif end_type == 'complete':
            task_sched = Scheduler(id, run_value)
        self.schedulers[id] = task_sched

        thread.start_new_thread(self._wait_for_the_end, (id, task_sched, end_type, global_condition))

    def _wait_for_the_end(self, test_id, task_sched, end_type, global_condition):
        try:
            task_sched.run()

            if end_type == 'duration':
                global_condition.acquire()
                while False:
                    global_condition.wait()
                global_condition.release()
            elif end_type == 'complete':
                time.sleep(0.01)
                while self.schedulers[test_id].still_running():
                    time.sleep(0.01)
            
            end_time = datetime.now()
            td = end_time - self.schedulers[test_id].started_at
            duration = float(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
            test = Test.get_by(id=test_id)
            test.duration = duration
            logging.info("[ Test %s ] Ended" % (test_id))
            logging.info("[ Test %s ] Duration: %f" % (test_id, test.duration))
            session.commit()
            
            self.clean_test(test_id)

            self.notify_handlers[test_id]()
        except Exception:
            pass

    def clean_test(self, test_id):
        self._run_commands(Clean.query.filter_by(test_id=test_id).all(), test_id)

    def stop_test(self, parent_id, id):
        # FIXME See if that works.
        test = Test.get_by(id=id)
        if not test:
            raise DatabaseError("[ Test %s ] Test 'doesn't exist." % (id))
        if not self.schedulers.has_key(id):
            raise SchedulerError("[ Test %s ] Test hasn't been started yet." % (id))
        self.schedulers[id].end()
        self.clean_test(id)

    def _run_commands(self, commands, test_id):
        for cmd in commands:
            if isinstance(cmd, Task) and cmd.cmd_type == 'notify':
                self.notify_handlers[test_id](test_id, cmd.command)
            else:
                try:
                    command = str(cmd.command)
                    command = Scheduler.subst(command, test_id)
                    args = shlex.split(command)
                    logging.info("[ Test %s ] Running %s command '%s' : %s" % (cmd.test_id, cmd.row_type, cmd.id, command))
                    dt = datetime.now()            
                    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    p.wait()
                    td = datetime.now() - dt
                except OSError, ResolvError:
                    Invocation(command=cmd, start_time=dt)
                    session.commit()

                    raise DaemonError("[ Test %s ] Command '%s' failed." % (test_id, cmd.id))
                else:
                    Invocation(command=cmd, output=p.stdout.read(), start_time=dt, duration=td, return_code=p.returncode)
                    session.commit()

                    if p.returncode != 0:
                        # For sanity_check and setup
                        raise CommandError("[ Test %s ] Command '%s' ended badly." % (test_id, cmd.id), cmd.id)

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

    def register_handler(self, test_id, handler_notify):
        self.notify_handlers[test_id] = handler_notify
