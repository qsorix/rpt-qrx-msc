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
import thread

class TaskScheduler:
    def __init__(self, test):
        self.test = test
        self.s = sched.scheduler(time, sleep)
        
        # Start in 2 seconds
        self.s.enterabs(time()+2, 1, self.start_scheduler, ())
#        self.s.enterabs(mktime(self.test.start), 1, start_scheduler, ())
        
        self.cmd_s = sched.scheduler(time, sleep)
        self.task_s = sched.scheduler(time, sleep)

        self.pids_to_kill = {}
        self.all_pids = []

    def run(self):
        self.s.run()
    
    def run_command(self, cmd):
        print '[test %d] Running command "%s"' % (self.test.id, cmd.command)
        cmd.output = commands.getoutput(cmd.command)
        session.commit()

    def run_task(self, task):
        if task.name and task.name in self.pids_to_kill and task.command == 'kill':
            # Special kill by name task
            self.kill_task(task.name)
        else:
            print '[test %d] Running task "%s"' % (self.test.id, task.command),
            if task.name: print '[%s]' % task.name
            else: sys.stdout.write('\n')

            args = task.command.split()
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            if task.name:
                self.pids_to_kill[task.name] = p.pid
            self.all_pids.append(p.pid)

            thread.start_new_thread(self.save_output, (task, p))

    def save_output(self, task, p):
        output = p.stdout.read()
        task.output = output
        session.commit()

    def kill_task(self, name):
        pid_to_kill = self.pids_to_kill.get(name)

        print '[test %d] Killing task [%s]' % (self.test.id, name),
        try:
            os.kill(pid_to_kill, signal.SIGKILL)
        except OSError:
            print '(already ended)'
        else:
            sys.stdout.write('\n')

    def kill_all_tasks(self):
        for pid in self.all_pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        print '[test %d] Killing all remaining tasks' % self.test.id

    def start_scheduler(self):
        print '[test %d] Starting' % self.test.id

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
        session.commit()
