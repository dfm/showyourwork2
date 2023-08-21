"""
Rules in this Snakefile are responsible for parsing the dependencies of any TeX
documents in the project and writing them in a standard JSON format. This works
by redefining TeX macros like ``\includegraphics`` and ``\input`` to write to a
log file instead of including the file. After running this hacked TeX file
through ``tectonic``, the log file is parsed to extract the dependency
structure. Of note, this procedure depends on the TeX documents including the
``showyourwork`` package, and the workflow will fail if it is not included.
"""

from showyourwork2.plugins.tex.dependencies import parse_dependencies

# We only define these rules for documents explicitly listed in the config file
# because we otherwise end up with ambigious rules for other TeX files. So here
# we're looping over all the document paths.
for document in SYW__DOCUMENTS:
    doc = document.path
    explicit_deps = document.dependencies
    doc_dir = Path(doc).parent
    deps_dir = SYW__WORK_PATHS / "dependencies" / doc
    xml =  deps_dir / doc_dir / f"{Path(doc).with_suffix('').name}.dependencies.xml"

    rule:
        """
        Run tectonic to produce the XML log file tracking all data dependencies.
        """
        name:
            sywplug_tex__rule_name("dependecies", "list", document=doc)
        message:
            f"Listing dependencies of '{Path(doc).name}'"
        input:
            document=deps_dir / doc,
            dependencies=[deps_dir / d for d in explicit_deps],
            style=deps_dir / doc_dir / "showyourwork.tex",
            classfile=deps_dir / doc_dir / "showyourwork.sty",
        output:
            xml
        conda:
            sywplug_tex__resource("envs", "tectonic.yml")
        shell:
            "tectonic "
            "--chatter minimal "
            "--keep-logs "
            "--keep-intermediates "
            "{input.document:q} "

    rule:
        """
        Parse the XML log file to produce a JSON file with the correctly
        formatted dependency structure.
        """
        name:
            sywplug_tex__rule_name("dependencies", "parse", document=doc)
        message:
            f"Parsing dependencies of '{Path(doc).name}'"
        input:
            xml
        output:
            SYW__WORK_PATHS.dependencies_for(doc)
        params:
            config=config
        run:
            base_path = Path(doc).parent
            parse_dependencies(
                input[0], output[0], base_path, SYW__REPO_PATHS.root, params.config
            )

rule:
    """
    A dummy rule that can be used to produce the dependencies for all TeX
    documents without knowing their specific names.
    """
    name:
        sywplug_tex__rule_name("dependencies")
    input:
        [SYW__WORK_PATHS.dependencies_for(doc.path) for doc in SYW__DOCUMENTS]
    output:
        touch(SYW__WORK_PATHS.flag("tex_dependencies"))
