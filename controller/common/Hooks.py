from common.PluginMount import PluginMount
from common import Exceptions

class HookPlugin:
    """
    Mount point for plugins implementing Hook interface. These plugins can be
    manually selected to run on a configured test before passing it to the
    controller for execution.

    Hooks must providing following attributes:

    =========  ====================================================
    hook_name  Unique string used to identify and select this hook.
    =========  ====================================================
    """
    __metaclass__ = PluginMount

    @staticmethod
    def lookup(name):
        for hook in HookPlugin.plugins:
            if hook.hook_name == name: 
                return hook

        raise Exceptions.MissingPluginError("Can't find a plugin for a hook named '%s'." % name)
