import importlib

import pluggy

from showyourwork2.plugins import hooks

REQUIRED_PLUGINS = [
    "showyourwork2.config",
]


class PluginManager(pluggy.PluginManager):
    def __init__(self) -> None:
        super().__init__("showyourwork2")
        self.add_hookspecs(hooks)
        for modname in REQUIRED_PLUGINS:
            self.import_plugin(modname)

    def import_plugin(self, modname: str) -> None:
        try:
            mod = importlib.import_module(modname)
        except ImportError as e:
            raise ImportError(
                f'Error importing plugin "{modname}": {e.args[0]}'
            ).with_traceback(e.__traceback__) from e
        self.register(mod, modname)
