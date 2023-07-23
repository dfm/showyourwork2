from pathlib import Path
from typing import Any, Dict, List

import yaml

from showyourwork2.logging import get_logger
from showyourwork2.paths import package_data


def snakefiles() -> List[Path]:
    return [package_data("showyourwork2.plugins.tex", "workflow", "Snakefile")]


def preprocess_config(config: Dict[str, Any], schema: Dict[str, Any]) -> None:
    # Load the schema to be used for validation of these plugin-specific options
    with open(
        package_data("showyourwork2.plugins.tex", "config.schema.yaml"), "r"
    ) as f:
        schema["tex"] = yaml.safe_load(f)

    # Set the plugin-specific configuration variables
    tex_config = config.get("tex", {})
    enable_synctex = tex_config["synctex"] = tex_config.get("synctex", True)
    config["tex"] = tex_config

    # If no documents are provided, we default to generating a single document
    # called "ms.tex" or "src/tex/ms.tex"
    documents = config.get("documents", [])
    document_names = [d["path"] if isinstance(d, dict) else d for d in documents]
    for d in ["ms.tex", "src/tex/ms.tex"]:
        if d in document_names:
            continue
        if Path(d).is_file():
            get_logger().debug(f"Found default document {d}; adding to document list")
            documents.append(d)
    config["documents"] = documents

    # Generate the list of artifacts from the input list of documents
    artifacts = list(config.get("artifacts", []))
    for doc in config.get("documents", []):
        if isinstance(doc, str):
            name = doc
        else:
            name = doc["path"]

        pdf = Path(name).with_suffix(".pdf")
        synctex = Path(name).with_suffix(".synctex.gz")
        if pdf not in artifacts:
            artifacts.append(pdf)
        if enable_synctex and synctex not in artifacts:
            artifacts.append(synctex)
    config["artifacts"] = artifacts
