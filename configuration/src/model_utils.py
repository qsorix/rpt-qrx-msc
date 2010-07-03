#!/usr/bin/evn python

from config.Model import host, link
import itertools

def group(name, count):
    g = []
    for i in range(count):
        g.append(host('%s[%i]' % (name, i)))
    return g

def interface(host):
    if 'implicit' in host.interfaces():
        return host.interface('implicit')

    return host.add_interface('implicit')

def link_all(*interfaces):
    for (a, b) in itertools.combinations(interfaces, 2):
        link(a, b)
