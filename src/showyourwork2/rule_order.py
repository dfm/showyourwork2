import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import snakemake

from showyourwork2.config.models import Config


def get_rule_priority(config: Config, rule: "snakemake.ruleinfo.RuleInfo") -> int:
    for plugin in config.plugins:
        mod = importlib.import_module(plugin)
        if hasattr(mod, "get_rule_priority"):
            priority = mod.get_rule_priority(config, rule)
            if priority is not None:
                return priority

    if rule.name.startswith("syw__"):
        return 0
    elif rule.name.startswith("sywplug_"):
        return 1
    return 100


def fix_rule_order(config: Config, workflow: "snakemake.workflow.Workflow") -> None:
    """Update the rule order for all rules defined by the workflow

    The logic here is that we want all user-defined rules to be higher priority
    than showyourwork (and plugin) rules, and we want all plugin rules to be
    higher priority than the base showyourwork rules. Whether or not a rule is a
    showyourwork or plugin rule is determined by the prefix of the rule name,
    ``syw__`` and ``sywplug__`` respectively.
    """
    rules = list(workflow.rules)
    for n, r1 in enumerate(rules):
        p1 = get_rule_priority(config, r1)
        for r2 in rules[n + 1 :]:
            p2 = get_rule_priority(config, r2)
            if p1 > p2:
                workflow.ruleorder(r1.name, r2.name)
            elif p1 < p2:
                workflow.ruleorder(r2.name, r1.name)
