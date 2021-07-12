import glob
from pathlib import Path
import os


# Paths
TEX_FILES = glob.glob(str(Path("tex") / "*"))
FIGURE_SCRIPTS = glob.glob(str(Path("figures") / "*.py"))
PYTHON_TESTS = glob.glob(str(Path("tests") / "*"))

# Config
configfile: "config.yml"

# Generate the metadata file from direct user input
rule meta:
    output: ".cortex/data/meta.json"
    shell: "cd .cortex && python user_prompt.py"

# Generate figures (TODO)
rule figures:
    input: "figures/{figure}.py"
    output: "figures/{figure}{suffix,(_.*)?}.pdf"
    shell: "cd figures && python {wildcards.figure}.py"

# Compile the PDF
rule pdf:
    input: "tex/ms.tex", "tex/bib.bib", TEX_FILES, FIGURE_SCRIPTS, PYTHON_TESTS
    output: "ms.pdf"
    run: 
        shell("cd .cortex && python generate_sty.py")
        shell("cd .cortex && python check_git_status.py")
        STYLE_FILES = glob.glob(str(Path(".cortex") / "styles" / "*"))
        TEMP_FILES = glob.glob(str(Path("figures") / "*.py.cortex"))

        def clean():
            if not config["debug"]:
                for f in STYLE_FILES:
                    shell("rm tex/{}".format(Path(f).name))
                for f in TEMP_FILES:
                    shell("rm {}".format(f))

        try:
            for f in STYLE_FILES:
                shell("cp {} tex/".format(f))
            if config["debug"]:
                shell("tectonic --keep-logs --print tex/ms.tex")
            else:
                shell("tectonic tex/ms.tex")
            shell("mv tex/ms.pdf .")
            clean()
        except Exception as e:
            clean()
            raise e