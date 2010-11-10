#!/usr/bin/env python
# coding=utf-8

from config.Model import add_host

def group(name, count):
    g = []
    for i in range(count):
        g.append(add_host('%s[%i]' % (name, i)))
    return g

def interface(host):
    if 'implicit' in host.interfaces():
        return host.interface('implicit')

    return host.add_interface('implicit')
