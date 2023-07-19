build_dir = SYW__WORK_PATHS.build
enable_synctex = config.get("tex", {}).get("synctex", True)

def _build_dependendencies_for(doc):
    deps_func = get_document_dependencies(doc)
    def impl(*_):
        deps = deps_func()
        return [build_dir / dep for dep in deps]
    return impl

for doc in SYW__DOCUMENTS:
    doc_dir = Path(doc).parent
    pdf = build_dir / Path(doc).with_suffix(".pdf")
    synctex = build_dir / Path(doc).with_suffix(".synctex.gz")

    rule:
        """
        Compile the document using ``tectonic``.
        """
        name:
            sywplug_tex__rule_name("build", "compile", document=doc)
        message:
            f"Compiling document '{Path(doc).name}'"
        input:
            dependencies=_build_dependendencies_for(doc),
            document=build_dir / doc,
            style=build_dir / doc_dir / "showyourwork.tex",
            classfile=build_dir / doc_dir / "showyourwork.sty",
        output:
            pdf,
            synctex if enable_synctex else [],
        conda:
            sywplug_tex__resource("envs", "tectonic.yml")
        shell:
            "tectonic "
            "--chatter minimal "
            + ("--synctex " if enable_synctex else "") +
            "--keep-logs "
            "--keep-intermediates "
            "{input.document:q} "

    rule:
        """
        Copy the output PDF from the output directory to the same directory as
        the source file.
        """
        name:
            sywplug_tex__rule_name("build", "output", "pdf", document=doc)
        input:
            pdf
        output:
            Path(doc).with_suffix(".pdf")
        run:
            utils.copy_file_or_directory(input[0], output[0])

    if enable_synctex:
        rule:
            """
            Copy the output SyncTeX from the output directory to the same directory as
            the source file.
            """
            name:
                sywplug_tex__rule_name("build", "output", "synctex", document=doc)
            input:
                synctex
            output:
                Path(doc).with_suffix(".synctex.gz")
            run:
                utils.copy_file_or_directory(input[0], output[0])
