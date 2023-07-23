from functools import wraps
from pathlib import Path
from typing import Callable

import nox

OLDEST_SUPPORTED_SNAKEMAKE = "7.15.2"


def snakemake_session(
    func: Callable[[nox.Session], None]
) -> Callable[[nox.Session, str], None]:
    @nox.session(venv_backend="mamba")
    @nox.parametrize(
        "python,snakemake",
        [
            (python, snakemake)
            for python in ("3.9", "3.10", "3.11")
            for snakemake in (["oldest", "latest"] if python == "3.9" else ["latest"])
        ],
    )
    @wraps(func)
    def wrapped(session: nox.Session, snakemake: str | None) -> None:
        if snakemake == "oldest":
            target = f"bioconda::snakemake=={OLDEST_SUPPORTED_SNAKEMAKE}"
        else:
            target = "bioconda::snakemake"
        session.conda_install(target, channel="conda-forge")
        func(session)

    return wrapped


@snakemake_session
def tests(session: nox.Session) -> None:
    session.install(".[test]")
    args = tuple(*session.posargs)
    if not args:
        args = ("-v", "--durations=5")
    session.run("pytest", *args)


@snakemake_session
def examples(session: nox.Session) -> None:
    session.install(".[examples]")
    examples = list(sorted(Path("examples").glob("*")))
    for example in examples:
        session.log(f"Building {example.relative_to(Path('examples'))}")
        with session.chdir(example.resolve()):
            session.run("showyourwork2", "clean", "--deep")
            session.run("showyourwork2", "build")


@nox.session
def lint(session: nox.Session) -> None:
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files")
