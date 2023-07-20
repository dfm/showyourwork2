from showyourwork2.testing import run_showyourwork


def test_vcs_build() -> None:
    run_showyourwork("tests/projects/plugins/vcs/build", git_init=True)
