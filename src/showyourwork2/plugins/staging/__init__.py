from pathlib import Path

from showyourwork2.paths import package_data
from showyourwork2.plugins.hooks import hookimpl
from showyourwork2.plugins.staging.config import configure as configure
from showyourwork2.plugins.staging.stages import NoOpStage as NoOpStage, Stage as Stage
from showyourwork2.plugins.staging.zenodo import ZenodoStage as ZenodoStage


@hookimpl
def snakefile() -> Path:
    return package_data("showyourwork2.plugins.staging", "workflow", "Snakefile")
