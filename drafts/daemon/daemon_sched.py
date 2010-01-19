import sched
import commands
import subprocess
from time import time, sleep

class TaskScheduler:
	def __init__(self, test):
		self.test = test
		self.s = sched.scheduler(time, sleep)
		#self.s.enterabs(mktime(self.test.start), 1, start_scheduler, ())
		self.s.enterabs(time()+2, 1, self.start_scheduler, ())

	def run(self):
		self.s.run()
	
	def run_cmd(self, cmd):
		print commands.getoutput(cmd)

	def start_scheduler(self):
		self.task_s = sched.scheduler(time, sleep)
		for task in self.test.tasks:
			self.task_s.enter(task.start, 1, self.run_cmd, [task.cmd])

		# dodanie kill'a dla testu po test.duration
		self.task_s.run()


