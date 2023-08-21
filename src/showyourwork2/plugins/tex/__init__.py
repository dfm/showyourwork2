from pathlib import Path
from typing import Type

from showyourwork2.paths import package_data
from showyourwork2.plugins.hooks import hookimpl
from showyourwork2.plugins.tex.models import Document


@hookimpl
def snakefile() -> Path:
    return package_data("showyourwork2.plugins.tex", "workflow", "Snakefile")


@hookimpl
def document_model() -> Type[Document]:
    return Document
