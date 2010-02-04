#!/usr/bin/env python

from sched import TaskScheduler
from test import Task, Test
import re
from threading import Thread
from time import strptime

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
	
