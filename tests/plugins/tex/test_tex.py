import gzip

from showyourwork2.testing import run_showyourwork


def test_tex_build() -> None:
    with run_showyourwork("tests/projects/plugins/tex/build") as d:
        # We also check that the synctex file paths have been properly corrected
        with gzip.open(d / "ms.synctex.gz", "rb") as f:
            data = f.read()
        expected_path = str((d / "ms.tex").resolve())
        assert any(
            line.decode().split(":")[-1] == expected_path for line in data.splitlines()
        )


def test_tex_dependencies() -> None:
    run_showyourwork(
        "tests/projects/plugins/tex/dependencies", "sywplug_tex__dependencies"
    )


def test_tex_dependencies_subdir() -> None:
    """Test for dependency discovery when manuscript is in a subdirectory"""
    run_showyourwork("tests/projects/plugins/tex/dependencies_subdir")
