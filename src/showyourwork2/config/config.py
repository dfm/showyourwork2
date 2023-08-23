from typing import Any, Dict, List, Tuple

import yaml
from pydantic import create_model

from showyourwork2.config.models import Config, expect_at_least_one_document
from showyourwork2.paths import PathLike
from showyourwork2.plugins import PluginManager


def load_config(file: PathLike) -> Config:
    with open(file, "r") as f:
        config = yaml.safe_load(f)

    if config is None:
        config = {}

    return parse_config(config)[0]


def normalize_keys(config: Any) -> Any:
    if isinstance(config, dict):
        result = {}
        for k, v in config.items():
            value = normalize_keys(v)
            result[k.replace("-", "_")] = value
        return result
    elif isinstance(config, list):
        return [normalize_keys(v) for v in config]
    return config


def parse_config(config: Dict[str, Any]) -> Tuple[Config, PluginManager]:
    config = normalize_keys(config)

    # Extract the plugins and add the default TeX plugin if required
    plugins = config.get("plugins", ["showyourwork2.plugins.tex"])
    if "showyourwork2.plugins.tex" not in plugins:
        plugins = ["showyourwork2.plugins.tex"] + list(plugins)
    config["plugins"] = plugins

    # Register all of the requested plugins first, since some might update the
    # configuration parsing.
    plugin_manager = PluginManager()
    for plugin in plugins:
        plugin_manager.import_plugin(plugin)

    # Load the schema to be used for validation
    Document = create_model(
        "Document", __base__=tuple(plugin_manager.hook.document_model())
    )
    Config = create_model(
        "Config",
        __base__=tuple(plugin_manager.hook.config_model()),
        documents=(List[Document], []),  # type: ignore
        __validators__={"expect_at_least_one_document": expect_at_least_one_document},
    )

    return Config.model_validate(config), plugin_manager
