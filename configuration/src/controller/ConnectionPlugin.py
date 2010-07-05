from common.PluginMount import PluginMount

class ConnectionPlugin:
    """
    Mount point for plugins which can be used to connect with other hosts

    Plugins implementing this reference should provide the following attributes:

    ===============  ========================================================
    connection_type  String naming connection type a plugin can handle. This
                     will be matched agains network host's connection
                     attribute.
    ===============  ========================================================
    """
    __metaclass__ = PluginMount
 
