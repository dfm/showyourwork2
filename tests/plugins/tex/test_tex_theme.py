from typing import Any

import pytest

from showyourwork2.config import ValidationError, parse_config


@pytest.mark.parametrize(
    "theme",
    [
        "base",
        {"name": "base"},
        {"path": "theme/directory"},
        [
            {"document": "ms1.tex", "theme": "base"},
            {"document": "ms2.tex", "theme": {"path": "theme/directory"}},
        ],
    ],
)
def test_tex_valid_theme_config(theme: Any) -> None:
    parse_config(
        {
            "config_version": 2,
            "plugins": ["showyourwork2.plugins.tex"],
            "tex": {"theme": theme},
        }
    )


@pytest.mark.parametrize(
    "theme",
    [0, [{"theme": "base"}]],
)
def test_tex_invalid_theme_config(theme: Any) -> None:
    with pytest.raises(ValidationError):
        parse_config(
            {
                "config-version": 2,
                "plugins": ["showyourwork2.plugins.tex"],
                "tex": {"theme": theme},
            }
        )
