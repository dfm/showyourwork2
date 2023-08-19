from showyourwork2.plugins.tex.theme import Theme
from showyourwork2.paths import path_to_rule_name

sywplug_tex__rule_name = partial(
    utils.rule_name, plugin="showyourwork2.plugins.tex"
)
sywplug_tex__resource = partial(
    package_data, "showyourwork2.plugins.tex", "workflow"
)

def sywplug_tex__local_or_provided_style(document):
    """Get the path to the showyourwork.sty file. We prefer to use the one
    provided by the user if it exists, but will provide our own if not.
    """
    path = Path(document).parent / "showyourwork.sty"
    if path.is_file():
        return path
    else:
        return sywplug_tex__resource("resources", "showyourwork.sty")


for base_path in [SYW__WORK_PATHS / "dependencies", SYW__WORK_PATHS / "build"]:
    slug = base_path.name

    for document in SYW__DOCUMENTS:
        doc = document.path
        doc_dir = Path(doc).parent
        work_dir = base_path / doc

        # Work out the theme resources
        theme = Theme(document.theme)
        theme_resources = theme.resources_for_template(slug)

        rule:
            """
            Copy explicit dependencies to the working directory.
            """
            name:
                sywplug_tex__rule_name("copy", "dependencies", "to", slug, document=doc)
            input:
                "{file}"
            output:
                work_dir / "{file}"
            run:
                utils.copy_file_or_directory(input[0], output[0])

        for resource_out, resource_in in theme_resources.items():
            rule:
                """
                Copy theme resources to the working directory.
                """
                name:
                    sywplug_tex__rule_name("copy", "resources", "for", slug, path_to_rule_name(resource_in), document=doc)
                input:
                    resource_in
                output:
                    work_dir / doc_dir / resource_out
                run:
                    utils.copy_file_or_directory(input[0], output[0])

        rule:
            """
            Copy the appropriate ``showyourwork`` style file to the work
            directory.
            """
            name:
                sywplug_tex__rule_name("style", slug, document=doc)
            input:
                [work_dir / doc_dir / f for f in theme_resources.keys()],
                dependencies_file=SYW__WORK_PATHS.dependencies_for(doc) if slug == "build" else [],
            output:
                work_dir / doc_dir / "showyourwork.tex"
            params:
                slug=slug,
                config=config,
                theme=theme,
            run:
                import json
                if input.dependencies_file:
                    with open(input.dependencies_file) as f:
                        dependencies = json.load(f)
                else:
                    dependencies = None

                params.theme.render_to(
                    template_name=f"{params.slug}.tex",
                    target_file=output[0],
                    config=params.config,
                    dependencies=dependencies,
                )

        rule:
            """
            Copy the ``showyourwork`` class file to the work directory. If
            the project contains a ``showyourwork.sty`` file in the same
            directory as the document, we use that instead of the standard
            one provided by showyourwork, allowing users to customize
            behavior.
            """
            name:
                sywplug_tex__rule_name("class", slug, document=doc)
            input:
                sywplug_tex__local_or_provided_style(doc)
            output:
                work_dir / doc_dir / "showyourwork.sty"
            run:
                utils.copy_file_or_directory(input[0], output[0])

        rule:
            """
            Copy the document from the top level working directory to the
            current working directory.
            """
            name:
                sywplug_tex__rule_name("doc", slug, document=doc)
            input:
                SYW__WORK_PATHS.root / doc
            output:
                work_dir / doc
            run:
                utils.copy_file_or_directory(input[0], output[0])
