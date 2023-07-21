import os
import subprocess
import sys
from pathlib import Path
from shutil import rmtree
from typing import Any, Callable, Iterable, Optional, Tuple

import click
import snakemake

from showyourwork2 import logging, paths
from showyourwork2.config import load_config
from showyourwork2.version import __version__


@click.group()
@click.version_option(
    __version__,
    "--version",
    "-v",
    package_name="showyourwork2",
    message="%(version)s",
)
def main() -> None:
    """Easily build open-source, reproducible scientific articles."""
    pass


def build_arguments(func: Callable[..., Any]) -> Callable[..., Any]:
    func = click.argument("snakemake_args", nargs=-1, type=click.UNPROCESSED)(func)
    func = click.option(
        "--conda-frontend",
        default=None,
        type=str,
        help="The conda frontend to use; passed to snakemake",
    )(func)
    func = click.option(
        "-c",
        "--cores",
        default="all",
        help="Number of cores to use; passed to snakemake",
    )(func)
    func = click.option(
        "-f",
        "--configfile",
        type=click.Path(exists=True),
        help="A showyourwork configuration file",
    )(func)
    func = click.option(
        "-v", "--verbose", is_flag=True, help="Print verbose output to the console"
    )(func)
    return func


@main.command(  # type: ignore[attr-defined]
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@build_arguments
def build(
    verbose: bool,
    configfile: Optional[paths.PathLike],
    cores: str,
    conda_frontend: Optional[str],
    snakemake_args: Iterable[str],
) -> None:
    """Build an article in the current working directory."""
    _build(
        verbose=verbose,
        configfile=configfile,
        cores=cores,
        conda_frontend=conda_frontend,
        snakemake_args=snakemake_args,
    )


@main.command(  # type: ignore[attr-defined]
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@build_arguments
@click.option(
    "--deep",
    is_flag=True,
    help="Also delete the temporary 'showyourwork' and 'snakemake' directories",
)
def clean(
    verbose: bool,
    configfile: Optional[paths.PathLike],
    cores: str,
    conda_frontend: Optional[str],
    snakemake_args: Iterable[str],
    deep: bool,
) -> None:
    """Delete all the outputs associated with a previous build."""
    snakemake_args = list(snakemake_args) + ["--delete-all-output"]
    _build(
        verbose=verbose,
        configfile=configfile,
        cores=cores,
        conda_frontend=conda_frontend,
        snakemake_args=snakemake_args,
    )

    # We run the clean a second time to handle the fact that the first pass
    # won't delete outputs that occur before the checkpoint.
    _build(
        verbose=verbose,
        configfile=configfile,
        cores=cores,
        conda_frontend=conda_frontend,
        snakemake_args=snakemake_args,
    )

    if deep:
        config_file, cwd, _ = get_config_file_and_project_root(
            snakemake_args=snakemake_args, config_file=configfile
        )
        config = load_config(config_file)
        logger = logging.get_logger(config)
        syw_dir = cwd / paths.work(config).root
        if syw_dir.is_dir():
            logger.info(f"Deleting directory {syw_dir}")
            rmtree(syw_dir)
        snakemake_dir = cwd / ".snakemake"
        if snakemake_dir.is_dir():
            logger.info(f"Deleting directory {snakemake_dir}")
            rmtree(snakemake_dir)


def _build(
    verbose: bool,
    configfile: Optional[paths.PathLike],
    cores: str,
    conda_frontend: Optional[str],
    snakemake_args: Iterable[str],
) -> None:
    """Build an article in the current working directory."""
    if verbose:
        snakemake_args = list(snakemake_args) + ["--config", "verbose=True"]

    run_snakemake(
        paths.package_data("showyourwork2", "workflow", "Snakefile"),
        config_file=configfile,
        cores=cores,
        conda_frontend=conda_frontend,
        check=True,
        extra_args=snakemake_args,
    )


def get_config_file_and_project_root(
    snakemake_args: Iterable[str] = (), config_file: Optional[paths.PathLike] = None
) -> Tuple[Path, Path, Iterable[str]]:
    if config_file is None:
        # Parse the snakemake arguments using the snakemake parser to identify if
        # there are any targets included.
        snakemake_parser = snakemake.get_argument_parser()
        parsed_args = snakemake_parser.parse_args(list(snakemake_args))

        # Check if any of the targets are paths. We're defining paths as anything
        # with multiple "parts", since anything without multiple parts will be found
        # anyways. If so, we'll use those to find the project root.
        target_paths = [t for t in parsed_args.target if len(Path(t).parts) > 1]

        cwd = paths.find_project_root(*target_paths)
        config_file = cwd / "showyourwork.yml"
        if not config_file.is_file():
            config_file = cwd / "showyourwork.yaml"
        if not config_file.is_file():
            raise RuntimeError(
                f"No config file found in project root ({cwd}). "
                "Please specify a configuration file using the '--configfile' command "
                "line argument."
            )
    else:
        cwd = Path(config_file).parent
        target_paths = []
    return Path(config_file), cwd, target_paths


def run_snakemake(
    snakefile: paths.PathLike,
    config_file: Optional[paths.PathLike] = None,
    cores: str = "1",
    conda_frontend: Optional[str] = None,
    check: bool = True,
    extra_args: Iterable[str] = (),
) -> int:
    # Find the project root (that's where we execute snakemake from), and the
    # configuration file there.
    config_file, cwd, target_paths = get_config_file_and_project_root(
        snakemake_args=extra_args, config_file=config_file
    )

    # Update any target paths to be relative to the project root
    extra_args = [
        str(Path(a).resolve().relative_to(cwd)) if a in target_paths else a
        for a in extra_args
    ]

    # If the user didn't specify a conda frontend, then we'll try to use mamba
    # if it exists. If not, we assume that conda is available and let snakemake
    # handle any issues.
    if conda_frontend is None:
        # TODO(dfm): Log the result of this choice.
        from ensureconda.api import ensureconda

        if (
            ensureconda(
                mamba=True,
                micromamba=False,
                conda=False,
                conda_exe=False,
                no_install=True,
            )
            is not None
        ):
            conda_frontend = "mamba"
        else:
            conda_frontend = "conda"

    env = dict(os.environ)
    cmd = [
        "snakemake",
        "--cores",
        f"{cores}",
        "--use-conda",
        "--conda-frontend",
        conda_frontend,
        "--reason",
        "--configfile",
        str(config_file),
        "-s",
        str(snakefile),
    ] + list(extra_args)
    result = subprocess.run(cmd, env=env, check=False, cwd=cwd)
    if check and result.returncode:
        sys.exit(result.returncode)
    return result.returncode
