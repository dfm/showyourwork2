from typing import Any, Dict

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader

from showyourwork2.paths import PathLike


def render_template(template_name: str, config: Dict[str, Any]) -> str:
    env = Environment(
        block_start_string="((*",
        block_end_string="*))",
        variable_start_string="((-",
        variable_end_string="-))",
        comment_start_string="((=",
        comment_end_string="=))",
        autoescape=False,
        loader=ChoiceLoader(
            [
                FileSystemLoader("."),
                PackageLoader("showyourwork2.plugins.tex", package_path="themes"),
                PackageLoader("showyourwork2.plugins.tex", package_path="themes/base"),
            ]
        ),
    )
    return env.get_template(template_name).render(**config)


def render_style_file(
    template_name: str, target_file: PathLike, config: Dict[str, Any]
) -> None:
    txt = render_template(template_name, config)
    with open(target_file, "w") as f:
        f.write(txt)
