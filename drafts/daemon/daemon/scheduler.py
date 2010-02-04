#!/usr/bin/evn python

import sched
import commands
import os
import signal
from subprocess import Popen, PIPE
from time import time, sleep

class TaskScheduler:
	def __init__(self, test):
		self.test = test
		self.s = sched.scheduler(time, sleep)
		#self.s.enterabs(mktime(self.test.start), 1, start_scheduler, ())
		self.s.enterabs(time()+2, 1, self.start_scheduler, ())	# zacznij za 2 sekundy

		self.cmd_s = sched.scheduler(time, sleep)
		
		for cmd in self.test.cmds:
			self.cmd_s.enter(cmd.start, 1, self.get_output, [cmd.cmd])

		self.pids = {}

	def run(self):
		self.s.run()
	
	def run_cmd(self, cmd):
		p = Popen(cmd.split(' '))

		# TODO: Get the output!!!

	def run_name_cmd(self, name, cmd):

		p = Popen(cmd.split(' '))

		# TODO: Get the output!!!

		self.pids[name] = p.pid

	def get_output(self, cmd):
		self.test.results_cmds[cmd] = commands.getoutput(cmd)

	def kill_everything(self):
		print 'End of tasks'

	def kill_cmd(self, task_name):
		os.kill(self.pids.get(task_name), signal.SIGKILL)
		print 'Killed', self.pids.get(task_name)

	def start_scheduler(self):
		self.task_s = sched.scheduler(time, sleep)
		for task in self.test.tasks:
			if task.cmd.startswith('{'):
				task_name = task.cmd[task.cmd.index('{')+1:task.cmd.index('}')]
				task_cmd = task.cmd[task.cmd.index('}')+2:]
				
				self.task_s.enter(task.start, 1, self.run_name_cmd, [task_name, task_cmd])
			elif task.cmd.startswith('kill'):
				task_name = task.cmd[task.cmd.index('{')+1:task.cmd.index('}')]

				self.task_s.enter(task.start, 1, self.kill_cmd, [task_name])
			else:
				self.task_s.enter(task.start, 1, self.run_cmd, [task.cmd])

		# dodanie kill'a dla testu po test.duration
		self.task_s.enter(self.test.duration, 1, self.kill_everything, [])

		# dodanie wykonania komend na koniec testu
		self.task_s.enter(self.test.duration+1, 1, self.cmd_s.run, [])

		# uruchomienie
		self.task_s.run()

