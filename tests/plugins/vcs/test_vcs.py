from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

import pytest

from showyourwork2 import git
from showyourwork2.plugins import vcs
from showyourwork2.testing import TemporaryDirectory, cwd, run_showyourwork


def test_vcs_build() -> None:
    run_showyourwork("tests/projects/plugins/vcs/build", git_init=True)


@pytest.mark.parametrize("repo_root", ["", "repo_root"])
def test_vcs_files(repo_root: str) -> None:
    with TemporaryDirectory("vcs") as d:
        path = Path(d) / repo_root
        doc0 = "doc0.tex"
        dep0 = "dep0.tex"

        subdir1 = path / "subdir1"
        subdir1.mkdir(parents=True)
        doc1 = str((subdir1 / "doc1.tex").relative_to(path))
        dep1 = str((subdir1 / "dep1.tex").relative_to(path))

        subdir2 = path / "subdir2" / "another"
        subdir2.mkdir(parents=True)
        doc2 = str((subdir2 / "doc2.tex").relative_to(path))
        dep2 = str((subdir2 / "dep2.tex").relative_to(path))

        not_tracked = "not_tracked.tex"

        open(path / dep0, "w").close()
        open(path / dep1, "w").close()
        open(path / dep2, "w").close()
        open(path / not_tracked, "w").close()

        config: Dict[str, Any] = {"documents": {doc0: [], doc1: [], doc2: []}}

        def run_and_check_config(config: Dict[str, Any]) -> None:
            c = deepcopy(config)
            vcs.postprocess_config(c)

            assert dep1 in c["documents"][doc0]
            assert dep2 in c["documents"][doc0]
            assert not_tracked not in c["documents"][doc0]

            assert dep1 in c["documents"][doc1]
            assert dep2 not in c["documents"][doc1]

            assert dep1 not in c["documents"][doc2]
            assert dep2 in c["documents"][doc2]

        with cwd(path):
            with pytest.raises(RuntimeError):
                vcs.postprocess_config(config)

        # Initialize the repo at the top level of the temporary directory. If
        # repo_root is not empty, the actual project is below this top level.
        git.git(["init", "."], cwd=d)

        with cwd(path):
            # Before adding any files, we shouldn't find any dependencies
            c = dict(**config)
            vcs.postprocess_config(c)
            assert c["documents"][doc0] == []
            assert c["documents"][doc1] == []
            assert c["documents"][doc2] == []

            # After adding the dependencies, they should be discovered
            git.git(["add", str(path / dep0), str(path / dep1), str(path / dep2)])
            run_and_check_config(config)

            # Just check that this didn't change the original config
            assert config["documents"][doc0] == []

            # We should also discover the dependencies after committing
            git.commit("Initial commit")
            run_and_check_config(config)
