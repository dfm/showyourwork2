import platform

import pytest

from showyourwork2.testing import run_showyourwork


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="imagemagick can't be installed on Windows using conda",
)
def test_render_dag() -> None:
    run_showyourwork("tests/projects/plugins/render_dag/render", "dag.pdf")
