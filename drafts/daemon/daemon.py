#!/usr/bin/env python

import sys
import os
import re

line = sys.stdin.readline()

while not re.search('^test +[0-9]+$', line.strip()):
	print '400: Bad Request'
	line = sys.stdin.readline()

print '200: OK'

line = sys.stdin.readline().strip()
while not re.search('^end$', line):

	if re.search('^file +\{[a-zA-Z0-9\.\-]+\} +[0-9]+$', line):
		print sys.stdin.readline().strip()
		print '200: OK'
	elif re.search('^schedule +[0-9]+$', line):
		for i in range(0,int(line.strip().split(' ')[1])):
			print sys.stdin.readline().strip()
		print '200: OK'
	elif re.search('^start +[0-9]{4}-[0-9]{2}-[0-9]{2} +[0-9]{2}:[0-9]{2}:[0-9]{2}$', line): # TODO: bez TZ
		print line
		print '200: OK'
	elif re.search('^duration +[0-9]+$', line):
		print line
		print '200: OK'
	else:
		print '400: Bad Request'

	line = sys.stdin.readline().strip()

print '200: OK'
