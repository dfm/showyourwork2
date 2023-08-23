from showyourwork2.testing import run_snakemake


def test_checkpoint_logic() -> None:
    run_snakemake("tests/projects/checkpoint", "dependencies.json", show_diff=True)
