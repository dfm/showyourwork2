from pathlib import Path
from typing import TYPE_CHECKING

import pluggy
from pydantic import BaseModel

if TYPE_CHECKING:
    import snakemake


hookspec = pluggy.HookspecMarker("showyourwork2")
hookimpl = pluggy.HookimplMarker("showyourwork2")


@hookspec
def snakefile() -> Path:
    raise NotImplementedError


@hookspec
def config_model() -> BaseModel:
    raise NotImplementedError


@hookspec
def document_model() -> BaseModel:
    raise NotImplementedError


@hookspec
def rule_priority(rule: "snakemake.ruleinfo.RuleInfo") -> int:
    del rule
    raise NotImplementedError
