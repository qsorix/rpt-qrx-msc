#!/usr/bin/env python
# coding=utf-8

import re

main_regex     = r'^(?P<type>\w+)\s+(?P<parameters>(\@\{\w+\=.+\}\s+)+)(?P<command>.+)?\s*$'
datetime_regex = r'^[0-9]{4}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}$'
main_types     = ['test', 'results', 'check', 'start', 'close']
sub_types      = ['file', 'task', 'cmd', 'end']
digit_types    = ['size', 'in', 'every', 'duration']
datetime_types = ['at']
required       = ['name']
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

        # Check some parameters values
        for param in datetime_types:
            if param in paramap:
                if not re.match(datetime_regex, paramap[param]):
                    raise NotDatetimeValueError(param)
                else:
                    pass # TODO Convert to Datetime            
        for param in digit_types:
            if param in paramap:
                if not paramap[param].isdigit():
                    raise NotDigitValueError(param)
                else:
                    paramap[param] = int(paramap[param])

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

class NotDatetimeValueError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'parameter\'s '+repr(self.value)+' value is not a correct datetime'

class NotDigitValueError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'parameter\'s '+repr(self.value)+' value is not a digit'

#pars = Parser()
#type, dict, command = pars.parse('task @{name=@{te@{test}te}test@{test}} @{in=5} command', parent='test')
