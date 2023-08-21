build_path = SYW__WORK_PATHS.build

for static_file in config.static:
    rule:
        name:
            utils.rule_name("static", document=static_file)
        input:
            static_file
        output:
            directory(build_path / static_file) if Path(static_file).is_dir() else build_path / static_file
        run:
            utils.copy_file_or_directory(input[0], output[0])
