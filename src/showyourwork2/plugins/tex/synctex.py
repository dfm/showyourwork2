import gzip
from pathlib import Path

from showyourwork2.paths import PathLike


def fix_synctex_paths(build_dir: PathLike, source: PathLike, target: PathLike) -> None:
    # Read the generated SyncTeX
    with gzip.open(source, "rb") as f:
        data = f.read()

    # Rewrite the input paths to be relative to the user's tex directory if
    # that file exists
    with gzip.open(target, "wb") as f:
        for line in data.split(b"\n"):
            result = line
            if line.decode().startswith("Input:"):
                parts = line.decode().split(":")
                path = parts[-1].strip()
                if len(path):
                    path_ = Path(path)
                    try:
                        path_ = path_.relative_to(build_dir)
                    except ValueError:
                        pass
                    else:
                        if path_.exists():
                            result = ":".join(
                                parts[:-1] + [str(path_.absolute())]
                            ).encode()
            result += b"\n"
            f.write(result)
