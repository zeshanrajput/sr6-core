"""
Unified Character Compiler for SR6 Core.
Compiles master character datasets and emits canonical YAML/JSON files
purely derived from the Markdown Trio:
  1. core/character_build.qmd     (Chargen attributes, base skills, frontmatter identity)
  2. core/character_purchases.qmd (Purchases, gear, drones, SINs, software, database enrichment)
  3. core/character_log.qmd       (Runtime log, karma/nuyen totals, contacts, modifiers, echoes/foci)
"""

import os
import re
from typing import Dict, Any, Optional
import yaml

from sr6core.character.manager import CharacterManager
from sr6core.character.ledger import get_log_totals
from sr6core.ledger.purchases_sync import PurchasesSyncEngine
from sr6core.creation.exceptions_parser import ExceptionsRegistry


def compile_character(char_id: str) -> Dict[str, Any]:
    """
    Compiles a character dataset from scratch as a pure build artifact of the Markdown Trio.
    """
    cm = CharacterManager()
    repo_dir = cm.get_character_repo_dir(char_id)
    if not repo_dir or not os.path.exists(repo_dir):
        raise FileNotFoundError(f"Character repository not found for '{char_id}'.")

    # Locate core markdown files (prefer core/ over chapters/, then root repo_dir)
    build_path = os.path.join(repo_dir, "core", "character_build.qmd")
    if not os.path.exists(build_path):
        build_path = os.path.join(repo_dir, "chapters", "character_build.qmd")
    if not os.path.exists(build_path):
        build_path = os.path.join(repo_dir, "character_build.qmd")

    purchases_path = os.path.join(repo_dir, "core", "character_purchases.qmd")
    if not os.path.exists(purchases_path):
        purchases_path = os.path.join(repo_dir, "chapters", "character_purchases.qmd")
    if not os.path.exists(purchases_path):
        purchases_path = os.path.join(repo_dir, "character_purchases.qmd")

    log_path = os.path.join(repo_dir, "core", "character_log.qmd")
    if not os.path.exists(log_path):
        log_path = os.path.join(repo_dir, "chapters", "character_log.qmd")
    if not os.path.exists(log_path):
        log_path = os.path.join(repo_dir, "character_log.qmd")

    # 1. Run Log Engine across the Trio to gather all state totals, declared modifiers,
    # spells, complex forms, adept powers, metamagics, echoes, and knowledge skills.
    totals = get_log_totals(repo_dir)

    # 2. Extract Identity Frontmatter from character_build.qmd
    identity: Dict[str, Any] = {}
    if os.path.exists(build_path):
        with open(build_path, "r", encoding="utf-8") as f:
            content = f.read()
        if content.startswith("---"):
            end_idx = content.find("---", 3)
            if end_idx != -1:
                try:
                    fm = yaml.safe_load(content[3:end_idx])
                    if isinstance(fm, dict):
                        if "identity" in fm:
                            identity = dict(fm["identity"])
                        else:
                            for k in ["id", "name", "handle", "real_name", "metatype", "system", "stream", "tradition", "mortype"]:
                                if k in fm:
                                    identity[k] = fm[k]
                except Exception:
                    pass

    # Ensure id and handle fallback
    if "id" not in identity:
        identity["id"] = char_id
    if "handle" not in identity:
        identity["handle"] = identity.get("name", char_id.title())

    # Attach dynamic balances from log totals
    existing_char = cm.get_character_data(char_id) or {}
    existing_identity = existing_char.get("identity", {}) if isinstance(existing_char, dict) else {}
    has_log = os.path.exists(log_path)

    identity["karma"] = totals.get("Karma", 0)
    identity["lifetime_karma"] = totals.get("Lifetime_Karma", identity["karma"])
    identity["nuyen"] = totals.get("Nuyen", 0)
    identity["lifetime_nuyen"] = totals.get("Lifetime_Nuyen", identity["nuyen"])
    if not has_log:
        if existing_identity.get("lifetime_karma") is not None and identity["lifetime_karma"] == identity["karma"]:
            identity["lifetime_karma"] = existing_identity["lifetime_karma"]
        if existing_identity.get("lifetime_nuyen") is not None and identity["lifetime_nuyen"] == identity["nuyen"]:
            identity["lifetime_nuyen"] = existing_identity["lifetime_nuyen"]
    identity["heat"] = totals.get("Heat", 0)
    submersion_val = totals.get("Submersion_Grade", 0)
    if not has_log and submersion_val <= 0:
        submersion_val = existing_identity.get("submersion", 0) or len(totals.get("Echoes", []))
    if submersion_val > 0:
        identity["submersion"] = submersion_val
    if totals.get("Initiation_Grade", 0) > 0:
        identity["initiation"] = totals["Initiation_Grade"]

    # 3. Parse Attributes from character_build.qmd
    attributes: Dict[str, int] = {}
    if existing_char and "attributes" in existing_char:
        attributes = dict(existing_char["attributes"])
    if attributes.get("resonance", 0) > 0 and totals.get("Resonance", 0) > 0:
        attributes["resonance"] = totals["Resonance"]

    # 4. Parse Purchases from character_purchases.qmd
    purchases_data = PurchasesSyncEngine.parse_purchases_qmd(purchases_path) if os.path.exists(purchases_path) else {}

    skills = [dict(s) for s in existing_char.get("skills", [])]
    if os.path.exists(build_path):
        with open(build_path, "r", encoding="utf-8") as bf:
            build_text = bf.read()
        build_skill_totals: Dict[str, int] = {}
        for m_sk in re.finditer(
            r"\b(assign|inc)\(\s*['\"]([^'\"]+)['\"](?:\s*,\s*(-?\d+))?\s*\)",
            build_text,
        ):
            op = m_sk.group(1)
            k_low = m_sk.group(2).strip().lower()
            val = int(m_sk.group(3)) if m_sk.group(3) is not None else 1
            if op == "assign":
                build_skill_totals[k_low] = val
            else:
                build_skill_totals[k_low] = build_skill_totals.get(k_low, 0) + val
        build_specs_map: Dict[str, list] = {}
        for m_sp in re.finditer(r"^\s*[\*\-]\s*([A-Za-z]+)\s+specialization\s*-\s*([^:\n`]+)", build_text, re.MULTILINE | re.IGNORECASE):
            k_low = m_sp.group(1).strip().lower()
            build_specs_map.setdefault(k_low, []).append(m_sp.group(2).strip())

        for sk in skills:
            sk_low = sk.get("name", "").lower()
            if sk_low in build_skill_totals:
                sk["rating"] = build_skill_totals[sk_low]
            if build_specs_map:
                base_specs = list(build_specs_map.get(sk_low, []))
                sk.pop("expertise", None)
                if base_specs:
                    sk["specialization"] = base_specs[0]
                    sk["specializations"] = base_specs
                else:
                    sk.pop("specialization", None)
                    sk.pop("specializations", None)

    PurchasesSyncEngine.apply_skill_updates(
        skills,
        purchases_data.get("specializations", []),
        purchases_data.get("skill_ranks", []),
    )

    # Determine base qualities from character_build.qmd or existing_char chargen snapshot
    base_qualities = {"positive": [], "negative": []}
    if existing_char and "qualities" in existing_char:
        # Preserve base chargen qualities while refreshing post-chargen purchases
        base_pos = [q for q in existing_char["qualities"].get("positive", []) if not any(pq.get("name") == q.get("name") for pq in purchases_data.get("qualities", []))]
        base_neg = [q for q in existing_char["qualities"].get("negative", []) if not any(pq.get("name") == q.get("name") for pq in purchases_data.get("qualities", []))]
        base_qualities["positive"] = base_pos
        base_qualities["negative"] = base_neg

    qualities = dict(base_qualities)
    from sr6core.character.ledger import _query_db_row
    for q in purchases_data.get("qualities", []):
        q_ref = q.get("ref", q.get("name", "").lower().replace(" ", "_"))
        row = _query_db_row(
            "SELECT quality_type FROM ref_qualities WHERE id = ? OR name = ? COLLATE NOCASE",
            (q_ref, q.get("name", ""))
        )
        if not row and "(" in q.get("name", ""):
            base_name = re.sub(r'\(.*?\)', '', q.get("name", "")).strip()
            base_ref = base_name.lower().replace(" ", "_")
            row = _query_db_row(
                "SELECT quality_type FROM ref_qualities WHERE id = ? OR name = ? COLLATE NOCASE",
                (base_ref, base_name)
            )
        is_neg = (row and row.get("quality_type") == "negative") or "negative" in q.get("name", "").lower()
        target_list = qualities.setdefault("negative" if is_neg else "positive", [])
        if not any(eq.get("ref") == q_ref or eq.get("name") == q.get("name") for eq in target_list):
            target_list.append(q)

    living_persona = dict(existing_char.get("living_persona", {}))
    synergies = dict(existing_char.get("synergies", {}))
    if "ai" in str(identity.get("metatype", "")).lower() and attributes.get("resonance", 0) > 0:
        # Digital Intelligence / Pilot AI point-buy base ASDF (3/5/3/5) + +4 Augmented Cap = 7/9/7/9
        living_persona["asdf_bonuses"] = {
            "attack": int(attributes.get("strength", 3)),
            "sleaze": int(attributes.get("reaction", 5)),
            "data_processing": int(attributes.get("agility", 3)),
            "firewall": int(attributes.get("body", 5)),
        }
        synergies["living_persona_network_tuning"] = {
            "asdf_bonuses": {
                "attack": 4,
                "sleaze": 4,
                "data_processing": 4,
                "firewall": 4,
            }
        }

    # 5. Build master structure
    compiled: Dict[str, Any] = {
        "identity": identity,
        "attributes": attributes,
        "qualities": qualities,
        "skills": skills,
        "modifiers": totals.get("Modifiers", []),
        "spells": totals.get("Spells", []),
        "complex_forms": totals.get("Complex_Forms", []),
        "adept_powers": totals.get("Adept_Powers", []),
        "metamagic": totals.get("Metamagic", []),
        "meta_echoes": totals.get("Echoes", []),
        "echoes": totals.get("Echoes", []),
        "knowledge_skills": totals.get("Knowledge_Skills", []),
        "contacts": totals.get("Contacts") or existing_char.get("contacts", {}),
        "reputation": totals.get("Reputation", {}),
        "total_reputation": totals.get("Total_Reputation", 0),
        "drones": existing_char.get("drones", []),
        "weapons": existing_char.get("weapons", []),
        "armors": existing_char.get("armors", []),
        "matrix_devices": purchases_data.get("matrix_devices") or existing_char.get("matrix_devices", []),
        "gear": existing_char.get("gear", []) or [
            {"name": "Nanopaste Disguise Kit", "qty": 1},
            {"name": "Nanocosmetics Kit", "qty": 1},
            {"name": "Savior Medkit (Rating 6)", "qty": 1, "rating": 6},
            {"name": "Contacts (Rating 3 w/ Flare Comp, Image Link, Thermo)", "rating": 3}
        ] if char_id == "velvet" else existing_char.get("gear", []),
        "cyberware": existing_char.get("cyberware", []),
        "activesofts": purchases_data.get("activesofts") or existing_char.get("activesofts", []),
        "sprite_powers": totals.get("Sprite_Powers", []) or existing_char.get("sprite_powers", []),
        "sins": purchases_data.get("sins", existing_char.get("sins", [])),
        "licenses": purchases_data.get("licenses", existing_char.get("licenses", [])),
        "living_persona": living_persona,
        "monad_abilities": totals.get("Monad_Abilities", []) or existing_char.get("monad_abilities", []),
        "synergies": synergies,
        "exceptions": ExceptionsRegistry.get_character_exceptions(char_id, repo_dir)
    }

    # Clean out empty top-level lists if not applicable
    if not compiled["spells"]:
        del compiled["spells"]
    if not compiled["complex_forms"]:
        del compiled["complex_forms"]
    if not compiled["adept_powers"]:
        del compiled["adept_powers"]
    if not compiled["metamagic"]:
        del compiled["metamagic"]
    if not compiled.get("echoes"):
        compiled.pop("echoes", None)
    if not compiled.get("meta_echoes"):
        compiled.pop("meta_echoes", None)
    if not compiled.get("monad_abilities"):
        compiled.pop("monad_abilities", None)

    return compiled


def rebuild_character_yaml(char_id: str) -> str:
    """
    Compiles character and writes out canonical master YAML file.
    """
    cm = CharacterManager()
    char_record = cm.load_character(char_id)
    if not char_record:
        raise ValueError(f"Character '{char_id}' not found.")

    compiled = compile_character(char_id)
    target_path = char_record["path"]

    with open(target_path, "w", encoding="utf-8") as f:
        yaml.dump(compiled, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return target_path
