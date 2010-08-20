#!/usr/bin/env python
# coding=utf-8

import re

from common.Exceptions import LineError, ParentError, TypeError, ParamError, ValueError

main_regex        = r'^(?P<type>\w+)(?P<parameters>( \@\{\w+\=[a-zA-Z0-9 -_\.]+\})*)(?P<command> .+)?\s*$'
start_run_regex   = r'^(at\s[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6})$'
start_end_regex   = r'^(duration\s[0-9]+)$'
task_run_regex    = r'^(at\s\d)|(after\s.+)|(every\s\d)$'

main_types        = ['test', 'results', 'prepare', 'start', 'stop', 'delete']
test_sub_types    = ['file', 'check', 'setup', 'task', 'clean', 'delete', 'end']
results_sub_types = ['get', 'end']

digit_types       = ['size']
start_run_types   = ['run']
task_run_types    = ['run']

file_required     = ['size']
task_required     = ['run']
start_required    = ['run', 'end']

def parse(line, parent=None):
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
    req = []
    if not type in ['end', 'get']:
        req.append('id')
    if globals().has_key(type+'_required'):
        req += globals()[type+'_required']
    for param in req:
        if not tmparamap.has_key(param):
            raise ParamError("No required parameter '%s'." % (param))
        else:
            tmparamap.pop(param)

    # Check some parameters values
    if type == 'file':
        param = 'size'
        if not paramap[param].isdigit():
            raise ValueError("Parameter '%s' has no digit value." % (param))
        else:
            paramap[param] = int(paramap[param])
    elif type == 'start':
        param = 'run'
        if not re.match(start_run_regex, paramap[param]):
            raise ValueError("Parameter '%s' has invalid value." % (param))
        param = 'end'
        if not re.match(start_end_regex, paramap[param]):
            raise ValueError("Parameter '%s' has invalid value." % (param))
    elif type == 'task':
        param = 'run'
        if not re.match(task_run_regex, paramap[param]):
            raise ValueError("Parameter '%s' has invalid value." % (param))

    # Check other parameters
    if len(tmparamap) > 0:
        raise ParamError("Unknown parameter '%s'." % (tmparamap.popitem()[1]))

    # Return parsed line
    if parent:
        type = parent+'_'+type
    if command:
        paramap['command'] = command
    return (type, paramap)
    