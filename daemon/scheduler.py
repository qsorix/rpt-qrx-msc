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

class TaskScheduler:
    def __init__(self, test):
        self.test = test
        self.s = sched.scheduler(time, sleep)
        
        # Start in 2 seconds
        self.s.enterabs(time()+2, 1, self.start_scheduler, ())
#        self.s.enterabs(mktime(self.test.start), 1, start_scheduler, ())
        
        self.cmd_s = sched.scheduler(time, sleep)
        self.task_s = sched.scheduler(time, sleep)

#        self.pids_to_kill = {}
        self.all_pids = []

    def run(self):
        self.s.run()
    
    def run_command(self, cmd):
        print '[test %s] Running command "%s"' % (self.test.name, cmd.name)
        cmd.output = commands.getoutput(cmd.command)
        session.commit()

    def join_args(self, args):
        join = False
        symbols = ['"', '\'', '`']
        delete = []

        for i in range(len(args)):
            if join:
                args[first] += ' ' + args[i]
                if args[i].endswith(symbol):
                    join = False
                delete.append(args[i])
            elif args[i][0] in symbols:
                first = i
                symbol = args[i][0]
                join = True

        for arg in delete:
            args.remove(arg)

    def run_task(self, task):
        print '[test %s] Running task "%s"' % (self.test.name, task.name)

        rsubst = re.compile('^(?P<pre>.+)?\@\{(?P<subst>.+)\}(?P<post>.+)?$')

        args = task.command.split()
        self.join_args(args)
        print task.command
        print args

        for i in range(len(args)):
            if rsubst.match(args[i]):
                m = rsubst.match(args[i])
                pre = m.group('pre')
                post = m.group('post')
                subst = m.group('subst')

                args[i] = ''
                if pre: args[i] += pre
                args[i] += unicode(self.subst(subst))
                if post: args[i] += post
        print args
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        task.pid = p.pid
        session.commit()

        # TODO Move it to database query
        self.all_pids.append(p.pid)

        thread.start_new_thread(self.save_output, (task, p))

    def save_output(self, task, p):
        output = p.stdout.read()
        task.output = output
        session.commit()

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
        for pid in self.all_pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        print '[test %s] Killing all remaining tasks' % self.test.name

    def subst(self, str):
        rdatabase = re.compile('^(?P<type>(file|task|cmd))\.(?P<name>[a-zA-Z0-9_]+)\.(?P<param>[a-zA-Z0-9_]+)$')
        rdaemon   = re.compile('^daemon.(?P<param>[a-zA-Z0-9_]+)$')

        if rdatabase.match(str):
            m = rdatabase.match(str)
            type = unicode(m.group('type'))
            name = unicode(m.group('name'))
            param = unicode(m.group('param'))

            print type, name, param

            if type == 'file':
                file = File.query.filter_by(name=name, test=self.test).first()
                if file and param in ['name', 'size']:
                    exec('value = file.%s' % param)
                    return value

            elif type == 'task':
                task = Task.query.filter_by(name=name, test=self.test).first()
                if task and param in ['name', 'command', 'start', 'pid']:
                    exec('value = task.%s' % param)
                    return value

            elif type == 'cmd':
                cmd = Command.query.filter_by(name=name, test=self.test).first()
                if cmd and param in ['name', 'command']:
                    exec('value = cmd.%s' % param)
                    return value

        elif rdaemon.match(str):
            m = rdaemon.match(str)
            param = unicode(m.group('param'))

            if os.path.isfile('daemon.cfg') and param in ['tmpdir']:
                config = ConfigParser.SafeConfigParser()
                config.read('daemon.cfg')

                exec('value = config.get(\'Daemon\', \'%s\')' % param)
                return value

        print 'CHECK THIS: Parameter %s could not be converted!' % str
        return ''

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
        session.commit()
