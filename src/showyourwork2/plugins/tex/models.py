from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, computed_field, model_validator  # type: ignore

from showyourwork2.paths import package_data


class Theme(BaseModel):
    path: Path
    options: Dict[str, Any] = {}

    @model_validator(mode="before")
    @classmethod
    def allow_path_or_name(cls, data: Any) -> Any:
        if isinstance(data, str):
            data = {"path": _theme_path_from_name(data)}
        elif isinstance(data, dict) and "name" in data:
            data["path"] = _theme_path_from_name(data.pop("name"))
        return data


class Document(BaseModel):
    build_tex: Optional[bool] = None
    synctex: bool = True
    theme: Theme = Theme(
        path=package_data("showyourwork2.plugins.tex", "themes", "base")
    )

    if TYPE_CHECKING:
        path: Path
        artifacts: List[Path] = []

    @computed_field  # type: ignore
    @property
    def build_tex_(self) -> bool:
        if self.build_tex is None:
            return self.path.suffix == ".tex"
        return self.build_tex

    @model_validator(mode="after")
    def generate_artifact_list(self) -> "Document":
        if not self.build_tex_:
            return self
        self.artifacts.append(self.path.with_suffix(".pdf"))
        if self.synctex:
            self.artifacts.append(self.path.with_suffix(".synctex.gz"))
        return self


# Helpers for resolving theme paths
@lru_cache
def _get_built_in_themes() -> Dict[str, Path]:
    path = package_data("showyourwork2.plugins.tex", "themes")
    themes = list(sorted(path.glob("*")))
    return {t.name: t for t in themes}


def _theme_path_from_name(name: str) -> Path:
    built_in = _get_built_in_themes()
    if name in built_in:
        return built_in[name]
    try:
        return package_data(name)
    except ModuleNotFoundError as e:
        raise ValueError(f"Theme '{name}' not found") from e
