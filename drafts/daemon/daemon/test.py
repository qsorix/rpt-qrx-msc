#!/usr/bin/env python

from time import strftime, mktime

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

	def check_config(self):
		if not self.duration > 0 or self.start is None or not len(self.tasks) > 0:
			return False
		return True
	
class Task:
	def __init__(self, start, cmd):
		self.start = start
		self.cmd = cmd

	def __str__(self):
		return 'At ' + str(self.start) + ' start: ' + self.cmd


