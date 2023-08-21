from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

import pytest
from pydantic import ValidationError

from showyourwork2.config.config import load_config, normalize_keys


def test_normalize_keys() -> None:
    result = normalize_keys(
        {
            "a-b": 1,
            "c-d": {"e-f": 2, "gh": [{"i-j": 3}, {"k-l": 4}]},
        }
    )
    assert result == {
        "a_b": 1,
        "c_d": {"e_f": 2, "gh": [{"i_j": 3}, {"k_l": 4}]},
    }


@contextmanager
def temp_config_file(body: str) -> Generator[Path, None, None]:
    with TemporaryDirectory() as d:
        name = Path(d) / "config.yml"
        with open(name, "w") as f:
            f.write(body)
        yield name


@pytest.mark.parametrize("sep", ["-", "_"])
def test_minimal_valid(sep: str) -> None:
    with temp_config_file(f"config{sep}version: 2\ndocuments: ['ms.tex']") as f:
        load_config(f)


def test_missing_version() -> None:
    with temp_config_file("") as f:
        with pytest.raises(ValidationError):
            load_config(f)


def test_invalid_version() -> None:
    with temp_config_file("config-version: 1") as f:
        with pytest.raises(ValidationError):
            load_config(f)


def test_invalid_schema() -> None:
    with temp_config_file(
        """
config-version: 2
conda: 1
"""
    ) as f:
        with pytest.raises(ValidationError):
            load_config(f)


def test_invalid_nested_schema() -> None:
    with temp_config_file(
        """
config-version: 2
documents:
    - path: "test"
      dependencies: 1
"""
    ) as f:
        with pytest.raises(ValidationError):
            load_config(f)


def test_invalid_property() -> None:
    with temp_config_file(
        """
config-version: 2
not-allowed: "test"
"""
    ) as f:
        with pytest.raises(ValidationError):
            load_config(f)


def test_document() -> None:
    with temp_config_file(
        """
config-version: 2
documents:
    - path: test1
    - test2
    - path: test3
      dependencies:
        - dep1
        - dep2
"""
    ) as f:
        config = load_config(f)
        assert config.documents[0].path == Path("test1")
        assert config.documents[0].dependencies == []
        assert config.documents[1].path == Path("test2")
        assert config.documents[1].dependencies == []
        assert config.documents[2].path == Path("test3")
        assert config.documents[2].dependencies == [Path("dep1"), Path("dep2")]
