#!/usr/bin/env python

import sys
import os
import re
from time import strptime, strftime

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
		output += ' Start: ' + strftime('%Y-%m-%d %H:%M:%S', self.start) + '\n'
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

while not re.search('^test [0-9]+$', line):
	print '400: Bad Request'
	line = sys.stdin.readline().strip()

print '200: OK'
test = Test(int(line[5:]))

line = sys.stdin.readline().strip()
while not re.search('^end$', line):

	if re.search('^file \{[a-zA-Z0-9\.\-]+\} [0-9]+$', line):
		test.files[line.split(' ')[1][1:-1]] = sys.stdin.readline().strip()
		print '200: OK'
	elif re.search('^schedule [0-9]+$', line):
		for i in range(0, int(line.strip().split(' ')[1])):
			task = sys.stdin.readline().strip().split(':')
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

	line = sys.stdin.readline().strip()

print '200: OK'

print test
