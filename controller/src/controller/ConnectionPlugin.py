from common.PluginMount import PluginMount

class ConnectionPlugin:
    """
    Mount point for plugins which can be used to connect with other hosts

    Plugins implementing this reference should provide the following attributes:

    =================  =======================================================
    connection_type    String naming connection type a plugin can handle. This
                       will be matched agains network host's connection
                       attribute.

    needed_attributes  List of attributes that must be set for a device if
                       this connection is to be used. Will revoke
                       configurations without those attributes set.
                       Defaults to [].
    =================  =======================================================

    And methods FIXME: describe
        connect()
        disconnect()
        __init__(host)
    """
    needed_attributes = []

    __metaclass__ = PluginMount
 
