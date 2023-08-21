from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from showyourwork2.plugins.hooks import hookimpl
from showyourwork2.version import __version__

REQUIRED_CONFIG_VERSION = 2


class GitHubInfo(BaseModel):
    owner: str
    repo: str


class DynamicFile(BaseModel):
    script: Path
    command: Optional[str] = None
    conda: Optional[Path] = None
    input: List[Path] = []
    output: List[Path] = []

    @model_validator(mode="before")
    @classmethod
    def one_or_more_outputs(cls, data: Any) -> Any:
        if not isinstance(data, dict) or "output" not in data:
            return data
        output = data.get("output", [])
        if isinstance(output, (Path, str)):
            output = [output]
        data["output"] = output
        return data


class Document(BaseModel):
    path: Path
    dependencies: List[Path] = []
    artifacts: List[Path] = []

    @model_validator(mode="before")
    @classmethod
    def allow_raw_document_path(cls, data: Any) -> Any:
        if isinstance(data, (Path, str)):
            return {"path": data}
        return data


class Config(BaseModel):
    config_version: int

    working_directory: Optional[Path] = None
    verbose: bool = False

    plugins: List[str] = ["showyourwork2.plugins.tex"]

    github: Optional[GitHubInfo] = None

    conda: Optional[Path] = None

    static: List[Path] = []
    dynamic: List[DynamicFile] = []
    scripts: Dict[str, str] = {}
    datasets: Dict[str, List[Path]] = {}
    snakefiles: List[Path] = []

    _document_dependencies: Dict[Path, List[Path]] = {}
    _dependency_tree: Dict[Path, List[Path]] = {}
    _dependency_tree_simple: Dict[Path, List[Path]] = {}

    model_config = ConfigDict(extra="forbid")

    @field_validator("config_version")
    @classmethod
    def allowed_config_version(cls, config_version: int) -> int:
        if config_version != REQUIRED_CONFIG_VERSION:
            raise ValueError(
                f"Version {__version__} of showyourwork requires configuration with "
                f"version {REQUIRED_CONFIG_VERSION} of the specification, but the "
                f"config file specifies the version as {config_version}"
            )
        return config_version

    @model_validator(mode="after")
    def expect_at_least_one_document(self) -> "Config":
        if not self.documents:
            raise ValueError("No documents were specified in the configuration file")
        return self


@hookimpl
def document_model() -> Type[Document]:
    return Document


@hookimpl
def config_model() -> Type[Config]:
    return Config
