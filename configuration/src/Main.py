#!/usr/bin/env python

from config import Configuration
from command import Executer
import sys

def dump_configuration(c):
    for h in c.hosts():
        print '-- HOST ', h.model.name(), ' --'
        m = h.model
        print '    model {'
        print '        ', m.attributes()
        print '        ', [(i.name(), i.attributes()) for i in m.interfaces().values()]
        print '    }'

        n = h.network
        if n is not None:
            print '    network {'
            print '        ', n.attributes()
            print '        ', [(i.name(), i.attributes()) for i in n.interfaces().values()]
            print '    }'

        s = h.schedule
        if s is not None:
            print '    schedule {'
            print '        ', s
            print '    }'

        print

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print "run with %s <model> <network> <mapping> <schedule>" % sys.argv[0]
        sys.exit(1)

    c = Configuration.Configuration()
    c.read(*sys.argv[1:5])

    e = Executer.Executer()

    for h in c.hosts():
        print h.model.name()
        c = e.generate(h)
        c.dump()

