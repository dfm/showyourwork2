import importlib
from pathlib import Path
from typing import Any, Dict, List

import yaml
from jsonschema import ValidationError as JSONSchemaValidationError
from jsonschema import validate, validators

from showyourwork2.paths import PathLike, package_data
from showyourwork2.version import __version__


class ConfigVersionError(Exception):
    def __init__(self, config: Dict[str, Any], required_version: int = 2):
        if "config_version" not in config:
            super().__init__(
                "The expected version of the showyourwork configuration must be "
                "specified using the 'config_version' key."
            )
        else:
            super().__init__(
                f"Version {__version__} of showyourwork requires configuration with "
                f"version {required_version} of the specification, but the config file "
                f"specifies the version as {config['config_version']}"
            )


class ValidationError(Exception):
    pass


def load_config(file: PathLike, required_version: int = 2) -> Dict[str, Any]:
    with open(file, "r") as f:
        config = yaml.safe_load(f)

    if config is None:
        config = {}

    return parse_config(config, required_version=required_version)


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


def parse_config(config: Dict[str, Any], required_version: int = 2) -> Dict[str, Any]:
    config = normalize_keys(config)

    # Check the config version. We require a value here to safely fail with old
    # config files.
    if config.get("config_version", None) != required_version:
        raise ConfigVersionError(config, required_version=required_version)

    # Load the schema to be used for validation
    with open(package_data("showyourwork2.config", "config.schema.yaml"), "r") as f:
        schema = yaml.safe_load(f)

    # Extract the plugins and add the default TeX plugin if required
    plugins = config.get("plugins", ["showyourwork2.plugins.tex"])
    if "showyourwork2.plugins.tex" not in plugins and not config.get("notex", False):
        plugins = ["showyourwork2.plugins.tex"] + list(*plugins)
    config["plugins"] = plugins

    # Loop over the plugins and parse their configs
    for plugin in plugins:
        mod = importlib.import_module(plugin)
        if hasattr(mod, "update_config"):
            # The configuration and schema are modified in-place
            mod.update_config(config=config, schema=schema)

    # Validate the config against the schema
    try:
        validate(config, schema, CustomSchemaValidator)
    except JSONSchemaValidationError as e:
        raise ValidationError(
            "The configuration file is invalid; schema validation failed with the "
            f"following error:\n\n{e}"
        ) from e

    # Extract the list of documents and their dependencies and fill it out. The
    # resulting 'documents' config item is keyed by document path and has a list
    # of dependencies, including the global dependencies defined in
    # 'document_dependencies' and the per-document dependencies.
    document_dependencies = list(config.get("document_dependencies", []))
    input_documents = config.get("documents", [])
    if not len(input_documents):
        raise ValidationError(
            "No documents could be found to generate, please populate the 'documents' "
            "configuration field"
        )
    documents: Dict[str, List[str]] = {}
    for doc in input_documents:
        if isinstance(doc, str):
            documents[doc] = document_dependencies
        else:
            documents[doc["path"]] = document_dependencies + list(
                doc.get("dependencies", [])
            )
    config["document_dependencies"] = document_dependencies
    config["documents"] = documents

    return config


# Construct a custom JSON schema validator to optionally allow Path objects
# wherever "string" is expected
def _is_string_or_path(checker: Any, value: Any) -> bool:
    del checker
    return validators.Draft202012Validator.TYPE_CHECKER.is_type(
        value, "string"
    ) or isinstance(value, Path)


type_checker = validators.Draft202012Validator.TYPE_CHECKER.redefine(
    "string", _is_string_or_path
)
CustomSchemaValidator = validators.extend(
    validators.Draft202012Validator, type_checker=type_checker
)
