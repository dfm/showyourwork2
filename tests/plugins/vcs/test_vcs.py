from pathlib import Path

import pytest
from pydantic import ValidationError, create_model

from showyourwork2 import git
from showyourwork2.plugins import PluginManager, vcs
from showyourwork2.testing import TemporaryDirectory, cwd, run_showyourwork


def test_vcs_build() -> None:
    run_showyourwork("tests/projects/plugins/vcs/build", git_init=True)


@pytest.mark.parametrize("repo_root", ["", "repo_root"])
def test_vcs_files(repo_root: str) -> None:
    pm = PluginManager()
    pm.register(vcs)
    Document = create_model("Document", __base__=tuple(pm.hook.document_model()))
    with TemporaryDirectory("vcs") as d:
        path = Path(d) / repo_root
        doc0 = Path("doc0.tex")
        dep0 = Path("dep0.tex")

        subdir1 = path / "subdir1"
        subdir1.mkdir(parents=True)
        doc1 = (subdir1 / "doc1.tex").relative_to(path)
        dep1 = (subdir1 / "dep1.tex").relative_to(path)

        subdir2 = path / "subdir2" / "another"
        subdir2.mkdir(parents=True)
        doc2 = (subdir2 / "doc2.tex").relative_to(path)
        dep2 = (subdir2 / "dep2.tex").relative_to(path)

        not_tracked = Path("not_tracked.tex")

        open(path / dep0, "w").close()
        open(path / dep1, "w").close()
        open(path / dep2, "w").close()
        open(path / not_tracked, "w").close()

        def run_and_check_config() -> None:
            doc = Document.model_validate({"path": doc0})
            assert dep1 in doc.dependencies
            assert dep2 in doc.dependencies
            assert not_tracked not in doc.dependencies

            doc = Document.model_validate({"path": doc1})
            assert dep1 in doc.dependencies
            assert dep2 not in doc.dependencies

            doc = Document.model_validate({"path": doc2})
            assert dep1 not in doc.dependencies
            assert dep2 in doc.dependencies

        with cwd(path):
            with pytest.raises(ValidationError):
                Document.model_validate({"path": doc0})

        # Initialize the repo at the top level of the temporary directory. If
        # repo_root is not empty, the actual project is below this top level.
        git.git(["init", "."], cwd=d)

        with cwd(path):
            # Before adding any files, we shouldn't find any dependencies
            assert Document.model_validate({"path": doc0}).dependencies == []
            assert Document.model_validate({"path": doc1}).dependencies == []
            assert Document.model_validate({"path": doc2}).dependencies == []

            # After adding the dependencies, they should be discovered
            git.git(["add", str(path / dep0), str(path / dep1), str(path / dep2)])
            run_and_check_config()

            # We should also discover the dependencies after committing
            git.commit("Initial commit")
            run_and_check_config()
