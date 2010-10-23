#!/usr/bin/evn python
# coding=utf-8

import sched
import commands
import subprocess
import time
from datetime import datetime
import logging
import re
import shlex
import threading
import os
import signal

from database.Models import *
from common.Exceptions import ResolvError, DaemonError

class Scheduler:
    def __init__(self, test_id, start_time, condition=None, duration=None):
        self.test_id = test_id
        self.task_scheduler  = sched.scheduler(time.time, time.sleep)
        self.active = True
        self.start_time = start_time
        self.started_at = None
        
        self.conditions = {}
        self.global_condition = condition
        self.task_threads = {}
        self.pids = {}
        self.every_count = {}
        
        for task in Task.query.filter_by(test_id=self.test_id).all():
            type, value = self._resolv_task_run(task.run)
            if type == 'after' and Task.get_by(id=value):
                self.conditions[value] = threading.Condition()

        self.task_scheduler.enterabs(start_time, 1, self.start, ()) 

        counter = 0
        for task in Task.query.filter_by(test_id=self.test_id).all():
            type, value = self._resolv_task_run(task.run)
            if type == 'at':
                if (duration and value < duration) or not duration:
                    args = (task.id, self._get_notify_next(task.id))
                    task_thread = threading.Thread(name=task.id, target=self._run_task, args=args)
                    self.task_threads[task.id] = task_thread
                    self.task_scheduler.enterabs(start_time+value, 1, task_thread.start, ())
            elif type == 'every':
                self.every_count[task.id] = 0
                args = (task.id, None, None, value)
                task_thread = threading.Thread(name=task.id, target=self._run_task, args=args)
                self.task_threads[task.id+repr(0)] = task_thread
                self.task_scheduler.enterabs(start_time, 1, task_thread.start, ())
            elif type == 'after':
                after_condition = self._get_run_after(value)
                if after_condition:
                    while isinstance(value, str) or isinstance(value, unicode):
                        type, value = self._resolv_task_run(Task.get_by(test_id=self.test_id, id=value).run)
                    args = (task.id, self._get_notify_next(task.id), after_condition)
                    task_thread = threading.Thread(name=task.id, target=self._run_task, args=args)
                    self.task_threads[task.id] = task_thread
                    counter += 0.2
                    self.task_scheduler.enterabs(start_time+value+counter, 1, task_thread.start, ())
        if duration:
            self.task_scheduler.enterabs(start_time+duration, 1, self.end, (condition, ))          
    
    def run(self):
        self.task_scheduler.run()
    
    def start(self):
        self.started_at = datetime.now()
        test = Test.get_by(id=self.test_id)
        test.start_time = self.started_at
        session.commit()
    
    def end(self, condition=None):
        condition.acquire()

        self.active = False

        for event in self.task_scheduler.queue:
            self.task_scheduler.cancel(event)

        for id in self.task_threads.keys():
            if self.task_threads[id].is_alive():
                if self.pids.has_key(id):
                    os.kill(self.pids[id], signal.SIGKILL)

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
    
    def _run_task(self, task_id, notify_next=None, run_after=None, every=None):
        if notify_next:
            notify_next.acquire()
        if run_after:
            run_after.acquire()
            while False:
                run_after.wait()

        if self.active:
            if every != None:
                while self.active:
                    t = time.time()
                    self._shell_command_execution(task_id)
                    left = every - (time.time() - t)
                    if left > 0:
                        time.sleep(left)
                    # FIXME Command for 'every' can't last longer then 'every' value.
            else:                
                self._shell_command_execution(task_id)
            
        if notify_next:
            notify_next.notify()
            notify_next.release()

    def _shell_command_execution(self, task_id):
        dt = datetime.now()

        cmd_type = str(Command.get_by(test_id=self.test_id, id=task_id).cmd_type)
        command = str(Command.get_by(test_id=self.test_id, id=task_id).command)

        if cmd_type == 'shell':
            try:
                if re.search('@{(?P<ref>[a-zA-Z0-9\._]+)}', command):
                    command = Scheduler.subst(command, self.test_id)
                args = shlex.split(command)
                
                logging.info("[ Test %s ] Running task '%s' : %s" % (self.test_id, task_id, command))
                
                p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                task = Task.get_by(test_id=self.test_id, id=task_id)
                self.pids[task_id] = p.pid               
                task.pid = p.pid
                session.commit()
                p.wait()
                td = datetime.now() - dt
                duration = float(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
                Output(command=task, content=p.stdout.read().strip())
                StartTime(command=task, content=dt)
                Duration(command=task, content=duration)
                Returncode(command=task, content=p.returncode)
                session.commit()
            except (OSError, ResolvError) as e:
                logging.error(e)
                logging.error("[ Test %s ] Task '%s' failed." % (self.test_id, task_id))
                from modules.Daemon import Daemon
                manager = Daemon.get_manager()
#                manager.stop_test(None, self.test_id)
                # FIXME: See if that works:)

        elif cmd_type == 'notify':
            from modules.Daemon import Daemon
            manager = Daemon.get_manager()
            manager.notify_handlers[self.test_id](self.test_id, command)
            
    @staticmethod     
    def subst(param, test_id):
        cmd_ids  = list(cmd.id for cmd in Command.query.filter_by(test_id=test_id).all())
        file_ids = list(file.id for file in File.query.filter_by(test_id=test_id).all())

        def resolve_ref(matchobj):
            to_resolv = matchobj.group('ref')
            ref = to_resolv.split('.')
            if len(ref) is 2:
                id    = ref[0]
                param = ref[1]
                if id in cmd_ids:
                    cmd = Command.get_by(test_id=test_id, id=unicode(id))
                    param_map = {}
                    if len(cmd.returncodes) > 0:
                        param_map['returncode'] = cmd.returncodes[-1]
                    if cmd.row_type == u'task':
                        if cmd.pid is not None:
                            param_map['pid'] = cmd.pid
                        else:
                            raise ResolvError("[ Test %s ] Task '%s' hasn't been run yet." % (self.test_id, cmd.id))
                    if param in param_map.keys():
                        return str(param_map[param])
                elif id in file_ids:
                    file = File.get_by(test_id=test_id, id=unicode(id))
                    param_map = {}
                    param_map['size'] = file.size
                    param_map['path'] = file.path
                    if param in param_map.keys():
                        return str(param_map[param])
            raise ResolvError("[ Test %s ] Cannot resolve '%s'." % (test_id, to_resolv))

        session.close()
        return re.sub('@{(?P<ref>[a-zA-Z0-9\._]+)}', resolve_ref, param)

    def _resolv_task_run(self, run):
        t = run.split(' ')
        if t[0] in ['every', 'at']:
            return (t[0], int(t[1]))
        elif t[0] in ['after', 'trigger']:
            return (t[0], t[1])

    def still_running(self):
        running = len([th for th in self.task_threads.values() if th.is_alive()]) != 0
        return running or not self.task_scheduler.empty()
    
