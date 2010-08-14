#!/usr/bin/evn python
# coding=utf-8

import sched
import commands
import os
import sys
import signal
import subprocess
from time import time, sleep
from datetime import datetime
import ConfigParser
import thread
import threading
import re
import shlex

from daemon.Models import *
from common.Exceptions import CheckError, ResolvError

# TODO Parameters substitution

class Scheduler:
    def __init__(self, test):
        self.test = test
        
        # Start in 2 seconds
#        self.s.enterabs(time()+2, 1, self.start_scheduler, ())
#        self.s.enterabs(mktime(self.test.start), 1, start_scheduler, ())
        
        self.main_scheduler  = sched.scheduler(time, sleep)
        self.check_scheduler = sched.scheduler(time, sleep)
        self.setup_scheduler = sched.scheduler(time, sleep)
        self.task_scheduler  = sched.scheduler(time, sleep)
        self.clean_scheduler = sched.scheduler(time, sleep)

    def prepare(self):
        for cmd in self.test.commands:
            if isinstance(cmd, Check):
                self.check_scheduler.enter(0, 1, self._run_command, [cmd])
        self.check_scheduler.run()

    def start(self, run, end):
        for cmd in self.test.commands:
            # Setup commands:
            if isinstance(cmd, Setup):
                self.setup_scheduler.enter(0, 1, self._run_command, [cmd])
            # Tasks:
            if isinstance(cmd, Task):
                type, value = self.resolv_run(cmd.run)
                if type == 'in':
                    self.task_scheduler.enter(value, 1, self._run_task, [cmd])
#                elif type == 'every':
#                    self.task_scheduler.enter(0, 1, self._run_task, [cmd])
                    # TODO Run task every x seconds
            # Clean commands:
            if isinstance(cmd, Clean):
                self.clean_scheduler.enter(0, 1, self._run_command, [cmd])

        # Configure main scheduler
        self.main_scheduler.enter(0, 1, self.setup_scheduler.run, ())
        type, value = self.resolv_run(run)
        if type == 'at':
            self.main_scheduler.enterabs(value, 1, self.task_scheduler.run, ())
        elif type == 'in':
            self.main_scheduler.enter(value, 1, self.task_scheduler.run, ())
        type, value = self.resolv_end(end)
        if type == 'duration':
            self.main_scheduler.enter(value, 1, self.clean_scheduler.run, ())
#        elif type == 'until'... TODO

        # Run main scheduler
        print '[test %s] Starting...' % self.test.id
        self.main_scheduler.run()

    def _run_command(self, cmd):
        print '[test %s] Running command "%s"' % (self.test.id, cmd.id)
        status, output = commands.getstatusoutput(cmd.command)
        cmd.output = output
        if isinstance(cmd, Check) and status is not 0:
            raise CheckError("Command '%s' ended badly." % (cmd.id))

    def _run_task(self, task):
        print '[test %s] Running task "%s"' % (self.test.id, task.id)

        args = shlex.split(str(task.command))

        for arg in args:
            if re.search('@{(?P<ref>[a-zA-Z0-9\._]+)}', arg):
                arg = self._subst(arg)

        try:
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            task.pid = p.pid
            task.output = p.stdout.read()
        except OSError:
            pass

    def _subst(self, param):
        cmd_ids  = list(cmd.id for cmd in Command.query.filter_by(test=self.test).all())
        file_ids = list(file.id for file in File.query.filter_by(test=self.test).all())

        def resolve_ref(matchobj):
            to_resolv = matchobj.group('ref')
            ref = to_resolv.split('.')
            if len(ref) is 2:
                id    = ref[0]
                param = ref[1]
                if id in cmd_ids:
                    cmd = Command.get_by(id=id)
                    value_map = cmd.get_subst_params()
                    if cmd.row_type is 'task' and cmd.pid is not None:
                        # TODO Check those pids later
                        values_map['pid'] = cmd.pid
                    if param in value_map.keys():
                        return value_map[param]
                elif id in file_ids:
                    file = File.get_by(id=id)
                    value_map = file.get_subst_params()
                    if param in value_map.keys():
                        return value_map[param]
            elif len(ref) is 1 and ref[0] in ['tmpdir']:
                pass
            raise ResolvError("Cannot resolve '%s'." % (to_resolv))

        return re.sub('@{(?P<ref>[a-zA-Z0-9\._]+)}', resolve_ref, param)

    def resolv_run(self, run):
        run = run.split(' ')
        if run[0] in ['every', 'in']:
            return (run[0], int(run[1]))
        elif run[0] in ['at']:
            return (run[0], datetime.strptime(run[1], '%Y-%m-%d %H:%M:%S'))

    def resolv_end(self, end):
        end = end.split(' ')
        if end[0] in ['duration']:
            return (end[0], int(end[1]))

