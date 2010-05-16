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
        if self.duration != None:
            output += ' Duration: ' + str(self.duration) + '\n'
        if self.start != None:
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

    def check(self):
        err_list = []

        if not self.duration > 0:
            err_list.append("duration time is set to 0")
        if self.start is None:
            err_list.append("start time is not set")
        if not len(self.tasks) > 0:
            err_list.append("there are no tasks")

        if len(err_list) != 0:
            return err_list
        return None
    
class Task:
    def __init__(self, start, cmd):
        self.start = start
        self.cmd = cmd

    def __str__(self):
        return 'At ' + str(self.start) + ' start: ' + self.cmd
