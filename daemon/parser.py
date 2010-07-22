#!/usr/bin/env python
# coding=utf-8

import re

main_regex        = r'^(?P<type>\w+)(?P<parameters>(\s+\@\{\w+\=.+\})+)(?P<command>\s+.+)?\s*$'
datetime_regex    = r'^[0-9]{4}-[0-9]{2}-[0-9]{2}\.[0-9]{2}:[0-9]{2}:[0-9]{2}$'
main_types        = ['test', 'results', 'prepare', 'start', 'stop', 'delete']
test_sub_types    = ['file', 'check', 'setup', 'task', 'clean', 'delete', 'end']
results_sub_types = ['get', 'end']
digit_types       = ['size', 'in', 'every', 'duration']
datetime_types    = ['at']
required          = ['id']
test_required     = []
test_optional     = []
file_required     = ['size']
file_optional     = ['output']
check_required    = []
check_optional    = []
setup_required    = []
setup_optional    = []
task_required     = [('in', 'every')]
task_optional     = ['output']
clean_required    = []
clean_optional    = []
delete_required   = []
delete_optional   = []
results_required  = []
results_optional  = []
get_required      = []
get_optional      = []
prepare_required  = []
prepare_optional  = []
start_required    = [('at', 'in')]
start_optional    = [('duration', 'until')]
stop_required     = []
stop_optional     = []

class Parser():

    def parse(self, line, parent=None):
        # Check line
        match   = re.match(main_regex, line)
        if match is None:
            raise LineError()

        # Parse type and check for closure
        type    = match.group('type')
        if type is 'close':
            return None

        # Parse the rest of the line
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
            if type not in globals()[parent+'_sub_types']:
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
        for param in req:
            if isinstance(param, tuple):
                for p in param:
                    req.append(p)
                req.remove(param)
        for param in tmparamap:
            if param not in req:
                raise ParamError()

        # Check command
        if parent and parent is not 'test' and command is not None:
            raise CommandError()

        # Return parsed line
        if parent:
            type = parent+'_'+type
        paramap['command'] = command
        return (type, paramap)

    def __str__(self):
        # TODO Nice daemon communication protocol summary
        pass
        
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

