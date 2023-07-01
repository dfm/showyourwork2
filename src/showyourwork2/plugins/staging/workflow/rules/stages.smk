from pathlib import Path
from showyourwork2 import utils
from showyourwork2.plugins.staging import stages
from showyourwork2.plugins.staging.config import _CONFIG

previously_included = set()
for name, stage in stages.STAGES.items():
    # Custom rules for uploading and downloading this type of stage
    snakefile = stage.snakefile()
    if snakefile not in previously_included:
        include: snakefile
        previously_included.add(snakefile)


# A rule to upload all stages
working_directory = Path(_CONFIG.get("working_directory", "staging"))
rule staging__upload:  # Note: using a simple rule name to make this easy to target
    message:
        "Uploading all stages"
    input:
        [
            stage.upload_flag_file
            for stage in stages.STAGES.values()
            if not stage.restore
        ]
    output:
        touch(working_directory / "staging_upload.done")
