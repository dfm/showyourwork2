from pathlib import Path
from typing import List


def snakefiles() -> List[Path]:
    from showyourwork2.paths import package_data

    return [package_data("showyourwork2.plugins.tex", "workflow", "Snakefile")]
