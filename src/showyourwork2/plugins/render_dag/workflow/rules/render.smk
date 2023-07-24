sywplug_render_dag__rule_name = partial(
    utils.rule_name, plugin="showyourwork2.plugins.render_dag"
)
sywplug_render_dag__resource = partial(
    package_data, "showyourwork2.plugins.render_dag", "workflow"
)

SUPPORTED_FIGURE_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg"]
dag_directory = SYW__WORK_PATHS / "render_dag"
dag_filename = config.get("render_dag", {}).get("output", "dag.pdf")

rule:
    name:
        sywplug_render_dag__rule_name("config")
    input:
        rules.syw__dag.output,
        ensure_all_document_dependencies,
    output:
        dag_directory / "_render_dag_config.json"
    run:
        with open(output[0], "w") as f:
            utils.json_dump(config, f)

def generated_files(*_):
    deps = []
    for doc in SYW__DOCUMENTS:
        deps.extend(get_document_dependencies(doc)())
    return [d for d in set(deps) if Path(d).suffix in SUPPORTED_FIGURE_EXTENSIONS]

rule:
    name:
        sywplug_render_dag__rule_name("thumbnails")
    message:
        "Rendering thumbnails for generated figures"
    input:
        rules.syw__dag.output,
        files=generated_files,
        script=sywplug_render_dag__resource("scripts", "render_thumbnails.py"),
    output:
        directory(SYW__WORK_PATHS.root / "thumbnails")
    conda:
        sywplug_render_dag__resource("envs", "render_thumbnails.yml")
    shell:
        "python {input.script:q} "
        "--output {output:q} "
        "{input.files:q} "

rule:
    name:
        sywplug_render_dag__rule_name("render")
    message:
        f"Rendering DAG to '{dag_filename}'"
    input:
        config=dag_directory / "_render_dag_config.json",
        thumbnails=SYW__WORK_PATHS.root / "thumbnails",
        script=sywplug_render_dag__resource("scripts", "render_dag.py")
    output:
        dag_directory / dag_filename
    conda:
        sywplug_render_dag__resource("envs", "render_dag.yml")
    shell:
        "python {input.script:q} "
        "--config {input.config:q} "
        "--thumbnails-path {input.thumbnails:q} "
        "--output {output:q} "


rule:
    name:
        sywplug_render_dag__rule_name("copy")
    input:
        dag_directory / dag_filename
    output:
        dag_filename
    run:
        utils.copy_file_or_directory(input[0], output[0])
