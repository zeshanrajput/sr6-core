"""
Purchases Sync Engine for SR6 Core.
Parses character_purchases.qmd and synchronizes drone modifications,
inventory, foci, SINs, licenses, and gear into character_master.yaml automatically.
"""

import os
import re
from typing import Dict, List, Any, Optional
import yaml
from sr6core.character_manager import CharacterManager


class PurchasesSyncEngine:
    @staticmethod
    def clean_item_text(line: str) -> str:
        """Strips markdown asterisks, whitespace, backticks, and Quarto `{python} ...` code from line."""
        # Strip inline backtick code containing python or inc expressions
        cleaned = re.sub(r'`\s*\{?python[^\`]*\}?\s*`', '', line)
        cleaned = re.sub(r'\{python[^\}]*\}', '', cleaned)
        cleaned = re.sub(r'`\s*inc(_many)?[^\`]*`', '', cleaned)
        cleaned = re.sub(r'`[^`]*`', '', cleaned)
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
        autosofts: List[str] = []
        programs: List[str] = []
        commlink_apps: List[str] = []
        gear_items: List[str] = []
        sins: List[Dict[str, Any]] = []
        licenses: List[Dict[str, Any]] = []

        # Keywords that represent sub-headers or nested sub-items, not top-level modifications
        ignore_mod_prefixes = [
            'stores ', 'wearable', 'accessories', 'crimson wasp', 'mct gnat',
            'm-toc ii', 'foundation host', 'stores'
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
                    # Top-level drone entry (e.g. * Shiawase Man-At-Arms ...)
                    drone_title = cls.clean_item_text(stripped)
                    # Normalize drone name
                    current_drone = drone_title.split('(')[0].strip()
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
                    norm_mod = re.sub(r'Weapon Mount\s*-\s*Standard', 'Weapon Mount (Standard)', norm_mod, flags=re.IGNORECASE)
                    norm_mod = re.sub(r'Pop-Out Concealment\s*-\s*Standard', 'Pop-Out Concealment (Standard)', norm_mod, flags=re.IGNORECASE)
                    norm_mod = re.sub(r'Retractible Skates.*', 'Retractable Skates', norm_mod, flags=re.IGNORECASE)
                    norm_mod = re.sub(r'Retractable Skates.*', 'Retractable Skates', norm_mod, flags=re.IGNORECASE)
                    norm_mod = re.sub(r':$', '', norm_mod).strip()

                    if norm_mod and norm_mod not in drone_mods[current_drone]:
                        drone_mods[current_drone].append(norm_mod)

            # In Matrix & Software section
            elif current_section == 'matrix':
                if 'autosoft' in stripped.lower() and stripped.startswith('*'):
                    current_sub_category = 'autosofts'
                elif 'program' in stripped.lower() and stripped.startswith('*'):
                    current_sub_category = 'programs'
                elif 'commlink app' in stripped.lower() and stripped.startswith('*'):
                    current_sub_category = 'commlink_apps'
                elif current_sub_category == 'autosofts' and (raw_line.startswith('  *') or raw_line.startswith('    *')):
                    item_name = cls.clean_item_text(stripped)
                    if item_name and item_name not in autosofts:
                        autosofts.append(item_name)
                elif current_sub_category == 'programs' and (raw_line.startswith('  *') or raw_line.startswith('    *')):
                    item_name = cls.clean_item_text(stripped)
                    if item_name and item_name not in programs:
                        programs.append(item_name)
                elif current_sub_category == 'commlink_apps' and (raw_line.startswith('  *') or raw_line.startswith('    *')):
                    item_name = cls.clean_item_text(stripped)
                    if item_name and item_name not in commlink_apps:
                        commlink_apps.append(item_name)

            # In SINs & Licenses section
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

        return {
            "drone_modifications": drone_mods,
            "autosofts": autosofts,
            "programs": programs,
            "commlink_apps": commlink_apps,
            "gear": gear_items,
            "sins": sins,
            "licenses": licenses
        }

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

        # Find character_purchases.qmd
        qmd_path = os.path.join(repo_dir, "chapters", "character_purchases.qmd")
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

        # 1. Sync Drone Modifications
        drones = data.get("drones", []) + data.get("vehicles", [])
        parsed_drones = parsed.get("drone_modifications", {})

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
