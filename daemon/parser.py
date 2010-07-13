#!/usr/bin/env python
# coding=utf-8

import re

#regexes = [
#    ('test',  r'^test\s+\@\{name=(?P<name>.+)\}\s+\@\{start=(?P<start>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\}\s+\@\{duration=(?P<duration>[0-9]+)\}$'),
#        ('file',  r'^file\s+\@\{name=(?P<name>[a-zA-Z0-9_]+)\}\s*(\@\{output=(?P<output>.+)\})?\s+\@\{size=(?P<size>[0-9]+)\}$'),
#        ('task',  r'^task\s+\@\{name=(?P<name>[a-zA-Z0-9_]+)\}\s*(\@\{output=(?P<output>.+)\})?\s+\@\{at=(?P<start>[0-9]+)\}\s+(?P<command>.+)$'),
#        ('cmd',   r'^cmd\s+\@\{name=(?P<name>[a-zA-Z0-9_]+)\}\s+(?P<command>.+)$'),
#    ('rslt',  r'^results\s+\@\{name=(?P<name>.+)\}$'),
#        ('task',  r'^task\s+\@\{name=(?P<name>.+)\}$'),
#        ('cmd',   r'^cmd\s+\@\{name=(?P<name>.+)\}$'),
#        ('file',  r'^file\s+\@\{name=(?P<name>.+)\}$'),
#    ('end',   r'^end$'),
#    ('check', r'^check\s+\@\{name=(?P<name>.+)\}$'),
#    ('start', r'^check\s+\@\{name=(?P<name>.+)\}\s+\@\{at=(?P<start>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\}$'),
#    ('close', r'^close$')
#]

main_regex     = r'^(?P<type>\w+)\s+(?P<parameters>(\@\{\w+\=\w+\}\s+)+)(?P<command>.+)?\s*$'
main_types     = ['test', 'results', 'check', 'start', 'close']
sub_types      = ['file', 'task', 'cmd', 'end']
required       = ['name']
test_required  = []
test_optional  = []
file_required  = ['size']
file_optional  = ['output']
task_required  = [('at', 'every')]
task_optional  = ['output']
cmd_required   = []
cmd_optional   = []
rslt_required  = []
rslt_optional  = []
check_required = []
check_optional = []
start_required = [('at','in')]
start_optional = ['duration']    # TODO Do we need any other type of ending test?

class Parser():

    def __init__(self):
        self.last_match = None

    def match(self, pattern, text):
        self.last_match = re.match(pattern, text)
        return self.last_match

    def search(self, pattern, text):
        self.last_match = re.search(pattern, text)
        return self.last_match

#    def parse(self, line):
#        for name, regex in regexes:
#            if self.match(regex, line):
#                return (name, self.last_match)
#        return (None, None)

    def parse(self, line, parent=None):
        # Parse the line
        match   = re.match(main_regex, line)
        type    = match.group('type')
        params  = match.group('parameters')[:-1].split(' ')
        command = match.group('command')
        paramap = {}
        for param in params:
            paramsplited = param[2:-1].split('=')
            paramap[paramsplited[0]] = paramsplited[1]
        tmparamap = paramap.copy()
      
        # Check type
        if parent:
            if type not in sub_types:
                raise UnknownTypeError(type)
        else:
            if type not in main_types:
                raise UnknownTypeError(type)

        # Check required parameters
        req = required
        if parent and parent is 'test':
            req += globals()[type+'_required']
        print req
        for param in req:
            if isinstance(param, tuple):
                good = False
                for p in param:
                    if tmparamap.has_key(p):
                        tmparamap.pop(p)
                        if good is False:
                            good = True
                        else:
                            raise TooManyParamsError(param)
                if not good:
                    raise RequiredParamError(param)
            else:
                if not tmparamap.has_key(param):
                    raise RequiredParamError(param)
                else:
                    tmparamap.pop(param)

        print paramap
        print tmparamap

        # Check optional parameters
        for param in tmparamap:
            if param not in required + globals()[type+'_optional']:
                raise UnknownParameterError(param)

        # Return parsed line
        return (type, paramap, command)
        
class UnknownTypeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'unknown type '+repr(self.value)

class UnknownParameterError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'unknown parameter '+repr(self.value)

class RequiredParamError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'required parameter '+repr(self.value)+' not present'

class TooManyParamsError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'only one parameter from '+repr(self.value)+' can be present'

pars = Parser()
pars.parse('task @{output=value1} @{name=dupa} @{every=321} command', parent='test')
