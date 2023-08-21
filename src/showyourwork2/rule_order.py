from typing import TYPE_CHECKING, Optional

from showyourwork2.plugins import PluginManager

if TYPE_CHECKING:
    import snakemake


def get_rule_priority(
    rule: "snakemake.ruleinfo.RuleInfo",
    plugin_manager: Optional[PluginManager] = None,
) -> int:
    if plugin_manager is not None:
        priority = plugin_manager.hook.rule_priority(rule=rule)
        if priority:
            return min(priority)
    if rule.name.startswith("syw__"):
        return 0
    elif rule.name.startswith("sywplug_"):
        return 1
    return 100


def fix_rule_order(
    workflow: "snakemake.workflow.Workflow",
    plugin_manager: Optional[PluginManager] = None,
) -> None:
    """Update the rule order for all rules defined by the workflow

    The logic here is that we want all user-defined rules to be higher priority
    than showyourwork (and plugin) rules, and we want all plugin rules to be
    higher priority than the base showyourwork rules. Whether or not a rule is a
    showyourwork or plugin rule is determined by the prefix of the rule name,
    ``syw__`` and ``sywplug__`` respectively.
    """
    rules = list(workflow.rules)
    for n, r1 in enumerate(rules):
        p1 = get_rule_priority(r1, plugin_manager=plugin_manager)
        for r2 in rules[n + 1 :]:
            p2 = get_rule_priority(r2, plugin_manager=plugin_manager)
            if p1 > p2:
                workflow.ruleorder(r1.name, r2.name)
            elif p1 < p2:
                workflow.ruleorder(r2.name, r1.name)
