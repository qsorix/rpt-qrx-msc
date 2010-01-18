#!/usr/bin/env python

import sys
import os
import re
from time import strptime

tests = []

class Test:
	def __init__(self):
		self.tasks = []
		self.duration = 0
		self.files = {}
	
class Task:
	def __init__(self, start, cmd):
		self.start = start
		self.cmd = cmd

line = sys.stdin.readline()

while not re.search('^test [0-9]+$', line.strip()):
	print '400: Bad Request'
	line = sys.stdin.readline()

print '200: OK'
test = Test()

line = sys.stdin.readline().strip()
while not re.search('^end$', line):

	if re.search('^file \{[a-zA-Z0-9\.\-]+\} [0-9]+$', line):
		test.files[line.split(' ')[1]] = sys.stdin.readline().strip()
		print '200: OK'
	elif re.search('^schedule [0-9]+$', line):
		for i in range(0, int(line.strip().split(' ')[1])):
			task = sys.stdin.readline().strip().split(' ')
			test.tasks.append(Task(int(task[0][:-1]), task[1]))
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
