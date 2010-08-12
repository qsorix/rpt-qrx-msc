#!/usr/bin/env python
# coding=utf-8

import SocketServer
import daemon.Daemon as d

if __name__ == "__main__":
    d.setup_database()
    d.setup_config()

    HOST, PORT = "localhost", 4567
    SocketServer.TCPServer.allow_reuse_address = True
    daemon = SocketServer.TCPServer((HOST, PORT), d.DaemonHandler)
    daemon.serve_forever()

