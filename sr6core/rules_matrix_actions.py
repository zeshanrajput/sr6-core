"""
SRM-Compliant Matrix Action & Specialization Engine for SR6 Core.
Categorizes Matrix actions strictly by Skill and Specialization per the SRM FAQ.
Computes character-specific dice pools, specialization bonuses (+2d6) or expertise (+3d6),
and opposed defense formulas for tabletop roleplay reference.
"""

from typing import Dict, Any, List, Optional, Union


SRM_MATRIX_TAXONOMY = [
    {
        "skill": "Electronics",
        "specialization": "Computer",
        "actions": [
            {
                "name": "Matrix Perception",
                "action_type": "Minor",
                "linked_attr": "intuition",
                "opposed": "Sleaze + Intuition (or Threshold 1)",
                "description": "Analyze Matrix icons, detect hidden nodes/personas, or inspect running programs."
            },
            {
                "name": "Edit File",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Firewall + Intuition (or Device Rating x 2)",
                "description": "Create, alter, copy, or erase a Matrix file or payload."
            },
            {
                "name": "Matrix Search",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Threshold 1–5 (Legwork / Search Complexity)",
                "description": "Thoroughly search local grids or public data archives for specific intel."
            },
            {
                "name": "Trace Icon",
                "action_type": "Major",
                "linked_attr": "intuition",
                "opposed": "Sleaze + Willpower",
                "description": "Pinpoint the physical location of a persona, deck, or device in meatspace."
            },
            {
                "name": "Hash",
                "action_type": "Minor",
                "linked_attr": "logic",
                "opposed": "Device Rating x 2",
                "description": "Generate or verify cryptographic signatures and data checksums."
            }
        ]
    },
    {
        "skill": "Electronics",
        "specialization": "Software",
        "actions": [
            {
                "name": "Format Device",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Firewall + Willpower",
                "description": "Wipe the OS or active memory of a target device, forcing a factory reset."
            },
            {
                "name": "Reboot Device",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Firewall + Willpower",
                "description": "Remotely command a device to shut down and reboot (clears link-locks)."
            },
            {
                "name": "Disarm Data Bomb",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Data Bomb Rating x 2",
                "description": "Defuse a defensive data trap on a protected file without detonating it."
            }
        ]
    },
    {
        "skill": "Electronics",
        "specialization": "Hardware",
        "actions": [
            {
                "name": "Jack Out",
                "action_type": "Major",
                "linked_attr": "willpower",
                "opposed": "Attack + Logic (if link-locked)",
                "description": "Emergency disconnect from VR or direct neural connection. Suffers dumpshock if in VR."
            },
            {
                "name": "Jump into Rigged Device",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Threshold (Device Security / Control Rig)",
                "description": "Assume direct jumped-in vehicle or drone control via Control Rig or Living Persona."
            }
        ]
    },
    {
        "skill": "Cracking",
        "specialization": "Hacking",
        "actions": [
            {
                "name": "Backdoor",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Firewall + Willpower",
                "description": "Establish persistent, undetected User access to a host or system."
            },
            {
                "name": "Hack on the Fly",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Firewall + Intuition",
                "description": "Gain immediate temporary User or Admin access during tactical infiltration."
            },
            {
                "name": "Probe",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Firewall + Intuition",
                "description": "Extended stealth reconnaissance against a host to discover exploitable vulnerabilities."
            },
            {
                "name": "Set Data Bomb",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Device Rating x 2",
                "description": "Booby-trap a file to detonate and inflict Matrix damage if accessed without password."
            },
            {
                "name": "Spoof Command",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Firewall + Intuition",
                "description": "Forge a control signal to order a device, drone, or cyberware to execute an action."
            },
            {
                "name": "Enter/Exit Host",
                "action_type": "Minor",
                "linked_attr": "logic",
                "opposed": "Threshold (Host Rating)",
                "description": "Cross the data perimeter into or out of a virtual host architecture."
            }
        ]
    },
    {
        "skill": "Cracking",
        "specialization": "Cybercombat",
        "actions": [
            {
                "name": "Brute Force",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Firewall + Willpower",
                "description": "Violently bash through matrix defenses to seize immediate Admin or User privileges."
            },
            {
                "name": "Crash Program",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Firewall + Intuition",
                "description": "Corrupt and crash a specific active cyberprogram or IC routine on target system."
            },
            {
                "name": "Data Spike",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Firewall + Willpower",
                "description": "Hurl a high-voltage code spike dealing Matrix DV (Base Attack Rating) to condition monitor."
            },
            {
                "name": "Erase Matrix Signature",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Threshold (Signature Rating)",
                "description": "Scrub forensic residue and datatrails left behind by decking or technomancy."
            },
            {
                "name": "Jam Signals",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Threshold (Noise Rating)",
                "description": "Broadcast static interference to cut off wireless communication in tactical radius."
            },
            {
                "name": "Tarpit",
                "action_type": "Major",
                "linked_attr": "logic",
                "opposed": "Firewall + Willpower",
                "description": "Deploy sticky algorithmic traps to slow and pin down enemy persona or IC."
            }
        ]
    }
]


