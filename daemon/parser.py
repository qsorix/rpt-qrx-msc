#!/usr/bin/env python
# coding=utf-8

import re

# TODO Make this stuff more advanced.

regexes = [
    ('test',  r'^test\s+\@\{name=(?P<name>.+)\}\s+\@\{start=(?P<start>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\}\s+\@\{duration=(?P<duration>[0-9]+)\}$'),
        ('file',  r'^file\s+\@\{name=(?P<name>[a-zA-Z0-9_]+)\}\s*(\@\{output=(?P<output>.+)\})?\s+\@\{size=(?P<size>[0-9]+)\}$'),
        ('task',  r'^task\s+\@\{name=(?P<name>[a-zA-Z0-9_]+)\}\s*(\@\{output=(?P<output>.+)\})?\s+\@\{at=(?P<start>[0-9]+)\}\s+(?P<command>.+)$'),
        ('cmd',   r'^cmd\s+\@\{name=(?P<name>[a-zA-Z0-9_]+)\}\s+(?P<command>.+)$'),
    ('rslt',  r'^results\s+\@\{name=(?P<name>.+)\}$'),
        ('task',  r'^task\s+\@\{name=(?P<name>.+)\}$'),
        ('cmd',   r'^cmd\s+\@\{name=(?P<name>.+)\}$'),
        ('file',  r'^file\s+\@\{name=(?P<name>.+)\}$'),
    ('end',   r'^end$'),
    ('check', r'^check\s+\@\{name=(?P<name>.+)\}$'),
    ('start', r'^check\s+\@\{name=(?P<name>.+)\}\s+\@\{at=(?P<start>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\}$'),
    ('close', r'^close$')
]

class Parser():

    def __init__(self):
        self.last_match = None

    def match(self, pattern, text):
        self.last_match = re.match(pattern, text)
        return self.last_match

    def search(self, pattern, text):
        self.last_match = re.search(pattern, text)
        return self.last_match

    def parse(self, line):
        for name, regex in regexes:
            if self.match(regex, line):
                return (name, self.last_match)
        return (None, None)

