#!/usr/bin/evn python
# coding=utf-8

import sched
import commands
import os
import sys
import signal
import subprocess
from time import time, sleep
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
                self.check_scheduler.enter(0, 1, self.run_command, [cmd])
        try:
            self.check_scheduler.run()
        except CheckError:
            print 'dupa'

    def start(self, at_time=None, in_time=None):
        # Create setup commands scheduler
        for cmd in self.test.commands:
            if isinstance(cmd, Setup):
                self.setup_scheduler.enter(0, 1, self.run_command, [cmd])

        # TODO Create tasks scheduler

        # Create clean commands scheduler
        for cmd in self.test.commands:
            if isinstance(cmd, Clean):
                self.setup_scheduler.enter(0, 1, self.run_command, [cmd])

        # Configure main scheduler
        self.main_scheduler.enter(0, 1, self.setup_scheduler.run, ())
        if at_time:
            self.main_scheduler.enterabs(mktime(self.test.start), 1, self.task_scheduler.run, ())
        elif in_time:
            self.main_scheduler.enter(in_time, 1, self.task_scheduler.run, ())

        # TODO Add some finishing method with clean_scheduler.run()

        # Run main scheduler
        print '[test %s] Starting' % self.test.name
        self.main_scheduler.run()

    def run_command(self, cmd):
        print '[test %s] Running command "%s"' % (self.test.id, cmd.id)
        status, output = commands.getstatusoutput(cmd.command)
        cmd.output = output
        if status is not 0:
            raise CheckError

    def run_task(self, task):
        print '[test %s] Running task "%s"' % (self.test.name, task.name)

        args = shlex.split(task.command)

#        for i in range(len(args)):
            # TODO Create better subst
#            args[i] = utilz.subst(self.test, args[i])

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        task.pid = p.pid

        task.output = p.stdout.read()

    def _subst(self, param):
        cmd_ids  = list(cmd.id for cmd in Command.query.filter_by(test=self.test).all())
        file_ids = list(file.id for file in File.query.filter_by(test=self.test).all())

        print cmd_ids
        print file_ids

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