def calculate_matrix_action_pool(char_data: Dict[str, Any], skill_name: str, specialization_name: str, linked_attr: str) -> Dict[str, Any]:
    """
    Calculates effective tabletop dice pool and status for a specific Matrix action,
    deriving directly from ModifierEngine.get_matrix_action_pools for complete rules consistency.
    """
    from sr6core.modifiers import ModifierEngine

    pools = ModifierEngine.get_matrix_action_pools(char_data)

    skills = char_data.get("skills", [])
    skill_rec = next((s for s in skills if isinstance(s, dict) and s.get("name", "").lower() == skill_name.lower()), None)
    specs = []
    if skill_rec:
        specs = list(skill_rec.get("specializations", []))
        if isinstance(skill_rec.get("specialization"), str):
            specs.append(skill_rec.get("specialization"))

    has_spec = False
    is_expert = False
    for sp in specs:
        sp_name = sp.get("name", "") if isinstance(sp, dict) else str(sp)
        is_exp = sp.get("expertise", False) if isinstance(sp, dict) else ("expertise" in sp_name.lower())
        if specialization_name.lower() in sp_name.lower():
            has_spec = True
            if is_exp:
                is_expert = True
            break

    tier = "Expert (+3d)" if is_expert else ("Specialized (+2d)" if has_spec else "Base Skill")
    bonus_dice = 3 if is_expert else (2 if has_spec else 0)

    if skill_name.lower() == "cracking":
        if specialization_name.lower() == "hacking":
            opt = pools.get("cracking_hacking")
            total_pool = opt.total_pool if opt else 0
            wild_dice = opt.wild_dice if opt else 0
            breakdown = opt.get_modifiers_breakdown_string() if opt else "Cracking + Hacking"
        else:
            opt = pools.get("cracking_other")
            base_p = opt.total_pool if opt else 0
            wild_dice = opt.wild_dice if opt else 0
            extra = bonus_dice if has_spec else 0
            total_pool = base_p + extra
            breakdown = opt.get_modifiers_breakdown_string() if opt else "Cracking + RES/LOG"
    else:  # Electronics
        if specialization_name.lower() == "software":
            opt = pools.get("electronics_software")
            total_pool = opt.total_pool if opt else 0
            wild_dice = opt.wild_dice if opt else 0
            breakdown = opt.get_modifiers_breakdown_string() if opt else "Electronics + Software"
        else:
            opt = pools.get("electronics_other")
            base_p = opt.total_pool if opt else 0
            wild_dice = opt.wild_dice if opt else 0
            extra = bonus_dice if has_spec else 0
            total_pool = base_p + extra
            breakdown = opt.get_modifiers_breakdown_string() if opt else "Electronics + RES/INT/LOG"

    return {
        "pool": total_pool,
        "wild_dice": wild_dice,
        "bought_hits": total_pool // 4,
        "breakdown": breakdown,
        "tier": tier,
        "bonus_dice": bonus_dice
    }


def render_matrix_actions_markdown(char_input: Union[str, Dict[str, Any]]) -> str:
    """Renders SRM-compliant Markdown tables for character rules chapters."""
    if isinstance(char_input, str):
        from sr6core.character_manager import CharacterManager
        cm = CharacterManager()
        char_data = cm.get_character_data(char_input) or {}
    else:
        char_data = char_input

    sections = []

    for group in SRM_MATRIX_TAXONOMY:
        skill = group["skill"]
        spec = group["specialization"]
        actions = group["actions"]

        header = f"### {skill}: Specialization in *{spec}*\n"
        table_rows = [
            "| Action | Type | Tabletop Pool | Proficiency | Opposed Resistance Test | Mechanical Description |",
            "| :--- | :---: | :---: | :---: | :--- | :--- |"
        ]

        for act in actions:
            pool_info = calculate_matrix_action_pool(char_data, skill, spec, act["linked_attr"])
            prof_badge = f"**{pool_info['tier']}**" if pool_info["bonus_dice"] > 0 else pool_info["tier"]
            wild_badge = f" ({pool_info['wild_dice']} wild)" if pool_info.get("wild_dice") else ""
            hits_badge = f" $\\rightarrow$ **{pool_info['bought_hits']} hit{'s' if pool_info['bought_hits'] != 1 else ''}**"
            pool_badge = f"**{pool_info['pool']}d6**{wild_badge}{hits_badge}"

            row = (
                f"| **{act['name']}** | {act['action_type']} | {pool_badge} "
                f"| {prof_badge} | `{act['opposed']}` | {act['description']} |"
            )
            table_rows.append(row)

        sections.append(header + "\n".join(table_rows))

    return "\n\n".join(sections)

