#!/usr/bin/env python

from scheduler import TaskScheduler
from test import Task, Test
import re
from threading import Thread
from time import strptime

class Conn(Thread):
	def __init__(self, c_sock, addr, daemon):
		Thread.__init__(self)
		self.c_sock = c_sock
		self.addr = addr
		self.daemon = daemon

	def send_ok(self):
		self.c_sock.send('200 OK\n')

	def send_bad_request(self):
		self.c_sock.send('400 Bad Request\n')
		self.c_sock.close()

	def run(self):
		line = self.c_sock.recv(1024).strip()
		print '|',line,'|'

		if re.search('^test [0-9]+$', line):
			print line
			self.send_ok()
			self.recv_test(int(line[5:]))
		elif re.search('^results [0-9]+$', line):
			self.send_ok()
			self.send_results(int(line[8:]))
		else:
			self.send_bad_request()
			return

	def send_results(self, test_nr):
		test = self.daemon.tests.get(test_nr)
	
		print 'Sending results for test', test_nr

		for task in test.results_tasks:
			self.c_sock.send(test.results_tasks.get(task))

		for cmd in test.results_cmds:
			self.c_sock.send(test.results_cmds.get(cmd))

		self.c_sock.close()

	def recv_test(self, test_nr):
		test = Test(test_nr)

		line = self.c_sock.recv(1024).strip()
		print '|',line,'|'
		while not re.search('^end$', line):
			if re.search('^file \{.+\} [0-9]+$', line):
				test.files[line.split(' ')[1][1:-1]] = self.c_sock.recv(1024).strip()
				self.send_ok()

			elif re.search('^schedule [0-9]+$', line):
				test.tasks = []
				self.send_ok()

				for i in range(0, int(line.split(' ')[1])):
					task_line = self.c_sock.recv(1024).strip()
					print '|',task_line,'|'

					if not re.search('^[0-9]+\: .+$', task_line):
						self.send_bad_request()
						return

					task = task_line.split(':')
					test.tasks.append(Task(int(task[0]), task[1][1:]))

					self.send_ok()

			elif re.search('^cmds [0-9]+$', line):
				test.cmds = []
				self.send_ok()

				for i in range(0, int(line.split(' ')[1])):
					cmd_line = self.c_sock.recv(1024).strip()
					print '|',cmd_line,'|'

					if not re.search('^[0-9]+\: .+$', cmd_line):
						self.send_bad_request()
						return

					cmd = cmd_line.split(':')
					test.cmds.append(Task(int(cmd[0]), cmd[1][1:]))

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

			line = self.c_sock.recv(1024).strip()
			print '|',line,'|'

		self.send_ok()
		self.c_sock.close()

		print test

		if test.check_config():
			self.daemon.tests[test.id] = test
			ts = TaskScheduler(test)
			ts.run()
		else:
			print 'Cos jest nie tak z tym testem...'
	
