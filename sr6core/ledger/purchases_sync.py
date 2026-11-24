"""
Purchases Sync Engine for SR6 Core.
Parses character_purchases.qmd and synchronizes drone modifications,
inventory, foci, SINs, licenses, and gear into character_master.yaml automatically.
"""

import os
import re
from typing import Dict, List, Any, Optional
import yaml
from sr6core.character.manager import CharacterManager


class PurchasesSyncEngine:
    @staticmethod
    def clean_item_text(line: str) -> str:
        """Strips markdown asterisks, whitespace, backticks, and Quarto `{python} ...` code from line."""
        # Strip inline backtick code containing python or inc expressions
        cleaned = re.sub(r'`\s*\{?python[^\`]*\}?\s*`', '', line)
        cleaned = re.sub(r'\{python[^\}]*\}', '', cleaned)
        cleaned = re.sub(r'`\s*inc(_many)?[^\`]*`', '', cleaned)
        cleaned = re.sub(r'`[^`]*`', '', cleaned)
        cleaned = re.sub(r'inc(_many)?\([^\)]*\)', '', cleaned)
        # Strip any remaining backticks
        cleaned = re.sub(r'`+', '', cleaned)
        # Strip bold/italic markdown
        cleaned = re.sub(r'\*+', '', cleaned)
        # Strip leading bullets and whitespace
        cleaned = re.sub(r'^[\s\-•]+', '', cleaned)
        # Strip trailing colons
        cleaned = re.sub(r':\s*$', '', cleaned)
        cleaned = cleaned.strip()
        return cleaned

    @classmethod
    def parse_purchases_qmd(cls, qmd_path: str) -> Dict[str, Any]:
        """
        Parses a character_purchases.qmd file into structured collections:
        - drone_modifications: Dict[drone_name, List[modification_strings]]
        - autosofts: List[str]
        - programs: List[str]
        - commlink_apps: List[str]
        - gear: List[str]
        - sins: List[Dict[str, Any]]
        - licenses: List[Dict[str, Any]]
        """
        if not os.path.exists(qmd_path):
            return {}

        with open(qmd_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_section = None
        current_drone = None
        current_sub_category = None
        current_sin = None

        drone_mods: Dict[str, List[str]] = {}
        drone_quantities: Dict[str, int] = {}
        autosofts: List[str] = []
        programs: List[str] = []
        commlink_apps: List[str] = []
        activesofts: List[Dict[str, Any]] = []
        gear_items: List[str] = []
        matrix_devices: List[Dict[str, Any]] = []
        current_device = None
        sins: List[Dict[str, Any]] = []
        licenses: List[Dict[str, Any]] = []
        qualities: List[Dict[str, Any]] = []
        combat_items: List[str] = []

        # Keywords that represent sub-headers or nested sub-items, not top-level modifications
        ignore_mod_prefixes = [
            'stores ', 'wearable', 'accessories', 'crimson wasp', 'red fox',
            'han ', 'mct gnat', 'mct hornet', 'm-toc ii', 'foundation host', 'stores'
        ]

        for line in lines:
            raw_line = line.rstrip()
            stripped = raw_line.strip()
            if not stripped:
                continue

            # Section headers
            if stripped.startswith('### '):
                header = stripped.replace('### ', '').strip().lower()
                if 'vehicle' in header or 'drone' in header:
                    current_section = 'vehicles'
                elif 'matrix' in header or 'software' in header:
                    current_section = 'matrix'
                elif 'combat' in header:
                    current_section = 'combat'
                elif 'sin' in header or 'license' in header:
                    current_section = 'sins'
                else:
                    current_section = header
                current_drone = None
                current_sub_category = None
                current_sin = None
                continue

            # In Vehicles & Drones section
            if current_section == 'vehicles':
                # Check indentation / bullet level
                if raw_line.startswith('* ') or (raw_line.startswith('- ') and not raw_line.startswith('  -')):
                    # Top-level drone entry (e.g. * Shiawase Man-At-Arms ..., * MCT Gnat x5)
                    drone_title = cls.clean_item_text(stripped)
                    # Normalize drone name and extract optional quantity (e.g. x5)
                    raw_drone = drone_title.split('(')[0].strip()
                    m_dqty = re.search(r'\s+x\s*(\d+)\b', raw_drone, re.IGNORECASE)
                    d_qty = int(m_dqty.group(1)) if m_dqty else 1
                    current_drone = re.sub(r'\s+x\s*\d+\b', '', raw_drone, flags=re.IGNORECASE).strip()
                    if d_qty > 1:
                        drone_quantities[current_drone] = d_qty
                    if current_drone not in drone_mods:
                        drone_mods[current_drone] = []
                elif current_drone and (raw_line.startswith('  *') or raw_line.startswith('    *') or raw_line.startswith('  -')):
                    mod_text = cls.clean_item_text(stripped)
                    if not mod_text:
                        continue
                    low = mod_text.lower()
                    if any(low == ign or low.startswith(ign) for ign in ignore_mod_prefixes):
                        continue

                    # Normalize format
                    norm_mod = mod_text
                    norm_mod = re.sub(r'Weapon Mount\s*-\s*(Small|Standard|Large|Huge)', r'Weapon Mount (\1)', norm_mod, flags=re.IGNORECASE)
                    norm_mod = re.sub(r'Pop-Out Concealment\s*-\s*(Small|Standard|Large|Huge)', r'Pop-Out Concealment (\1)', norm_mod, flags=re.IGNORECASE)
                    norm_mod = re.sub(r'Retractible Skates.*', 'Retractable Skates', norm_mod, flags=re.IGNORECASE)
                    norm_mod = re.sub(r'Retractable Skates.*', 'Retractable Skates', norm_mod, flags=re.IGNORECASE)
                    norm_mod = re.sub(r':$', '', norm_mod).strip()

                    if norm_mod and norm_mod not in drone_mods[current_drone]:
                        drone_mods[current_drone].append(norm_mod)

            # In Matrix & Software section
            elif current_section == 'matrix':
                if (raw_line.startswith('* ') or raw_line.startswith('- ')) and not raw_line.startswith('  '):
                    low_stripped = stripped.lower()
                    if 'autosoft' in low_stripped:
                        current_sub_category = 'autosofts'
                        current_device = None
                    elif 'program' in low_stripped:
                        current_sub_category = 'programs'
                        current_device = None
                    elif 'commlink app' in low_stripped or 'utilities' in low_stripped:
                        current_sub_category = 'commlink_apps'
                        current_device = None
                    elif 'sensor' in low_stripped or 'audio' in low_stripped:
                        current_sub_category = 'sensors'
                        current_device = None
                    elif any(
                        kw in low_stripped
                        for kw in ('software library', 'knowsoft', 'data structures', 'resonance constructs')
                    ) or low_stripped in ('* other', '- other'):
                        current_sub_category = 'ignored_header'
                        current_device = None
                    else:
                        dev_text = cls.clean_item_text(stripped)
                        m_rat = re.search(r'(?:Rating|R|Device Rating)\s*(\d+)', dev_text, re.IGNORECASE)
                        m_qty = re.search(r'x\s*(\d+)', dev_text, re.IGNORECASE)
                        dev_name = re.sub(r'\(.*?\)', '', dev_text).replace(':', '').strip()
                        dev_name = re.sub(r'(?:^\d+\s*x\s*|\s*x\s*\d+$)', '', dev_name, flags=re.IGNORECASE).strip()
                        dev_rat = int(m_rat.group(1)) if m_rat else 1
                        dev_qty = int(m_qty.group(1)) if m_qty else 1
                        current_device = {
                            "name": dev_name,
                            "rating": dev_rat,
                            "qty": dev_qty,
                            "accessories": []
                        }
                        matrix_devices.append(current_device)
                        current_sub_category = 'device'
                elif raw_line.startswith('  *') or raw_line.startswith('    *') or raw_line.startswith('  -'):
                    if current_sub_category == 'device' and current_device:
                        acc_text = cls.clean_item_text(stripped)
                        if acc_text and acc_text not in current_device["accessories"]:
                            current_device["accessories"].append(acc_text)
                    elif current_sub_category == 'autosofts':
                        item_name = cls.clean_item_text(stripped)
                        if item_name and item_name not in autosofts:
                            autosofts.append(item_name)
                    elif current_sub_category == 'programs':
                        item_name = cls.clean_item_text(stripped)
                        if item_name and item_name not in programs:
                            programs.append(item_name)
                    elif current_sub_category == 'commlink_apps':
                        item_name = cls.clean_item_text(stripped)
                        if item_name and item_name not in commlink_apps:
                            commlink_apps.append(item_name)
                    elif current_sub_category == 'sensors':
                        item_name = cls.clean_item_text(stripped)
                        if item_name and item_name not in gear_items:
                            gear_items.append(item_name)

            # In SINs & Licenses section
            elif current_section == 'combat':
                item_cleaned = cls.clean_item_text(stripped)
                if item_cleaned:
                    combat_items.append(item_cleaned)

            elif current_section == 'sins':
                item_cleaned = cls.clean_item_text(stripped)
                if not item_cleaned:
                    continue

                # Parse rating if present e.g. "Yuriko Star (R6)" -> rating: 6
                rating_match = re.search(r'\((?:R|Rating\s*)(\d+)\)', item_cleaned, re.IGNORECASE)
                rating_val = int(rating_match.group(1)) if rating_match else 1
                name_clean = re.sub(r'\s*\((?:R|Rating\s*)\d+\)', '', item_cleaned, flags=re.IGNORECASE).strip()

                if raw_line.startswith('* ') or (raw_line.startswith('- ') and not raw_line.startswith('  -')):
                    # Top-level SIN
                    current_sin = name_clean
                    sins.append({
                        "name": name_clean,
                        "rating": rating_val
                    })
                elif raw_line.startswith('  *') or raw_line.startswith('    *') or raw_line.startswith('  -'):
                    # Sub-level License attached to current_sin
                    licenses.append({
                        "name": name_clean,
                        "rating": rating_val,
                        "sin": current_sin or "Primary SIN"
                    })

            # In Activesoft entries
            if 'activesoft' in stripped.lower() and ('* **' in raw_line or '- **' in raw_line or current_section == 'activesofts'):
                m_title = re.search(r'\*\*(.*?)\*\*', stripped)
                title = m_title.group(1).strip() if m_title else cls.clean_item_text(stripped)
                r_match = re.search(r'(?:Rating|R)\s*(\d+)', title, re.IGNORECASE)
                rating = int(r_match.group(1)) if r_match else 6
                name_clean = re.sub(r'\(.*?\)', '', title).replace(':', '').strip()
                if not name_clean.lower().endswith("activesoft"):
                    name_clean = f"{name_clean} Activesoft"
                attr = "agility" if any(k in name_clean.lower() for k in ["combat", "firearm", "athletic", "stealth"]) else "logic"
                if not any(a.get("name", "").lower() == name_clean.lower() for a in activesofts):
                    activesofts.append({
                        "name": name_clean,
                        "rating": rating,
                        "category": "activesoft",
                        "attribute": attr,
                        "notes": f"Rating {rating} activesoft synced from purchases.qmd. Runs on Skillwires R6 with Wireless-ON (+1) for {rating + 1} effective skill dice."
                    })

            # In Skill Specialization & Expertise entries
            m_spec = re.search(r'\*\*\s*([A-Za-z]+)\s+(Specialization|Expertise)\s*\((.*?)\)\s*:\s*\*\*', stripped, re.IGNORECASE)
            if m_spec:
                if 'specializations' not in locals():
                    specializations = []
                specializations.append({
                    "skill": m_spec.group(1).strip(),
                    "specialization": m_spec.group(3).strip(),
                    "expertise": m_spec.group(2).strip().lower() == "expertise"
                })

            # In Skill Rank entries (e.g. **Con (Rank 2):** or **Con Rank 2:**)
            m_rank = re.search(r'\*\*\s*([A-Za-z]+)\s*(?:\(Rank\s*(\d+)\)|Rank\s*(\d+))\s*:\s*\*\*', stripped, re.IGNORECASE)
            if m_rank:
                if 'skill_ranks' not in locals():
                    skill_ranks = []
                r_val = int(m_rank.group(2) or m_rank.group(3))
                skill_ranks.append({
                    "skill": m_rank.group(1).strip(),
                    "rating": r_val
                })

            # In Qualities & Mentor Spirits entries
            m_mentor = re.search(r'\*\*\s*Mentor Spirit\s*(?:\((.*?)\)|:\s*([^\*:]+))?\s*:\s*\*\*', stripped, re.IGNORECASE)
            if m_mentor:
                choice = (m_mentor.group(1) or m_mentor.group(2) or "").strip()
                q_name = f"Mentor Spirit ({choice})" if choice else "Mentor Spirit"
                if not any(q.get("name") == q_name for q in qualities):
                    qualities.append({
                        "name": q_name,
                        "ref": "mentor_spirit",
                        "choice": choice,
                        "karma": 20
                    })
            elif current_section in ['qualities', 'qualities & mentor spirits']:
                if raw_line.startswith('* ') or raw_line.startswith('- '):
                    m_title = re.search(r'\*\*\s*([^*]+?)\s*\*\*', stripped)
                    if m_title:
                        clean_q = m_title.group(1).rstrip(':').strip()
                    else:
                        clean_q = cls.clean_item_text(stripped)
                    if clean_q and not any(q.get("name").lower() == clean_q.lower() for q in qualities):
                        m_choice = re.search(r'\((.*?)\)', clean_q)
                        choice = m_choice.group(1).strip() if m_choice else ""
                        ref = "mentor_spirit" if "mentor spirit" in clean_q.lower() else clean_q.lower().replace(" ", "_")
                        qualities.append({
                            "name": clean_q,
                            "ref": ref,
                            "choice": choice,
                            "karma": 20 if "mentor spirit" in clean_q.lower() else 0
                        })

        if matrix_devices and commlink_apps:
            primary_dev = matrix_devices[0]
            for app in commlink_apps:
                if app not in primary_dev["accessories"]:
                    primary_dev["accessories"].append(app)

        return {
            "drone_modifications": drone_mods,
            "drone_quantities": drone_quantities,
            "autosofts": autosofts,
            "programs": programs,
            "commlink_apps": commlink_apps,
            "activesofts": activesofts,
            "gear": gear_items,
            "matrix_devices": matrix_devices,
            "sins": sins,
            "licenses": licenses,
            "qualities": qualities,
            "combat_items": combat_items,
            "specializations": locals().get("specializations", []),
            "skill_ranks": locals().get("skill_ranks", [])
        }


    @staticmethod
    def apply_skill_updates(
        skills: List[Dict[str, Any]],
        parsed_specs: List[Dict[str, Any]],
        parsed_ranks: List[Dict[str, Any]],
    ) -> List[str]:
        """Applies parsed skill specializations, expertises, and rank upgrades to a skills list."""
        changes: List[str] = []
        for spec_entry in parsed_specs:
            sk_target = spec_entry.get("skill", "").lower()
            sp_val = spec_entry.get("specialization", "").strip()
            is_exp = bool(spec_entry.get("expertise", False))
            if not sp_val:
                continue
            for sk in skills:
                if sk.get("name", "").lower() != sk_target:
                    continue
                curr_specs = list(sk.get("specializations", []))
                if sk.get("specialization") and sk["specialization"] not in curr_specs and f"{sk['specialization']} (Expertise)" not in curr_specs:
                    curr_specs.append(sk["specialization"])

                if is_exp:
                    exp_label = f"{sp_val} (Expertise)"
                    new_specs = [
                        s for s in curr_specs
                        if str(s).strip().lower() not in {sp_val.lower(), exp_label.lower()}
                    ]
                    new_specs.insert(0, exp_label)
                    if new_specs != curr_specs or sk.get("expertise") != sp_val:
                        sk["specializations"] = new_specs
                        sk["expertise"] = sp_val
                        if str(sk.get("specialization", "")).strip().lower() == sp_val.lower():
                            sk.pop("specialization", None)
                        changes.append(f"Upgraded Expertise '{sp_val}' on skill '{sk['name']}'")
                else:
                    already = any(
                        re.sub(r'\s*\(expertise\)', '', str(s), flags=re.IGNORECASE).strip().lower() == sp_val.lower()
                        for s in curr_specs
                    )
                    if not already:
                        curr_specs.append(sp_val)
                        sk["specializations"] = curr_specs
                        changes.append(f"Added Specialization '{sp_val}' to skill '{sk['name']}'")
                    if not sk.get("specialization") and str(sk.get("expertise", "")).strip().lower() != sp_val.lower():
                        sk["specialization"] = sp_val

        for rank_entry in parsed_ranks:
            sk_target = rank_entry.get("skill", "").lower()
            r_val = rank_entry.get("rating", 1)
            for sk in skills:
                if sk.get("name", "").lower() == sk_target:
                    old_r = sk.get("rating", 1)
                    if old_r != r_val:
                        sk["rating"] = r_val
                        changes.append(f"Updated skill '{sk['name']}' rating from {old_r} to {r_val}")
        return changes

    @classmethod
    def sync_character_purchases(cls, char_id: str) -> Dict[str, Any]:
        """
        Synchronizes purchases from character_purchases.qmd into character_master.yaml.
        Returns a dictionary of applied changes.
        """
        cm = CharacterManager()
        char_record = cm.load_character(char_id)
        if not char_record:
            return {"status": "error", "message": f"Character '{char_id}' not found"}

        repo_dir = cm.get_character_repo_dir(char_id)
        if not repo_dir or not os.path.exists(repo_dir):
            return {"status": "error", "message": f"Repo dir for '{char_id}' not found"}

        # Find character_purchases.qmd (prioritize core/ over chapters/)
        core_path = os.path.join(repo_dir, "core", "character_purchases.qmd")
        chap_path = os.path.join(repo_dir, "chapters", "character_purchases.qmd")
        qmd_path = core_path if os.path.exists(core_path) else chap_path
        if not os.path.exists(qmd_path):
            # Check alternative locations
            for root, _, files in os.walk(repo_dir):
                for f in files:
                    if "purchase" in f.lower() and f.endswith(".qmd"):
                        qmd_path = os.path.join(root, f)
                        break

        if not os.path.exists(qmd_path):
            return {"status": "skipped", "message": f"No purchases .qmd found for '{char_id}'"}

        parsed = cls.parse_purchases_qmd(qmd_path)
        data = char_record["data"]
        changes = []

        # 1. Sync Drone Modifications & Quantities
        drones = data.get("drones", []) + data.get("vehicles", [])
        parsed_drones = parsed.get("drone_modifications", {})
        parsed_drone_qtys = parsed.get("drone_quantities", {})

        for d in drones:
            if not isinstance(d, dict):
                continue
            d_name = d.get("name", "")
            # Match drone
            matched_mods = None
            for p_name, p_mods in parsed_drones.items():
                if p_name.lower() in d_name.lower() or d_name.lower() in p_name.lower():
                    matched_mods = p_mods
                    break

            if matched_mods is not None and len(matched_mods) > 0:
                old_mods = list(d.get("modifications", []))
                if old_mods != matched_mods:
                    d["modifications"] = matched_mods
                    changes.append(f"Updated {d_name} modifications ({len(matched_mods)} mods synced from purchases.qmd)")

            for p_name, p_qty in parsed_drone_qtys.items():
                if p_name.lower() in d_name.lower() or d_name.lower() in p_name.lower():
                    old_qty = d.get("quantity", d.get("qty", 1))
                    if old_qty != p_qty:
                        d["quantity"] = p_qty
                        changes.append(f"Updated {d_name} quantity ({old_qty} -> {p_qty})")
                    break

        # 2. Sync SINs & Licenses
        parsed_sins = parsed.get("sins", [])
        parsed_licenses = parsed.get("licenses", [])

        if parsed_sins:
            old_sins = data.get("sins", [])
            # Check if ratings or items changed
            if old_sins != parsed_sins:
                data["sins"] = parsed_sins
                changes.append(f"Updated SINs from purchases.qmd ({len(parsed_sins)} SINs synced)")

        if parsed_licenses:
            old_lics = data.get("licenses", [])
            # Normalize comparison
            lics_to_save = []
            for lic in parsed_licenses:
                lic_entry = {"name": lic["name"], "sin": lic["sin"]}
                if lic.get("rating") and lic["rating"] > 1:
                    lic_entry["rating"] = lic["rating"]
                lics_to_save.append(lic_entry)

            if old_lics != lics_to_save:
                data["licenses"] = lics_to_save
                changes.append(f"Updated Licenses from purchases.qmd ({len(lics_to_save)} licenses synced)")

        # 3. Sync Activesofts
        parsed_activesofts = parsed.get("activesofts", [])
        if parsed_activesofts:
            old_softs = data.get("activesofts", [])
            if old_softs != parsed_activesofts:
                data["activesofts"] = parsed_activesofts
                changes.append(f"Updated Activesofts from purchases.qmd ({len(parsed_activesofts)} softs synced)")

        # 4 & 4b. Sync Skill Specializations, Expertises & Ranks
        changes.extend(
            cls.apply_skill_updates(
                data.get("skills", []),
                parsed.get("specializations", []),
                parsed.get("skill_ranks", []),
            )
        )

        # 5. Sync Qualities
        parsed_qualities = parsed.get("qualities", [])
        if parsed_qualities:
            from sr6core.character.ledger import _query_db_row
            quals = data.setdefault("qualities", {"positive": [], "negative": []})
            pos_quals = quals.setdefault("positive", [])
            neg_quals = quals.setdefault("negative", [])
            for q in parsed_qualities:
                q_name = q.get("name", "")
                q_ref = q.get("ref", q_name.lower().replace(" ", "_"))
                row = _query_db_row(
                    "SELECT quality_type FROM ref_qualities WHERE id = ? OR name = ? COLLATE NOCASE",
                    (q_ref, q_name)
                )
                if not row and "(" in q_name:
                    base_name = re.sub(r'\(.*?\)', '', q_name).strip()
                    base_ref = base_name.lower().replace(" ", "_")
                    row = _query_db_row(
                        "SELECT quality_type FROM ref_qualities WHERE id = ? OR name = ? COLLATE NOCASE",
                        (base_ref, base_name)
                    )
                is_neg = (row and row.get("quality_type") == "negative") or "negative" in q_name.lower()
                target_list = neg_quals if is_neg else pos_quals
                opposite_list = pos_quals if is_neg else neg_quals
                # Remove any stale entry from the opposite polarity list
                before_len = len(opposite_list)
                opposite_list[:] = [
                    eq for eq in opposite_list
                    if eq.get("ref") != q_ref and eq.get("name", "").lower() != q_name.lower()
                ]
                if len(opposite_list) < before_len:
                    changes.append(f"Removed misclassified Quality '{q_name}' from {'positive' if is_neg else 'negative'} qualities")
                if not any(eq.get("ref") == q_ref or eq.get("name", "").lower() == q_name.lower() for eq in target_list):
                    target_list.append(q)
                    changes.append(f"Added Quality '{q_name}' to {'negative' if is_neg else 'positive'} qualities from purchases.qmd")

        # 6. Sync Matrix Devices
        parsed_devices = parsed.get("matrix_devices", [])
        if parsed_devices:
            old_devices = data.get("matrix_devices", [])
            if old_devices != parsed_devices:
                data["matrix_devices"] = parsed_devices
                changes.append(f"Updated Matrix Devices from purchases.qmd ({len(parsed_devices)} devices synced)")

        # 7. Sync Combat Weapons & Battery Gear Labels (when eye-mounted laser arrays, Tesla Coil, or Ram Plate change in ### Combat)
        combat_items = parsed.get("combat_items", [])
        combat_low = " ".join(combat_items).lower()
        weapons_block = data.get("weapons")
        if combat_items and isinstance(weapons_block, dict):
            ranged_list = weapons_block.get("ranged", [])
            wasp_templates = [
                {
                    "name": "Dual Eye Lasers",
                    "damage": "7P*",
                    "attack_rating": "22/20/17/12/-",
                    "mode": "SA/SS",
                    "ammo": "30(c)",
                    "smartlink": True,
                    "precomputed_ar": True,
                    "is_vehicle_mounted": True,
                    "link_fired_count": 2,
                    "accessories": [
                        "Smartlink (+2 AR)",
                        "Drone Mount (+2 AR)",
                        "M-TOC II (+1 AR)",
                        "Link-Fired (2x Crimson Wasps, Minor Action)",
                    ],
                    "notes": "FS p. 44 / DC p. 143. Dual Crimson Wasps (Crimson Wasp Array, 2x Link-Fired in Small Eye Mounts; Costs Minor Action; +2 DV, +1 AR). 1 Wild Die. Decreases by 2P (to 5P*) at Medium range.",
                },
                {
                    "name": "Eye Beam",
                    "damage": "5P*",
                    "attack_rating": "21/19/16/11/-",
                    "mode": "SA/SS",
                    "ammo": "30(c)",
                    "smartlink": True,
                    "precomputed_ar": True,
                    "is_vehicle_mounted": True,
                    "link_fired_count": 1,
                    "accessories": [
                        "Smartlink (+2 AR)",
                        "Drone Mount (+2 AR)",
                        "M-TOC II (+1 AR)",
                    ],
                    "notes": "FS p. 44. Single Crimson Wasp (Eye Mount, Independent; NO Minor Action required). 1 Wild Die. Decreases to 3P at Medium range.",
                },
                {
                    "name": "Lightning Breath",
                    "category": "Cyberweapons",
                    "damage": "5S(e)",
                    "attack_rating": "10/12/-/-/-",
                    "mode": "SS",
                    "ammo": "5(c)",
                    "max_range": "20m",
                    "area_effect": "Straight Line (Flamethrower rules)",
                    "is_vehicle_mounted": True,
                    "accessories": ["MAA Cyberarm Mount (+2 AR)"],
                    "notes": "BS p. 49 / CRB p. 117. Tesla Coil (single target / Straight). Direct stream spray attack (first valid target on 20m line). Cyberarm Mount (+2 AR). 5(c) capacitor bank.",
                },
                {
                    "name": "Mega Lightning Breath",
                    "category": "Cyberweapons",
                    "damage": "4S(e)",
                    "attack_rating": "12/14/-/-/-",
                    "mode": "SS",
                    "ammo": "5(c)",
                    "max_range": "20m",
                    "area_effect": "8.58° Cone (3m width at 20m)",
                    "apex_angle": 8.58,
                    "is_vehicle_mounted": True,
                    "accessories": ["MAA Cyberarm Mount (+2 AR)"],
                    "notes": "BS p. 49 / CRB p. 117. Tesla Coil (narrow cone / Wobbly). Wobbly spray attack (+2 AR, -1 DV). 8.58° apex cone (3m wide @ 20m). Optional Wild Die. Cyberarm Mount (+2 AR). 5(c) capacitor bank.",
                },
                {
                    "name": "Giga Lightning Breath",
                    "category": "Cyberweapons",
                    "damage": "2S(e)",
                    "attack_rating": "14/16/-/-/-",
                    "mode": "SS",
                    "ammo": "5(c)",
                    "max_range": "20m",
                    "area_effect": "28.07° Cone (10m width at 20m)",
                    "apex_angle": 28.07,
                    "is_vehicle_mounted": True,
                    "accessories": ["MAA Cyberarm Mount (+2 AR)"],
                    "notes": "BS p. 49 / CRB p. 117. Tesla Coil (wide cone / Sweeping). Sweeping spray attack (+4 AR, -3 DV). 28.07° apex cone (10m wide @ 20m). Optional Wild Die. Cyberarm Mount (+2 AR). 5(c) capacitor bank.",
                },
            ]
            if ("crimson wasp" in combat_low or "dual eye lasers" in combat_low) and ranged_list != wasp_templates:
                weapons_block["ranged"] = wasp_templates
                changes.append("Synced Dual Eye Lasers / Eye Beam / Lightning Breath weapons from purchases.qmd")

            gear_list = data.get("gear", [])
            if "crimson wasp" in combat_low and isinstance(gear_list, list):
                for g in gear_list:
                    if isinstance(g, dict) and "peak-discharge laser battery" in str(g.get("name", "")).lower() and "red fox" in str(g.get("name", "")).lower():
                        g["name"] = re.sub(r"\(Red Fox\)", "(Crimson Wasp)", g["name"], flags=re.IGNORECASE)
                        changes.append("Updated laser battery clip label to Crimson Wasp")

            # Sync Rating 9 Autosofts to Gear (Software Emulator rules) and prune Mapsoft/Shopsoft/Commlink Apps from Gear
            parsed_autosofts = parsed.get("autosofts", [])
            if parsed_autosofts and isinstance(gear_list, list):
                cleaned_gear = [
                    g for g in gear_list
                    if not (
                        isinstance(g, dict)
                        and (
                            any(k in str(g.get("name", "")).lower() for k in (
                                "mapsoft", "shopsoft", "facial scanner", "p-ice spines",
                                "personal assistant", "social hud", "thermal mood", "vocal tension",
                            ))
                            or str(g.get("category", "")).lower() == "autosoft"
                        )
                    )
                ]
                for a_str in parsed_autosofts:
                    if "r9" not in a_str.lower() and "rating 9" not in a_str.lower():
                        continue
                    is_emulated = any(
                        em in a_str.lower()
                        for em in ("clearsight", "close combat", "evasion", "maneuvering", "stealth", "targeting", "tracking")
                    )
                    cleaned_gear.append({
                        "name": a_str,
                        "rating": 9,
                        "qty": 1,
                        "category": "Autosoft",
                        "notes": (
                            "Rating 9 Autosoft (learned via Software Emulator Echo, 1 Karma; always slotted)."
                            if is_emulated
                            else "Rating 9 Autosoft (always slotted via Living Persona / Software Emulator)."
                        ),
                    })
                if cleaned_gear != gear_list:
                    data["gear"] = cleaned_gear
                    changes.append("Synced R9 Autosofts to gear and pruned Mapsoft/Shopsoft/Commlink Apps from gear")

            close_list = weapons_block.get("close_combat", [])
            has_ram_plate_mod = any(
                "ram plate" in str(m).lower()
                for d in data.get("drones", []) if isinstance(d, dict)
                for m in d.get("modifications", [])
            )
            has_wrist_shield_mod = any(
                "wrist shield" in str(m).lower()
                for d in data.get("drones", []) if isinstance(d, dict)
                for m in d.get("modifications", [])
            )
            if isinstance(close_list, list):
                new_close = [
                    {
                        "name": "Amalgam Cestas",
                        "damage": "3P",
                        "attack_rating": "14/-/-/-/-",
                        "category": "close_combat",
                        "is_melee": True,
                        "precomputed_ar": True,
                        "personalized_grip": True,
                        "accessories": ["Personalized Grip"],
                        "notes": "Scotophobia p. 181. Amalgam Tech Cestas; 3P damage, overrides magical immunity to normal weapons (ItNW). AR = STR (3) + REA/Sleaze (9) + Personalized Grip (2) = 14. 1 Wild Die.",
                    },
                    {
                        "name": "Unarmed Combat (Narcoslap)",
                        "damage": "2S",
                        "attack_rating": "12/-/-/-/-",
                        "category": "close_combat",
                        "is_melee": True,
                        "precomputed_ar": True,
                        "notes": "CRB p. 109. Unarmed strike / Narcoject dermal delivery (Man-at-Arms Cyberarm STR 3 + AI REA/Sleaze 9 = AR 12). Attack Pool: Targeting (DP, 7) + Sensors (10) + Ally TW (4) = 21d6.",
                    },
                ]
                if has_wrist_shield_mod:
                    new_close.append({
                        "name": "Wrist Shield",
                        "damage": "2P/3S",
                        "attack_rating": "9/-/-/-/-",
                        "category": "close_combat",
                        "is_melee": True,
                        "precomputed_ar": True,
                        "notes": "Body Shop p. 49. Concealed 1m forearm disc (Left Synthetic Cyberarm); Minor Action deploy (+4 DR, hands-free). AR = Base (6) + Cyberarm STR (3) = 9. Damage: 2P (Blades) / 3S (Clubs).",
                    })
                if has_ram_plate_mod:
                    new_close.append({
                        "name": "Drone Martial Arts",
                        "damage": "8P",
                        "attack_rating": "33 (39)/-/-/-/-",
                        "category": "close_combat",
                        "is_melee": True,
                        "skill": "piloting",
                        "notes": (
                            "CRB p. 201 / DC p. 144. Vehicle Ramming w/ Ram Plate (Shiawase Man-at-Arms). "
                            "Attack roll is a Piloting test (Maneuvering 7 + Pilot/RES vs. Defense, -1 Threshold via Pilot Origins). "
                            "AR = Piloting (7) + Sensors (11 passive / 17 Enlightened) + Ram Plate Body (15) = 33 (39). "
                            "Base DV = BOD/2 rounded up (Body 15 / 2 = 8P) + 1 per Speed Interval. "
                            "Ram Plate moves blowback damage to BOD/8 (vehicles) and BOD/16 (non-vehicles)."
                        ),
                    })
                if close_list != new_close:
                    weapons_block["close_combat"] = new_close
                    changes.append("Synced Amalgam Cestas, Unarmed Combat (Narcoslap), Wrist Shield, and Drone Martial Arts")

        # Save back to YAML if changes occurred
        if changes:
            yaml_path = char_record["path"]
            with open(yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        return {
            "status": "success",
            "char_id": char_id,
            "changes_count": len(changes),
            "changes": changes,
            "parsed_drone_mods": parsed_drones,
            "parsed_sins": parsed_sins,
            "parsed_licenses": parsed_licenses
        }

    @classmethod
    def sync_all(cls) -> List[Dict[str, Any]]:
        """Syncs all available character portfolios."""
        cm = CharacterManager()
        results = []
        for c in cm.list_characters():
            cid = c["id"]
            if c.get("exists"):
                res = cls.sync_character_purchases(cid)
                results.append(res)
        return results
