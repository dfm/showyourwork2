from pathlib import Path
from typing import List

from showyourwork2.plugins.staging.config import configure as configure
from showyourwork2.plugins.staging.stages import NoOpStage as NoOpStage
from showyourwork2.plugins.staging.stages import Stage as Stage
from showyourwork2.plugins.staging.zenodo import ZenodoStage as ZenodoStage


def snakefile() -> Path:
    from showyourwork2.paths import package_data

    return package_data("showyourwork2.plugins.staging", "workflow", "Snakefile")


def snakefiles() -> List[Path]:
    return [snakefile()]
