#!/usr/bin/env python

from config import Configuration
from command import Executer
from controller import Controller

import sys

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print "run with %s <model> <network> <mapping> <schedule>" % sys.argv[0]
        sys.exit(1)

    c = Configuration.Configuration()
    configured_test = c.read(*sys.argv[1:5])
    configured_test.sanity_check()

    e = Executer.Executer()
    prepared_commands = e.process( configured_test )
    #TODO: prepared_commands.sanity_check()

    ctrl = Controller.Controller()
    ctrl.run(configured_test, prepared_commands)

