#!/usr/bin/env python
# coding=utf-8

import inspect
import os

def relative(path):
    calling_file = inspect.stack()[1][1]
    relpath = os.path.join(os.path.dirname(calling_file), path)
    return relpath

