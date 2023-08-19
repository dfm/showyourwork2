from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from jinja2 import Environment, FileSystemLoader

from showyourwork2.paths import PathLike
from showyourwork2.plugins.tex.models import Theme as ThemeModel, _theme_path_from_name


class Theme:
    def __init__(self, model: ThemeModel):
        self.path = model.path
        self.options = model.options
        self._hierarchy: List[Path] = []
        self.config: Dict[str, Any] = {}
        _walk_theme_hierarchy(self.path, self._hierarchy, self.config)

    def resources_for_template(self, template_slug: str) -> Dict[Path, Path]:
        resources: Dict[Path, Path] = {}
        for theme in self._hierarchy:
            resource_directory = theme / "resources" / template_slug
            if resource_directory.exists():
                for resource in sorted(resource_directory.rglob("*")):
                    key = resource.relative_to(resource_directory)
                    if key not in resources:
                        resources[key] = resource
        return resources

    def render(
        self,
        template_name: str,
        config: Dict[str, Any],
        dependencies: Optional[Dict[str, Any]] = None,
    ) -> str:
        env = Environment(
            block_start_string="((*",
            block_end_string="*))",
            variable_start_string="((-",
            variable_end_string="-))",
            comment_start_string="((=",
            comment_end_string="=))",
            autoescape=False,
            loader=FileSystemLoader(self._hierarchy),
        )
        return env.get_template(template_name).render(
            config=config, dependencies=dependencies
        )

    def render_to(
        self,
        template_name: str,
        target_file: PathLike,
        config: Dict[str, Any],
        dependencies: Optional[Dict[str, Any]] = None,
    ) -> None:
        txt = self.render(template_name, config, dependencies=dependencies)
        with open(target_file, "w") as f:
            f.write(txt)


def _load_theme_config(theme: Path) -> Dict[str, Any]:
    config_file = theme / "theme.yml"
    if config_file.is_file():
        with open(config_file, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def _walk_theme_hierarchy(
    theme: Path, themes: List[Path], config: Dict[str, Any]
) -> None:
    themes.append(theme)
    c = _load_theme_config(theme)
    if "extends" in c:
        parent = resolve_theme_path(c["extends"])
        if parent not in themes:
            _walk_theme_hierarchy(parent, themes, config)
    config.update(c.get("config", {}))


# @lru_cache
# def _get_built_in_themes() -> Dict[str, Path]:
#     path = package_data("showyourwork2.plugins.tex", "themes")
#     themes = list(sorted(path.glob("*")))
#     return {t.name: t for t in themes}


# def _theme_path_from_name(name: str) -> Path:
#     built_in = _get_built_in_themes()
#     if name in built_in:
#         return built_in[name]
#     return package_data(name)


def resolve_theme_path(theme: Union[str, Dict[str, str]]) -> Path:
    if isinstance(theme, str):
        return _theme_path_from_name(theme)
    if "name" in theme:
        return _theme_path_from_name(theme["name"])
    return Path(theme["path"])


# def get_theme_for_document(config: Dict[str, Any], document_name: PathLike) -> Theme:
#     theme = config.get("tex", {}).get("theme", "base")

#     if isinstance(theme, (str, dict)):
#         return Theme(theme)

#     for entry in theme:
#         if document_name == entry["document"]:
#             return Theme(entry["theme"])

#     raise ValueError(f"Could not resolve theme for document '{document_name}'")
