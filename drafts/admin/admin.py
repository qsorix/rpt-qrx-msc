#!/usr/bin/env python

from xml.dom.minidom import parse
from socket import gethostbyname
import xpath

conf = parse('config.xml')
context = xpath.XPathContext()

for h in context.find('/configuration/hosts/host', conf):
    print context.find('@id/text()', h)[0].data,
    print '=',

    ip = context.find('ip/text()', h);
    if ip:
        print ip[0].data

    name = context.find('name/text()', h);
    if name:
        print gethostbyname(name[0].data)

command =  context.find('/configuration/test/schedule/action/command', conf)[0]
command.normalize();
print context.find('text()', command)[0].data;
