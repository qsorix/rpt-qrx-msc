#!/usr/bin/env python
# coding=utf-8

import re

from common.Exceptions import LineError, ParentError, TypeError, ParamError, ValueError

main_regex        = r'^(?P<type>\w+)(?P<parameters>(\s\@\{\w+\=.+\})*)(?P<command> .+)?\s*$'
datetime_regex    = r'^(at\s[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})|(in\s\d)$'
digit_regex       = r'^(in\s\d)|(every\s\d)$'
main_types        = ['test', 'results', 'prepare', 'start', 'stop', 'delete']
test_sub_types    = ['file', 'check', 'setup', 'task', 'clean', 'delete', 'end']
results_sub_types = ['get', 'end']
digit_types       = ['size', 'in', 'every', 'duration']
datetime_types    = ['at']
test_required     = ['id']
test_optional     = []
file_required     = ['id', 'size']
file_optional     = ['output']
check_required    = ['id']
check_optional    = []
setup_required    = ['id']
setup_optional    = []
task_required     = ['id', 'run']#('in', 'every')]
task_optional     = []
clean_required    = ['id']
clean_optional    = []
delete_required   = ['id']
delete_optional   = []
end_required      = []
end_optional      = []
results_required  = ['id']
results_optional  = []
get_required      = ['id']
get_optional      = []
prepare_required  = ['id']
prepare_optional  = []
start_required    = ['id', 'run']#('at', 'in')]
start_optional    = ['end']#('duration', 'until')]
stop_required     = ['id']
stop_optional     = []

class Parser():

    def parse(self, line, parent=None):
        # Check line
        match   = re.match(main_regex, line)
        if match is None:
            raise LineError("Unknown line '%s'." % (line))

        # Parse line
        type = unicode(match.group('type'))
        params = match.group('parameters')
        command = match.group('command')
        paramap = {}
        if params:
            params = unicode(params)
            for param in re.split(r'\s\@\{', params)[1:]:
                paramsplited = param[:-1].split('=')
                if paramap.has_key(paramsplited[0]):
                    raise ParamError("Parameter '%s' exists more than once." % (paramsplited[0]))
                paramap[paramsplited[0]] = paramsplited[1]
        tmparamap = paramap.copy()
        if command:
            command = unicode(command[1:])

        # Check parent
        if parent not in ['test', 'results', None]:
            raise ParentError("Unknown parent '%s'." % (parent))

        # Check type
        if parent:
            if type not in globals()[parent+'_sub_types']:
                raise TypeError("Unknown subtype '%s'." %(type))
        else:
            if type not in main_types:
                raise TypeError("Unknown type '%s'." %(type))

        # Check required parameters
        req = globals()[type+'_required']
        for param in req:
#            if isinstance(param, tuple):
#                good = False
#                for p in param:
#                    if tmparamap.has_key(p):
#                        tmparamap.pop(p)
#                        if good is False:
#                            good = True
#                        else:
#                            raise ParamError("")
#                if not good:
#                    raise ParamError("")
#            else:
            if not tmparamap.has_key(param):
                raise ParamError("No required parameter '%s'." % (param))
            else:
                tmparamap.pop(param)

        # Check some parameters values
#        for param in datetime_types:
#            if param in paramap:
#                if not re.match(datetime_regex, paramap[param]):
#                    raise ValueError("Parameter '%s' has no datetime value." % (param))
#                else:
#                    pass # TODO Convert to Datetime
        for param in digit_types:
            if param in paramap:
                if not paramap[param].isdigit():
                    raise ValueError("Parameter '%s' has no digital value." % (param))
                else:
                    paramap[param] = int(paramap[param])

        # Check optional parameters
        opt = globals()[type+'_optional']
#        for param in opt:
#            if isinstance(param, tuple):
#                for p in param:
#                    opt.append(p)
#                opt.remove(param)
        for param in tmparamap:
            if param not in opt:
                raise ParamError("Unknown parameter '%s'." % (param))

        # Return parsed line
        if parent:
            type = parent+'_'+type
        if command:
            paramap['command'] = command
        return (type, paramap)

    def __str__(self):
        # TODO Nice daemon communication protocol summary
        pass
        
