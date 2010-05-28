#!/usr/bin/evn python
# coding=utf-8

import sched
import commands
import os
import sys
import signal
import subprocess
from time import time, sleep
from models import *
import ConfigParser
import thread
import threading
import re
import shlex
import utilz

class TaskScheduler:
    def __init__(self, test):
        self.test = test
        self.s = sched.scheduler(time, sleep)
        
        # Start in 2 seconds
        self.s.enterabs(time()+2, 1, self.start_scheduler, ())
#        self.s.enterabs(mktime(self.test.start), 1, start_scheduler, ())
        
        self.cmd_s = sched.scheduler(time, sleep)
        self.task_s = sched.scheduler(time, sleep)

    def run(self):
        self.s.run()
    
    def run_command(self, cmd):
        print '[test %s] Running command "%s"' % (self.test.name, cmd.name)
        cmd.output = commands.getoutput(cmd.command)

    def run_task(self, task):
        print '[test %s] Running task "%s"' % (self.test.name, task.name)

        args = task.command.split()
        utilz.join_args(args)

        for i in range(len(args)):
            args[i] = utilz.subst(self.test, args[i])

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        task.pid = p.pid

        if not task.file_output:
            output = p.stdout.read()
            task.output = output
        else:
            with open(utilz.subst(self.test, task.file_path), 'wb') as file:
                file.write(p.stdout.read())

#        thread.start_new_thread(self.save_output, (task, p))

    def kill_task(self, name):
        pid_to_kill = self.pids_to_kill.get(name)

        print '[test %s] Killing task [%s]' % (self.test.name, name)
        try:
            os.kill(pid_to_kill, signal.SIGKILL)
        except OSError:
            print '(already ended)'
        else:
            sys.stdout.write('\n')

    def kill_all_tasks(self):
        for task in Task.query.filter(Task.pid!=None).all():
            try:
                os.kill(task.pid, signal.SIGKILL)
            except OSError:
                pass
        print '[test %s] Killing all remaining tasks' % self.test.name

    def start_scheduler(self):
        print '[test %s] Starting' % self.test.name

        for task in self.test.tasks:
            self.task_s.enter(task.start, 1, self.run_task, [task])

        # Kill all tasks after test.duration
        self.task_s.enter(self.test.duration, 1, self.kill_all_tasks, [])

        for cmd in self.test.commands:
            self.cmd_s.enter(0, 1, self.run_command, [cmd])
        
        self.cmd_s.enter(1, 1, self.clean_database, [])

        # Start commands scheduler after test.duration
        # FIXME Maybe it's a good idea to start them before tasks?
        self.task_s.enter(self.test.duration+1, 1, self.cmd_s.run, [])

        self.task_s.run()
        self.cmd_s.run()

    def clean_database(self):
        for task in Task.query.filter_by(command=u'kill', test=self.test).all():
            task.delete()
