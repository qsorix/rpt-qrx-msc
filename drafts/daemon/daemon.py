#!/usr/bin/env python

import sys
import re
import sched
import subprocess
import commands
from time import *

tests = []

class Test:
	def __init__(self, id):
		self.id = id
		self.tasks = []
		self.duration = 0
		self.start = None
		self.files = {}

	def __str__(self):
		output = 'Test ' + str(self.id) + '\n'
		output += ' Duration: ' + str(self.duration) + '\n'
		output += ' Start: ' + strftime('%Y-%m-%d %H:%M:%S', self.start) + ' (' + str(mktime(self.start)) + ')\n'
		for task in self.tasks:
			output += ' ' + str(task) + '\n'
		for file in self.files.keys():
			output += ' File \"' + file + '\": ' + self.files.get(file)[:30] + '\n'
		return output
	
class Task:
	def __init__(self, start, cmd):
		self.start = start
		self.cmd = cmd

	def __str__(self):
		return 'At ' + str(self.start) + ' start: ' + self.cmd

line = sys.stdin.readline().strip()

#while
if not re.search('^test [0-9]+$', line):
#	line = sys.stdin.readline().strip()
	print '400: Bad Request'
	sys.exit(1)

print '200: OK'
test = Test(int(line[5:]))

line = sys.stdin.readline().strip()
while not re.search('^end$', line):

	if re.search('^file \{.+\} [0-9]+$', line):
		test.files[line.split(' ')[1][1:-1]] = sys.stdin.readline().strip()
		print '200: OK'
	elif re.search('^schedule [0-9]+$', line):
		test.tasks = []
		for i in range(0, int(line.strip().split(' ')[1])):
			task_line = sys.stdin.readline().strip()
#			while
			if not re.search('^[0-9]+\: .+$', task_line):
#				task_line = sys.stdin.readline().strip()
				print '400: Bad Request'
				sys.exit(1)

			task = task_line.split(':')
			test.tasks.append(Task(int(task[0]), task[1][1:]))
		print '200: OK'
	elif re.search('^start [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$', line):
		test.start = strptime(line[6:], "%Y-%m-%d %H:%M:%S")
		print '200: OK'
	elif re.search('^duration [0-9]+$', line):
		test.duration = int(line[9:])
		print '200: OK'
	else:
		print '400: Bad Request'
		sys.exit(1)

	line = sys.stdin.readline().strip()

print '200: OK'

class TaskScheduler:
	def __init__(self):
		self.s = sched.scheduler(time, sleep)
		#self.s.enterabs(mktime(test.start), 1, start_scheduler, ())
		self.s.enterabs(time()+2, 1, self.start_scheduler, ())

	def run(self):
		self.s.run()
	
	def run_cmd(self, cmd):
		print commands.getoutput(cmd)

	def start_scheduler(self):
		task_s = sched.scheduler(time, sleep)
		for task in test.tasks:
			task_s.enter(task.start, 1, self.run_cmd, [task.cmd])
		task_s.run()

ts = TaskScheduler().run()

#print test
