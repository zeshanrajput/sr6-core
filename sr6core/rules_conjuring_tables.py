"""
Downtime Spirit Binding & Sprite Registration Probability Engine for SR6.
Evaluates downtime binding/registering under standard SRM Downtime rules where
both the runner and the entity MUST BUY HITS (1 hit per 4 full dice).
Yields deterministic guaranteed tasks/services and terminates when net hits <= 0.
"""

from typing import Dict, Any, List, Optional


def calculate_downtime_binding_table(
    caster_pool: int,
    entity_type: str = "Spirit",
    pool_name: str = "Conjuring (Summoning)"
) -> Dict[str, Any]:
    """
    Computes deterministic downtime binding/registering tasks under SRM Buying Hits rules.
    Runner and entity must buy hits (1 hit per 4 full dice, floor).
    Table ends before guaranteed net hits reach 0.
    """
    pc_bought_hits = caster_pool // 4

    rows = []
    max_force = 12

    for force in range(1, max_force + 1):
        entity_opposed_pool = force * 2
        entity_bought_hits = entity_opposed_pool // 4  # force // 2

        net_hits = pc_bought_hits - entity_bought_hits

        # Exact cutoff: cease before or when guaranteed net hits drop to <= 0
        if net_hits <= 0:
            break

        rows.append({
            "force": force,
            "entity_pool": entity_opposed_pool,
            "entity_hits": entity_bought_hits,
            "pc_pool": caster_pool,
            "pc_hits": pc_bought_hits,
            "net_hits": net_hits,
        })

    return {
        "entity_type": entity_type,
        "pool_name": pool_name,
        "pc_pool": caster_pool,
        "pc_bought_hits": pc_bought_hits,
        "rows": rows,
        "max_viable_force": rows[-1]["force"] if rows else 0
    }


def render_downtime_binding_markdown(
    caster_pool: int,
    entity_type: str = "Spirit",
    pool_name: str = "Conjuring (Summoning)"
) -> str:
    """Renders formatted Quarto/Markdown callout table for downtime binding/registering."""
    result = calculate_downtime_binding_table(caster_pool, entity_type=entity_type, pool_name=pool_name)
    rows = result["rows"]

    if not rows:
        return f"*(No viable downtime {entity_type.lower()} binding possible: {pool_name} pool of {caster_pool} yields {result['pc_bought_hits']} bought hits, failing to beat Force 1)*"

    entity_label = "Sprite Level" if "sprite" in entity_type.lower() else "Spirit Force"
    action_label = "Registering" if "sprite" in entity_type.lower() else "Binding"
    tasks_label = "Guaranteed Tasks" if "sprite" in entity_type.lower() else "Guaranteed Services"

    lines = [
        f"::: {{.callout-note icon=false title=\"🔮 SRM Downtime {action_label} Table: {entity_type}s\"}}",
        f"Under Shadowrun Missions (SRM) downtime rules, characters and entities **must buy hits** (1 hit per 4 full dice). Full drain/fading recovery is assumed prior to mission start.\n",
        f"**Runner Tabletop Pool**: **{caster_pool}d6** ({result['pc_bought_hits']} Bought Hits) via *{pool_name}*.\n",
        f"| {entity_label} | Opposed Defense Pool | Entity Bought Hits | Runner Bought Hits | {tasks_label} |",
        f"| :---: | :---: | :---: | :---: | :---: |"
    ]

    for r in rows:
        task_str = f"**+{r['net_hits']} {action_label[:4].lower()}**" if r['net_hits'] > 1 else f"**+{r['net_hits']} task**"
        lines.append(
            f"| **Force {r['force']}** | {r['entity_pool']}d6 (`{r['force']} x 2`) | {r['entity_hits']} hits | {r['pc_hits']} hits | {task_str} |"
        )

    lines.append(f"\n*Cutoff Rule: Ceases at Force {result['max_viable_force'] + 1} where opposed entity hits ({((result['max_viable_force'] + 1) * 2) // 4}) match or exceed runner hits ({result['pc_bought_hits']}).*")
    lines.append(":::")

    return "\n".join(lines)
