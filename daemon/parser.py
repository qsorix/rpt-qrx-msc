#!/usr/bin/env python
# coding=utf-8

import re

main_regex     = r'^(?P<type>\w+)(?P<parameters>(\s+\@\{\w+\=.+\})+)(?P<command>\s+.+)?\s*$'
datetime_regex = r'^[0-9]{4}-[0-9]{2}-[0-9]{2}\.[0-9]{2}:[0-9]{2}:[0-9]{2}$'
main_types     = ['test', 'results', 'check', 'start', 'close']
sub_types      = ['file', 'task', 'cmd', 'end']
digit_types    = ['size', 'in', 'every', 'duration']
datetime_types = ['at']
required       = ['id']
test_required  = []
test_optional  = []
file_required  = ['size']
file_optional  = ['output']
task_required  = [('in', 'every')]
task_optional  = ['output']
cmd_required   = []
cmd_optional   = []
rslt_required  = []
rslt_optional  = []
check_required = []
check_optional = []
start_required = [('at','in')]
start_optional = ['duration']

class Parser():

    def parse(self, line, parent=None):
        # Check line
        match   = re.match(main_regex, line)
        if match is None:
            raise LineError()

        # Parse the line
        type    = match.group('type')
        params  = match.group('parameters')[1:].split(' ')
        command = match.group('command')
        if command:
            command = command[1:]
        paramap = {}
        for param in params:
            paramsplited = param[2:-1].split('=')
            paramap[paramsplited[0]] = paramsplited[1]
        tmparamap = paramap.copy()

        # Check parent
        if parent not in ['test', 'results', None]:
            raise ParentError()
        # Check type
        if parent:
            if type not in sub_types:
                raise TypeError()
        else:
            if type not in main_types:
                raise TypeError()

        # Check required parameters
        if parent and parent is 'results':
            req = required
        else:
            req = required + globals()[type+'_required']
        for param in req:
            if isinstance(param, tuple):
                good = False
                for p in param:
                    if tmparamap.has_key(p):
                        tmparamap.pop(p)
                        if good is False:
                            good = True
                        else:
                            raise ParamError()
                if not good:
                    raise ParamError()
            else:
                if not tmparamap.has_key(param):
                    raise ParamError()
                else:
                    tmparamap.pop(param)

        # Check some parameters values
        for param in datetime_types:
            if param in paramap:
                if not re.match(datetime_regex, paramap[param]):
                    raise ValueError()
                else:
                    pass # TODO Convert to Datetime            
        for param in digit_types:
            if param in paramap:
                if not paramap[param].isdigit():
                    raise ValueError()
                else:
                    paramap[param] = int(paramap[param])

        # Check optional parameters
        req = required + globals()[type+'_optional']
        for param in tmparamap:
            if param not in req:
                raise ParamError()

        # Check command
        if parent and parent is not 'test' and command is not None:
            raise CommandError()

        # Return parsed line
        return (type, paramap, command)
        
class LineError(Exception):
    pass
class ParentError(Exception):
    pass
class TypeError(Exception):
    pass
class ParamError(Exception):
    pass
class ValueError(Exception):
    pass
class CommandError(Exception):
    pass

