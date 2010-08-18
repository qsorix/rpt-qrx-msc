#!/usr/bin/env python
# coding=utf-8

import sys

from modules.Daemon import Daemon

if __name__ == "__main__":
    # TODO Add some command line parameters
    daemon = Daemon(port=int(sys.argv[1]), database=sys.argv[2])
    daemon.run()