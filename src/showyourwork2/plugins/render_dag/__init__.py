from pathlib import Path
from typing import Any, Dict, List

import yaml

from showyourwork2.paths import package_data


def snakefiles() -> List[Path]:
    return [package_data("showyourwork2.plugins.render_dag", "workflow", "Snakefile")]


def preprocess_config(config: Dict[str, Any], schema: Dict[str, Any]) -> None:
    with open(
        package_data("showyourwork2.plugins.render_dag", "config.schema.yaml"), "r"
    ) as f:
        schema["render_dag"] = yaml.safe_load(f)

    del config
