#!/usr/bin/evn python

from Model import host, link

def group(name, count):
    g = []
    for i in range(count):
        g.append(host('%s[%i]' % (name, i)))
    return g

def interface(host):
    if 'default' in host.interfaces():
        return host.interfaces()['default']

    return host.interface('default')

def link_all(*interfaces):
    for (a, b) in [(a, b) for a in range(len(interfaces)) for b in range(len(interfaces)) if a<b]:
        link(interfaces[a], interfaces[b])
