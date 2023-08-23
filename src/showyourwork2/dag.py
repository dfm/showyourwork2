from collections import defaultdict
from functools import partial
from pathlib import Path
from typing import Any, Set

from snakemake.dag import DAG

from showyourwork2.config.models import Config


class _tracing_defaultdict(defaultdict[Path, Set[Path]]):
    def __init__(self, config: Config, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.config = config

    def __setitem__(self, key: Any, value: Any) -> None:
        if hasattr(key, "input") and hasattr(key, "output"):
            for output in key.output:
                output_path = Path(output)
                inputs = set(Path(i) for i in key.input)
                if output_path in self.config._dependency_tree:
                    self.config._dependency_tree[output_path] |= inputs
                else:
                    self.config._dependency_tree[output_path] = inputs
        super().__setitem__(key, value)


def trace_dag_dependencies(config: Config) -> None:
    def _tracing_getter(self: DAG) -> _tracing_defaultdict:
        return self._dependencies

    def _tracing_setter(self: DAG, value: Any) -> None:
        del value
        self._dependencies = _tracing_defaultdict(config, partial(defaultdict, set))

    DAG.dependencies = property(_tracing_getter, _tracing_setter)
