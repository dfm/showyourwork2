from showyourwork2.testing import run_showyourwork


def test_tex_build() -> None:
    run_showyourwork("tests/projects/plugins/tex/build")
