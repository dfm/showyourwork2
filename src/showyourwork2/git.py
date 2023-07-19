import subprocess
from functools import lru_cache
from typing import Any, Iterable, List, Optional, Union


def git(
    args: Union[Iterable[str], str], **kwargs: Any
) -> subprocess.CompletedProcess[str]:
    kwargs["check"] = kwargs.get("check", True)
    kwargs["text"] = kwargs.get("text", True)
    kwargs["capture_output"] = kwargs.get("capture_output", True)
    if isinstance(args, str):
        args = f"git {args}"
        kwargs["shell"] = kwargs.get("shell", True)
    else:
        args = ["git", *args]
        kwargs["shell"] = kwargs.get("shell", False)
    return subprocess.run(args, **kwargs)


@lru_cache
def get_repo_branch() -> str:
    return git(["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()


@lru_cache
def get_repo_sha() -> str:
    return git(["rev-parse", "HEAD"]).stdout.strip()


@lru_cache
def get_repo_tag() -> Optional[str]:
    r = git(["describe", "--exact-match", "--tags", "HEAD"], check=False)
    if r.returncode == 0:
        return r.stdout.strip()
    return None


@lru_cache
def list_files() -> List[str]:
    # List all files tracked at HEAD
    r = git(["ls-tree", "-r", "HEAD", "--name-only"])
    files: List[str] = list(r.stdout.splitlines())

    # Also list the staged files
    r = git(["diff", "--name-only", "--relative", "--cached"])
    files += list(r.stdout.splitlines())

    return list(sorted(set(files)))
