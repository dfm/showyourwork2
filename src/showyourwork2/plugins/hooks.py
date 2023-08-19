import pluggy
from pydantic import BaseModel

hookspec = pluggy.HookspecMarker("showyourwork2")
hookimpl = pluggy.HookimplMarker("showyourwork2")


@hookspec
def config_model() -> BaseModel:
    ...


@hookspec
def document_model() -> BaseModel:
    ...
