from typing import Any

import pytest
from pydantic import ValidationError

from showyourwork2.config import parse_config
from showyourwork2.paths import package_data
from showyourwork2.plugins.tex.models import ThemeModel
from showyourwork2.plugins.tex.theme import Theme


@pytest.mark.parametrize(
    "theme",
    [
        "base",
        {"name": "base"},
        {"path": "theme/directory"},
    ],
)
def test_tex_theme_config_valid(theme: Any) -> None:
    parse_config(
        {
            "config_version": 2,
            "plugins": ["showyourwork2.plugins.tex"],
            "documents": [
                {"path": "ms.tex", "theme": theme},
            ],
        }
    )


@pytest.mark.parametrize(
    "theme",
    [0, [{"theme": "base"}]],
)
def test_tex_theme_config_invalid(theme: Any) -> None:
    with pytest.raises(ValidationError):
        parse_config(
            {
                "config-version": 2,
                "plugins": ["showyourwork2.plugins.tex"],
                "documents": [
                    {"path": "ms.tex", "theme": theme},
                ],
            }
        )


@pytest.mark.parametrize(
    "spec",
    [
        "base",
        {"name": "base"},
        {"path": str(package_data("showyourwork2.plugins.tex", "themes/base"))},
    ],
)
def test_base_theme(spec: Any) -> None:
    model = ThemeModel.model_validate(spec)
    theme = Theme(model)
    assert len(theme._hierarchy) == 1
    assert theme._hierarchy[0] == theme.path
    assert theme.resources_for_template("dependencies") == {}
    assert theme.resources_for_template("build") == {}
    theme.render("dependencies.tex", {})
    theme.render("build.tex", {})


@pytest.mark.parametrize(
    "spec",
    [
        "classic",
        {"name": "classic"},
        {"path": str(package_data("showyourwork2.plugins.tex", "themes/classic"))},
    ],
)
def test_classic_theme(spec: Any) -> None:
    model = ThemeModel.model_validate(spec)
    theme = Theme(model)
    assert len(theme._hierarchy) == 2  # noqa: PLR2004
    assert theme._hierarchy[0] == theme.path
    assert theme._hierarchy[1].name == "base"
    assert theme.resources_for_template("dependencies") == {}
    assert theme.resources_for_template("build") != {}
    theme.render("dependencies.tex", {})
    theme.render("build.tex", {})
