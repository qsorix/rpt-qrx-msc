#!/usr/bin/env python
# coding=utf-8

from common.PluginMount import PluginMount

class HostDriverPlugin:
    """
    Moint point for plugins implementing host drivers.

    Host driver is an object that renders model host's attributes into commands
    to configure those attributes on a target host.

    Plugins implementing this interface should provide methods:

    process(self, cmd, host, attributes)
        cmd        - instance of HostCommands for given host
        host       - instance of Configuration.ConfiguredHost
        attributes - set of hosts attributes that are left to process

    process must remove handled attributes from the set
    """
    __metaclass__ = PluginMount


class InterfaceDriverPlugin:
    """
    Moint point for plugins implementing host interface drivers.

    Host interface driver is an object that renders model host's interface's
    attributes into commands to configure those attributes on a binded
    interface.

    Plugins implementing this interface should provide methods:

    process(self, cmd, host, attributes)
        cmd        - instance of HostCommands for given host
        host       - instance of Configuration.ConfiguredHost
        interface  - the interface for which configuration is being prepared
        attributes - set of hosts attributes that are left to process

    process must remove handled attributes from the set
    """
    __metaclass__ = PluginMount

