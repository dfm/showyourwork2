def _build_dependendencies_for(document):
    build_dir = SYW__WORK_PATHS.build / document.path
    deps_func = get_document_dependencies(document)
    def impl(*_):
        deps = deps_func()
        return [build_dir / dep for dep in deps]
    return impl

for document in SYW__DOCUMENTS:
    doc = document.path
    enable_synctex = document.synctex
    doc_dir = Path(doc).parent
    build_dir = SYW__WORK_PATHS.build / doc
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
            dependencies=_build_dependendencies_for(document),
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
            "--synctex "
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
            Copy the output SyncTeX from the output directory to the same
            directory as the source file.
            """
            name:
                sywplug_tex__rule_name("build", "output", "synctex", document=doc)
            input:
                synctex
            output:
                Path(doc).with_suffix(".synctex.gz")
            params:
                build_dir=build_dir.resolve(),
            run:
                from showyourwork2.plugins.tex.synctex import fix_synctex_paths

                fix_synctex_paths(params.build_dir, input[0], output[0])
