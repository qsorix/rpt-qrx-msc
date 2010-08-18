#!/usr/bin/evn python
# coding=utf-8

import sched
import commands
import subprocess
import time
from datetime import datetime
import ConfigParser
import re
import shlex
import threading
import os
import signal

from database.Models import *
from common.Exceptions import CheckError, ResolvError

class Scheduler:
    def __init__(self, test_id, start_time, condition, duration=None):
        self.test_id = test_id
        self.task_scheduler  = sched.scheduler(time.time, time.sleep)
        
        self.conditions = {}
        self.task_threads = {}
        self.pids = {}
#        self.every_count = {}
        
        for task in Task.query.filter_by(test_id=self.test_id).all():
            type, value = self._resolv_task_run(task.run)
            if type == 'after' and Task.get_by(id=value):
                self.conditions[value] = threading.Condition()
                        
        for task in Task.query.filter_by(test_id=self.test_id).all():
            type, value = self._resolv_task_run(task.run)
            if type == 'at':
                args = (task.id, self._get_notify_next(task.id))
                task_thread = threading.Thread(name=task.id, target=self._run_task, args=args)
                self.task_threads[task.id] = task_thread
                print task.id, 'should run at:', datetime.fromtimestamp(start_time+value)
                self.task_scheduler.enterabs(start_time+value, 1, task_thread.start, ())
            elif type == 'every':
                # TODO
                pass
#                self.every_count[task.id] = 0
            elif type == 'after':
                after_condition = self._get_run_after(value)
                if after_condition:
                    type, value = self._resolv_task_run(Task.get_by(id=value).run)
                    args = (task.id, None, after_condition)
                    task_thread = threading.Thread(name=task.id, target=self._run_task, args=args)
                    self.task_threads[task.id] = task_thread
                    self.task_scheduler.enterabs(start_time+value+0.01, 1, task_thread.start, ())
        if duration:
            self.task_scheduler.enterabs(start_time+duration, 1, self.end, (condition, ))          
    
    def run(self):
        self.task_scheduler.run()
    
    def end(self, condition):
        condition.acquire()

        for event in self.task_scheduler.queue:
            self.task_scheduler.cancel(event)

        for id in self.task_threads.keys():
            if self.task_threads[id].is_alive():
                if self.pids.has_key(id):
                    os.kill(self.pids[id], signal.SIGKILL)
                else:
                    pass

        condition.notify()
        condition.release()
    
    def _get_notify_next(self, id):
        if self.conditions.has_key(id):
            return self.conditions[id]
        return None
    
    def _get_run_after(self, id):
        if self.conditions.has_key(id):
            return self.conditions[id]
        return None
    
#    def start(self):

#        self.start_time = datetime.now()
#        self.task_scheduler.run()
        
#        test = Test.get_by(id=self.test_id) 
#        test.started_at = self.start_time 
#        now = (datetime.now() - self.start_time)
#        test.length = now.seconds
#        session.commit()

    def _run_task(self, task_id, notify_next=None, run_after=None, every=None):       
#        if notify_next:
#            notify_next.acquire()
#        if run_after:
#            run_after.acquire()
#            while False:
#                run_after.wait()
                        
        print '[test %s] Running task "%s" @ %s' % (self.test_id, task_id, datetime.fromtimestamp(time.time()))

#        if every:
#            self.every_count[task.id] += 1
#            self.task_scheduler.enter(self.every_count[task.id]*every, 1, self._run_task, [task, every=every])

        args = shlex.split(str(Command.get_by(test_id=self.test_id, id=task_id).command))

        try:
            for arg in args:
                if re.search('@{(?P<ref>[a-zA-Z0-9\._]+)}', arg):
                    arg = self._subst(arg)

            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            task = Task.get_by(test_id=self.test_id, id=task_id)
            self.pids[task_id] = p.pid
            task.pid = p.pid
            session.commit()
            p.wait()
            task.output = p.stdout.read()
            session.commit()
        except OSError, ResolvError:
            pass
        
 #       if notify_next:
 #           notify_next.notify_all()
 #           notify_next.release()
            
    def _subst(self, param):
        cmd_ids  = list(cmd.id for cmd in Command.query.filter_by(test_id=self.test_id).all())
        file_ids = list(file.id for file in File.query.filter_by(test_id=self.test_id).all())

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

    def _resolv_task_run(self, run):
        t = run.split(' ')
        if t[0] in ['every', 'at']:
            return (t[0], int(t[1]))
        elif t[0] in ['after']:
            return (t[0], t[1])

    def still_running(self):
        running = len([th for th in self.task_threads.values() if th.is_alive()]) != 0
        return running or not self.task_scheduler.empty()
    