#!/usr/bin/env python

from daemon_sched import TaskScheduler
import sys
import re
import socket
from threading import Thread
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

class Conn(Thread):
	def __init__(self, c_sock, addr):
		Thread.__init__(self)
		self.c_sock = c_sock
		self.addr = addr

	def send_ok(self):
#		print '200: OK'
		self.c_sock.send('200: OK')

	def send_bad_request(self):
#		print '400: Bad Request'
		self.c_sock.send('400: Bad Request')
		self.c_sock.close()

	def run(self):
		line = self.c_sock.recv(1024)

		if not re.search('^test [0-9]+$', line):
			self.sent_bad_request()
			return

		self.send_ok()
		test = Test(int(line[5:]))

		line = self.c_sock.recv(1024)
		while not re.search('^end$', line):
			if re.search('^file \{.+\} [0-9]+$', line):
				test.files[line.split(' ')[1][1:-1]] = self.c_sock.recv(1024)
				self.send_ok()

			elif re.search('^schedule [0-9]+$', line):
				test.tasks = []
				self.send_ok()

				for i in range(0, int(line.split(' ')[1])):
					task_line = self.c_sock.recv(1024)

					if not re.search('^[0-9]+\: .+$', task_line):
						self.send_bad_request()
						return

					task = task_line.split(':')
					test.tasks.append(Task(int(task[0]), task[1][1:]))

					self.send_ok()

			elif re.search('^start [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$', line):
				test.start = strptime(line[6:], "%Y-%m-%d %H:%M:%S")

				self.send_ok()

			elif re.search('^duration [0-9]+$', line):
				test.duration = int(line[9:])

				self.send_ok()

			else:
				self.send_bad_request()
				return

			line = self.c_sock.recv(1024)

		self.send_ok()
		self.c_sock.close()

		print test

		if test.check_config():
			ts = TaskScheduler(test)
			ts.run()
		else:
			print 'Cos jest nie tak z tym testem...'
	
class Daemon:
	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind(('', int(sys.argv[1])))
		self.sock.listen(1)

		while 1:
			c_sock, addr = self.sock.accept()
			conn = Conn(c_sock, addr)
			conn.start()

		self.sock.close()

daemon = Daemon()


