dynamic_path = SYW__WORK_PATHS.root
build_path = SYW__WORK_PATHS.build
repo_path = SYW__REPO_PATHS.root

# Default script rules
scripts = {
    "py": "python {script} {output}",
    "ipynb": "jupyter execute {script}",
}
scripts = dict(scripts, **config.scripts)

for dynamic in config.dynamic:
    script = dynamic.script
    name = utils.rule_name("dynamic", document=script)
    message = f"Running script '{script}'"
    input = dynamic.input
    output = dynamic.output
    conda = dynamic.conda or config.conda
    if conda is not None:
        conda = repo_path / conda

    suffix = Path(script).suffix[1:]
    if suffix not in scripts:
        raise ValueError(
            f"showyourwork doesn't know how to run the script '{script}' with "
            f"type '{suffix}'; use the 'scripts' config option to add a rule"
        )
    command = scripts[suffix].format(script=script, output=" ".join(map(str, output)))

    if conda is None:
        rule:
            name:
                name
            message:
                message
            input:
                input, script=script
            output:
                output
            shell:
                command

    else:
        rule:
            name:
                name
            message:
                message
            input:
                input, script=script
            output:
                output
            conda:
                conda
            shell:
                command
