from pathlib import Path
from typing import Any, Dict, List

from showyourwork2 import git
from showyourwork2.paths import PathLike, package_data


def snakefiles() -> List[Path]:
    return [package_data("showyourwork2.plugins.vcs", "workflow", "Snakefile")]


def filter_files_below(file_list: List[str], file: PathLike) -> List[str]:
    parent = Path(file).parent
    return [f for f in file_list if Path(f).is_relative_to(parent)]


def postprocess_config(config: Dict[str, Any]) -> None:
    git_files = git.list_files()
    for key, deps in config["documents"].items():
        git_deps = filter_files_below(git_files, key)
        config["documents"][key] = list(deps) + git_deps
