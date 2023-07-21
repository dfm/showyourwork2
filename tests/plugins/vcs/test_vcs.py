from pathlib import Path
from typing import Iterable

from showyourwork2 import cli
from showyourwork2.git import git
from showyourwork2.paths import find_project_root
from showyourwork2.testing import cwd, run_showyourwork


def add_file_and_run(
    tmp_dir: Path,
    ms_dir: Path,
    args: Iterable[str] = (),
) -> None:
    target = ms_dir / "subdir" / "another" / "file.tex"
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w") as f:
        f.write(r"\sywvcs")

    with open(ms_dir / "ms.tex", "w") as f:
        f.write(
            r"""
\documentclass{article}
\usepackage{showyourwork}
\usepackage{syw-vcs-simple}
\begin{document}

This is a simple document.
\include{subdir/another/file.tex}

\end{document}
"""
        )

    # Add a new file, but don't commit it
    with cwd(tmp_dir):
        # Clean the repo
        cli._build(
            verbose=False,
            configfile=None,
            cores="1",
            conda_frontend="mamba",
            snakemake_args=list(args) + ["--delete-all-output"],
        )

        # Add the new file
        git(["add", str(target)])

        # Run a build
        find_project_root.cache_clear()
        cli._build(
            verbose=False,
            configfile=None,
            cores="1",
            conda_frontend="mamba",
            snakemake_args=args,
        )


def test_vcs_build() -> None:
    with run_showyourwork("tests/projects/plugins/vcs/build", git_init=True) as d:
        add_file_and_run(d, d / "src")


def test_vcs_repo_root() -> None:
    """
    Tests to make sure that the paths are correct when the git repo is not the
    root of the project.
    """
    with run_showyourwork(
        "tests/projects/plugins/vcs/repo_root", "repo/src/ms.pdf", git_init=True
    ) as d:
        add_file_and_run(
            d,
            d / "repo" / "src",
            args=("repo/src/ms.pdf",),
        )
        assert (
            d
            / "repo"
            / ".showyourwork"
            / "build"
            / "src"
            / "subdir"
            / "another"
            / "file.tex"
        ).is_file()
