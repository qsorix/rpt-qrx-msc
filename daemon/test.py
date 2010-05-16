#!/usr/bin/env python
# coding=utf-8

from time import strftime, mktime

class Test:
	def __init__(self, id): 
		self.id = id
		self.tasks = []
		self.cmds = []
		self.duration = 0
		self.start = None
		self.files = {}

		self.results_cmds = {}
		self.results_tasks = {}

	def __str__(self):
		output = 'Test ' + str(self.id) + '\n'
		output += ' Duration: ' + str(self.duration) + '\n'
		output += ' Start: ' + strftime('%Y-%m-%d %H:%M:%S', self.start) + ' (' + str(mktime(self.start)) + ')\n'
		output += ' Tasks:\n'
		for task in self.tasks:
			output += '  ' + str(task) + '\n'
		output += ' Commands:\n'
		for cmd in self.cmds:
			output += '  ' + str(cmd) + '\n'
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
