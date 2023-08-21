from pathlib import Path
from typing import TYPE_CHECKING, List

from pydantic import BaseModel, model_validator  # type: ignore

from showyourwork2 import git
from showyourwork2.paths import PathLike


class Document(BaseModel):
    if TYPE_CHECKING:
        path: Path
        dependencies: List[Path] = []

    @model_validator(mode="after")
    def include_git_dependencies(self) -> "Document":
        git_files = git_list_files()
        for dep in filter_files_below(git_files, self.path):
            dep_ = Path(dep)
            if dep_ in self.dependencies or dep_ == self.path:
                continue
            self.dependencies.append(dep_)
        return self


def filter_files_below(file_list: List[str], file: PathLike) -> List[str]:
    parent = Path(file).parent
    return [f for f in file_list if Path(f).is_relative_to(parent)]


def git_list_files() -> List[str]:
    try:
        return git.list_files()
    except RuntimeError as e:
        raise ValueError(
            "Could not list files tracked by git; "
            "are you sure you're in a git repository?"
        ) from e
