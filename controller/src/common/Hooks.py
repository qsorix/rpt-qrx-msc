from common.PluginMount import PluginMount

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
