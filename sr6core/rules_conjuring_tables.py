"""
Downtime Spirit Binding & Sprite Registration Probability Engine for SR6.
Evaluates downtime binding/registering under standard SRM Downtime rules where
both the runner and the entity MUST BUY HITS (1 hit per 4 full dice).
Yields deterministic guaranteed tasks/services and terminates when net hits <= 0.
"""

from typing import Dict, Any, List, Optional, Union


def resolve_character_binding_context(char_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Resolves character stats, skills, foci, and metamagics for downtime binding/registering."""
    if isinstance(char_input, str):
        from sr6core.character_manager import CharacterManager
        cm = CharacterManager()
        char_data = cm.get_character_data(char_input) or {}
    else:
        char_data = char_input

    attrs = char_data.get("attributes", {})
    magic = attrs.get("magic", 0)
    resonance = attrs.get("resonance", 0)
    char_name = char_data.get("identity", {}).get("name", "Runner")

    skills_map = {s.get("name", "").lower(): s for s in char_data.get("skills", [])}

    from sr6core.modifiers import ModifierEngine

    if magic > 0:
        conj_skill = skills_map.get("conjuring", {})
        conj_rating = conj_skill.get("rating", 0)
        spec = str(conj_skill.get("specialization", "")).lower()
        spec_bonus = 2 if spec else 0
        focus_mods = ModifierEngine.get_focus_modifiers(char_data, "magic")
        power_focus = sum(m.value for m in focus_mods)

        base_pool = conj_rating + spec_bonus + magic + power_focus
        initiation_grade = len(char_data.get("metamagic", [])) or len(char_data.get("meta_echoes", []))

        # Check for Channeling metamagic
        has_channeling = any("channel" in m.get("name", "").lower() for m in char_data.get("metamagic", []))
        channeling_pool = (base_pool + initiation_grade) if has_channeling else None

        return {
            "is_awakened": True,
            "entity_type": "Spirit",
            "action_label": "Binding",
            "pool_name": "Conjuring",
            "base_pool": base_pool,
            "channeling_pool": channeling_pool,
            "char_name": char_name,
            "power_focus": power_focus,
            "initiation_grade": initiation_grade,
        }
    elif resonance > 0:
        task_skill = skills_map.get("tasking", {})
        task_rating = task_skill.get("rating", 0)
        spec = str(task_skill.get("specialization", "")).lower()
        spec_bonus = 2 if ("register" in spec or "compil" in spec) else 0
        focus_mods = ModifierEngine.get_focus_modifiers(char_data, "resonance")
        res_focus = sum(m.value for m in focus_mods)

        compiling_pool = task_rating + resonance + res_focus
        registering_pool = task_rating + spec_bonus + resonance + res_focus

        return {
            "is_awakened": False,
            "entity_type": "Sprite",
            "action_label": "Registering",
            "pool_name": "Tasking (Registering)",
            "base_pool": registering_pool,
            "compiling_pool": compiling_pool,
            "char_name": char_name,
            "res_focus": res_focus,
        }
    else:
        return {
            "is_awakened": False,
            "entity_type": "None",
            "base_pool": 0,
            "char_name": char_name,
        }


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
    caster_input: Union[int, str, Dict[str, Any]],
    entity_type: str = "Spirit",
    pool_name: str = "Conjuring (Summoning)"
) -> str:
    """Renders formatted Quarto/Markdown callout table for downtime binding/registering."""
    if isinstance(caster_input, (str, dict)):
        ctx = resolve_character_binding_context(caster_input)
        if ctx.get("entity_type") == "None":
            return f"*(No downtime binding/registering applicable for {ctx.get('char_name')})*"

        entity_type = ctx["entity_type"]
        pool_name = ctx["pool_name"]
        base_pool = ctx["base_pool"]
        channeling_pool = ctx.get("channeling_pool")
        compiling_pool = ctx.get("compiling_pool")
    else:
        base_pool = caster_input
        channeling_pool = None
        compiling_pool = None

    entity_label = "Sprite Level" if "sprite" in entity_type.lower() else "Spirit Force"
    action_label = "Registering" if "sprite" in entity_type.lower() else "Binding"
    tasks_label = "Guaranteed Tasks" if "sprite" in entity_type.lower() else "Guaranteed Services"

    # Handle dual Channeling table for Awakened
    if channeling_pool is not None:
        base_hits = base_pool // 4
        chan_hits = channeling_pool // 4

        lines = [
            f"::: {{.callout-note icon=false title=\"🔮 SRM Downtime {action_label} Table: {entity_type}s\"}}",
            f"Under official **Shadowrun Missions (SRM / SRMG)** rules, downtime tests utilize bought hits (4 dice = 1 hit).",
            f"* **Standard Conjuring Pool**: **{base_pool}d6 $\\rightarrow$ {base_hits} Bought Hits**",
            f"* **Channeling Inhabitation Pool**: **{channeling_pool}d6 $\\rightarrow$ {chan_hits} Bought Hits** (Initiate Grade +{ctx.get('initiation_grade', 0)})\n",
            f"| {entity_label} | Opposed Defense Pool | Entity Bought Hits | Conjuring Net Hits ({base_pool}d6 $\\rightarrow$ {base_hits} Hits) | Channeling Net Hits ({channeling_pool}d6 $\\rightarrow$ {chan_hits} Hits) | Downtime Utility & Services |",
            f"| :---: | :---: | :---: | :---: | :---: | :--- |"
        ]

        for force in range(1, 10):
            def_pool = force * 2
            def_hits = def_pool // 4
            conj_net = base_hits - def_hits
            chan_net = chan_hits - def_hits

            if conj_net <= 0 and chan_net <= 0:
                break

            conj_svc = f"{conj_net} Service" if conj_net == 1 else f"{conj_net} Services"
            conj_str = f"**+{conj_net} Net Hit{'s' if conj_net != 1 else ''}** ({conj_svc})" if conj_net > 0 else "0 Net Hits"
            chan_str = f"**+{chan_net} Net Hit{'s' if chan_net != 1 else ''}**" if chan_net > 0 else "0 Net Hits"

            role_desc = "Minor utility & scouting" if force == 1 else ("Standard elemental" if force == 2 else ("Social / Tactical anchor" if force in (3, 4) else "Heavy combat & major service"))

            lines.append(
                f"| **Force {force}** | {def_pool}d6 | {def_hits} hit{'s' if def_hits != 1 else ''} | {conj_str} | {chan_str} | {role_desc} |"
            )

        lines.append(f"\n> **Deterministic Threshold**: Summoning and binding spirits up to Force {base_hits * 2 - 1} succeeds with 100% certainty and 0 net drain in downtime.")
        lines.append(":::")
        return "\n".join(lines)

    # Handle dual Compiling / Registering table for Technomancer
    if compiling_pool is not None:
        comp_hits = compiling_pool // 4
        reg_hits = base_pool // 4

        lines = [
            f"::: {{.callout-note icon=false title=\"🔮 SRM Downtime {action_label} Table: {entity_type}s\"}}",
            f"Under official **Shadowrun Missions (SRM / SRMG)** rules, downtime compiling and registering utilize bought hits (4 dice = 1 hit).",
            f"* **Compiling Pool**: **{compiling_pool}d6 $\\rightarrow$ {comp_hits} Bought Hits** (Tasking + Resonance + Focus)",
            f"* **Registering Pool**: **{base_pool}d6 $\\rightarrow$ {reg_hits} Bought Hits** (Tasking + Specialization + Resonance + Focus)\n",
            f"| {entity_label} | Opposed Defense Pool | Entity Bought Hits | Compiling Net Hits | Registering Net Hits | Combined Guaranteed Services |",
            f"| :---: | :---: | :---: | :---: | :---: | :---: |"
        ]

        for level in range(1, 10):
            def_pool = level * 2
            def_hits = def_pool // 4
            comp_net = comp_hits - def_hits
            reg_net = reg_hits - def_hits

            if comp_net <= 0 and reg_net <= 0:
                break

            comp_services = (comp_net + 1) if comp_net > 0 else 0  # Technoshaman +1 service bonus on compiled
            total_services = comp_services + max(0, reg_net)

            comp_str = f"**+{comp_net} hit{'s' if comp_net != 1 else ''}** (+{comp_services} svc)" if comp_net > 0 else "0 hits"
            reg_str = f"**+{reg_net} hit{'s' if reg_net != 1 else ''}**" if reg_net > 0 else "0 hits"
            total_str = f"**{total_services} service{'s' if total_services != 1 else ''}**" if total_services > 0 else "None"

            lines.append(
                f"| **Level {level}** | {def_pool}d6 | {def_hits} hit{'s' if def_hits != 1 else ''} | {comp_str} | {reg_str} | {total_str} |"
            )

        lines.append(f"\n> **Deterministic Threshold**: Compiling and registering sprites up to Level {comp_hits * 2 - 1} succeeds with 100% certainty in downtime.")
        lines.append(":::")
        return "\n".join(lines)

    # Standard single pool table
    result = calculate_downtime_binding_table(base_pool, entity_type=entity_type, pool_name=pool_name)
    rows = result["rows"]

    if not rows:
        return f"*(No viable downtime {entity_type.lower()} binding possible: {pool_name} pool of {base_pool} yields {result['pc_bought_hits']} bought hits, failing to beat Force 1)*"

    lines = [
        f"::: {{.callout-note icon=false title=\"🔮 SRM Downtime {action_label} Table: {entity_type}s\"}}",
        f"Under Shadowrun Missions (SRM) downtime rules, characters and entities **must buy hits** (1 hit per 4 full dice). Full drain/fading recovery is assumed prior to mission start.\n",
        f"**Runner Tabletop Pool**: **{base_pool}d6** ({result['pc_bought_hits']} Bought Hits) via *{pool_name}*.\n",
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

