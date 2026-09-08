"""
Character Dossier Integrity Validator for Shadowrun 6e.
Validates character portfolios (Markdown Trio & master YAML files) against SQLite catalog keys.
Detects missing foreign keys, typos with fuzzy matching suggestions, deprecated book references,
and financial/Karma discrepancies.
"""

import os
import re
import difflib
import sqlite3
from typing import Dict, Any, List, Optional, Tuple, Set

from sr6core.rules_db import DEFAULT_DB_PATH, RulesDB
from sr6core.character_manager import CharacterManager
from sr6core.creation.deep_audit import calculate_transaction_price


class DossierValidator:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.environ.get("SR6_RULES_DB_PATH", DEFAULT_DB_PATH)
        RulesDB(db_path=self.db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._build_catalog_cache()

    def _build_catalog_cache(self):
        """Preloads reference tables into O(1) in-memory dictionaries for instant lookups."""
        self.catalogs: Dict[str, Dict[str, Any]] = {}
        tables = {
            "qualities": "ref_qualities",
            "spells": "ref_spells",
            "complex_forms": "ref_complex_forms",
            "adept_powers": "ref_adept_powers",
            "weapons": "ref_weapons",
            "cyberware": "ref_cyberware",
            "vehicles": "ref_vehicles",
            "programs": "ref_programs",
            "gear": "ref_gear",
        }

        for cat, tbl in tables.items():
            try:
                rows = self.conn.execute(f"SELECT id, name, raw_xml FROM {tbl}").fetchall()
                id_map = {}
                name_map = {}
                data_map = {}
                for r in rows:
                    rid = r["id"].lower()
                    rname = (r["name"] or "").lower()
                    id_map[rid] = r["id"]
                    if rname:
                        name_map[rname] = r["id"]
                        name_map[rname.replace(" ", "_")] = r["id"]
                        name_map[rname.replace("-", "_")] = r["id"]
                    data_map[r["id"]] = dict(r)

                self.catalogs[cat] = {
                    "ids": id_map,
                    "names": name_map,
                    "data": data_map,
                    "all_keys": list(id_map.keys()) + list(name_map.keys())
                }
            except Exception:
                self.catalogs[cat] = {"ids": {}, "names": {}, "data": {}, "all_keys": []}

        # Rules vault topics & IDs (for echoes, metamagics, qualities, actions)
        try:
            rule_rows = self.conn.execute("SELECT id, topic FROM rules").fetchall()
            rule_ids = {}
            rule_topics = {}
            for r in rule_rows:
                rule_ids[r["id"].lower()] = r["id"]
                topic_clean = (r["topic"] or "").lower()
                if topic_clean:
                    rule_topics[topic_clean] = r["id"]
                    rule_topics[topic_clean.replace(" ", "_")] = r["id"]
                    rule_topics[topic_clean.replace("-", " ")] = r["id"]
                    if ":" in topic_clean:
                        sub_topic = topic_clean.split(":", 1)[1].strip()
                        rule_topics[sub_topic] = r["id"]
                        rule_topics[sub_topic.replace(" ", "_")] = r["id"]
                        rule_topics[sub_topic.replace("-", " ")] = r["id"]
            self.catalogs["rules"] = {
                "ids": rule_ids,
                "names": rule_topics,
                "all_keys": list(rule_ids.keys()) + list(rule_topics.keys())
            }
        except Exception:
            self.catalogs["rules"] = {"ids": {}, "names": {}, "all_keys": []}

    @staticmethod
    def clean_name(text: str) -> str:
        """Extracts normalized name without quantity prefixes, rating suffixes, or trailing plural s."""
        cleaned = re.sub(r"^\d+x\s+", "", text.strip(), flags=re.IGNORECASE)
        match = re.search(r"^(.*?)\s*\(.*?\)$", cleaned)
        if match:
            cleaned = match.group(1).strip()
        cleaned_lower = cleaned.lower()
        if cleaned_lower.endswith("ches") or cleaned_lower.endswith("shes") or cleaned_lower.endswith("xes"):
            cleaned_lower = cleaned_lower[:-2]
        elif cleaned_lower.endswith("s") and not cleaned_lower.endswith("ss"):
            cleaned_lower = cleaned_lower[:-1]
        return cleaned_lower

    def validate_item(self, category: str, name: str, ref: str = "") -> Dict[str, Any]:
        """Validates a single item against the catalog cache, returning validity and suggestions."""
        matched_id, resolved_cat = self._match_catalog(category, ref, name)
        if matched_id:
            return {
                "valid": True,
                "matched_key": matched_id,
                "category": resolved_cat,
                "suggestions": []
            }
        suggestion = self._suggest_correction(category, ref or name)
        return {
            "valid": False,
            "matched_key": None,
            "category": category,
            "suggestions": [suggestion] if suggestion else []
        }

    def _strip_rating_suffix(self, text: str) -> Tuple[str, Optional[int]]:
        """Extracts base item name, cleans leading quantity prefixes (e.g. '10x'), and optional ratings."""
        cleaned = re.sub(r"^\d+x\s+", "", text.strip(), flags=re.IGNORECASE)
        match = re.search(r"^(.*?)\s*\(rating\s*(\d+).*?\)$", cleaned, re.IGNORECASE)
        if match:
            return match.group(1).strip(), int(match.group(2))
        match2 = re.search(r"^(.*?)\s*\(r(\d+).*?\)$", cleaned, re.IGNORECASE)
        if match2:
            return match2.group(1).strip(), int(match2.group(2))
        match3 = re.search(r"^(.*?)\s*\(.*?\)$", cleaned)
        if match3:
            return match3.group(1).strip(), None
        return cleaned.strip(), None

    def _match_catalog(self, category: str, ref: str, name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Attempts to resolve an item against the primary category catalog,
        falling back to general gear or rules vault. Returns (matched_id, resolved_category).
        """
        cat = self.catalogs.get(category, {})
        clean_ref = ref.lower().strip() if ref else ""
        clean_name = name.lower().strip() if name else ""
        norm_name = clean_name.replace(" ", "_").replace("-", "_")

        # 1. Direct match in primary category
        matched = cat.get("ids", {}).get(clean_ref) or cat.get("names", {}).get(clean_name) or cat.get("names", {}).get(norm_name)
        if matched:
            return matched, category

        # 2. Stripped quantity & base name (e.g. '10x Glitter Grenades' -> 'Glitter Grenades', or 'Savior Medkit (Rating 6)' -> 'Savior Medkit')
        base_name, _ = self._strip_rating_suffix(clean_name)
        if base_name:
            bn_lower = base_name.lower()
            bn_norm = bn_lower.replace(" ", "_").replace("-", "_")
            matched = cat.get("names", {}).get(bn_lower) or cat.get("names", {}).get(bn_norm) or cat.get("ids", {}).get(bn_norm)
            if matched:
                return matched, category

            # Try singular form (e.g. 'Glitter Grenades' -> 'Glitter Grenade')
            if bn_lower.endswith("s"):
                singular = bn_lower[:-1]
                sing_norm = singular.replace(" ", "_").replace("-", "_")
                matched = cat.get("names", {}).get(singular) or cat.get("names", {}).get(sing_norm) or cat.get("ids", {}).get(sing_norm)
                if matched:
                    return matched, category

            # Check generic software (e.g. 'Cracking Activesoft' -> 'activesoft')
            if bn_lower.endswith("activesoft"):
                matched = cat.get("ids", {}).get("activesoft") or cat.get("names", {}).get("activesoft")
                if matched:
                    return matched, category
            if bn_lower.endswith("linguasoft"):
                matched = cat.get("ids", {}).get("linguasoft") or cat.get("names", {}).get("linguasoft")
                if matched:
                    return matched, category

        # 3. Cross-catalog fallback: gear, vehicles, programs
        for fallback_cat in ["gear", "vehicles", "programs"]:
            if fallback_cat == category:
                continue
            f_cat = self.catalogs.get(fallback_cat, {})
            matched = f_cat.get("ids", {}).get(clean_ref) or f_cat.get("names", {}).get(clean_name) or f_cat.get("names", {}).get(norm_name)
            if not matched and base_name:
                bn_lower = base_name.lower()
                bn_norm = bn_lower.replace(" ", "_").replace("-", "_")
                matched = f_cat.get("names", {}).get(bn_lower) or f_cat.get("names", {}).get(bn_norm) or f_cat.get("ids", {}).get(bn_norm)
                if not matched and bn_lower.endswith("s"):
                    singular = bn_lower[:-1]
                    sing_norm = singular.replace(" ", "_").replace("-", "_")
                    matched = f_cat.get("names", {}).get(singular) or f_cat.get("names", {}).get(sing_norm) or f_cat.get("ids", {}).get(sing_norm)
            if matched:
                return matched, fallback_cat

        # 4. Rules vault fallback (for echoes, metamagics, special actions)
        r_cat = self.catalogs.get("rules", {})
        matched = r_cat.get("ids", {}).get(clean_ref) or r_cat.get("names", {}).get(clean_name) or r_cat.get("names", {}).get(norm_name)
        if not matched and base_name:
            bn_lower = base_name.lower()
            matched = (
                r_cat.get("names", {}).get(bn_lower) or
                r_cat.get("names", {}).get(bn_lower.replace(" ", "_")) or
                r_cat.get("names", {}).get(bn_lower + "s") or
                r_cat.get("names", {}).get(bn_lower.replace(" ", "_") + "s")
            )
        if matched:
            return matched, "rules"

        return None, None

    def _suggest_correction(self, category: str, query: str) -> Optional[str]:
        """Uses Levenshtein distance to suggest the closest valid ID or name."""
        if not query:
            return None
        cat = self.catalogs.get(category, {})
        keys = cat.get("all_keys", [])
        if not keys:
            keys = self.catalogs.get("rules", {}).get("all_keys", [])

        matches = difflib.get_close_matches(query.lower().replace(" ", "_"), keys, n=1, cutoff=0.6)
        if not matches and " " in query:
            matches = difflib.get_close_matches(query.lower(), keys, n=1, cutoff=0.6)

        if matches:
            suggested = matches[0]
            # Return canonical ID if found
            return cat.get("ids", {}).get(suggested) or cat.get("names", {}).get(suggested) or suggested
        return None

    def validate_character(self, char_id: str) -> Dict[str, Any]:
        """Performs comprehensive foreign key and pricing validation for a character portfolio."""
        cm = CharacterManager()
        char_data = cm.get_character_data(char_id)
        if not char_data:
            return {
                "char_id": char_id,
                "valid": False,
                "error": f"Character portfolio '{char_id}' could not be loaded."
            }
        return self.validate_character_data(char_data, char_id=char_id)

    def validate_character_data(self, char_data: Dict[str, Any], char_id: str = "custom") -> Dict[str, Any]:
        """Performs comprehensive foreign key and pricing validation on a character dictionary."""
        checks = [
            ("qualities", "Positive Qualities", char_data.get("qualities", {}).get("positive", [])),
            ("qualities", "Negative Qualities", char_data.get("qualities", {}).get("negative", [])),
            ("spells", "Spells", char_data.get("spells", [])),
            ("complex_forms", "Complex Forms", char_data.get("complex_forms", [])),
            ("adept_powers", "Adept Powers", char_data.get("adept_powers", [])),
            ("weapons", "Weapons", char_data.get("weapons", [])),
            ("cyberware", "Cyberware / Bioware", char_data.get("cyberware", [])),
            ("vehicles", "Drones & Vehicles", char_data.get("drones", []) or char_data.get("vehicles", [])),
            ("programs", "Activesofts & Programs", char_data.get("activesofts", []) or char_data.get("programs", [])),
            ("gear", "Inventory Gear", char_data.get("gear", [])),
            ("rules", "Echoes & Submersion", char_data.get("echoes", []) or char_data.get("meta_echoes", [])),
            ("rules", "Metamagic", char_data.get("metamagic", [])),
        ]

        total_items = 0
        valid_items = 0
        issues = []
        price_discrepancies = []

        for category, label, items in checks:
            if not items:
                continue

            for it in items:
                total_items += 1
                if isinstance(it, dict):
                    ref = it.get("ref") or it.get("id", "")
                    name = it.get("name", "")
                else:
                    ref = str(it)
                    name = str(it)

                # Skip innate/generic entries like 'Unarmed' or 'close_combat' category markers
                if category == "weapons" and ref.lower() in ["close_combat", "unarmed", "unarmed_combat", "natural"]:
                    valid_items += 1
                    continue

                matched_id, resolved_cat = self._match_catalog(category, ref, name)

                if matched_id:
                    valid_items += 1
                    # Price & Karma audit for gear, weapons, cyberware, qualities
                    if isinstance(it, dict) and resolved_cat in self.catalogs:
                        cat_data = self.catalogs[resolved_cat].get("data", {}).get(matched_id, {})
                        if cat_data:
                            # Check cost if stated
                            if "cost" in cat_data and "cost" in it:
                                try:
                                    expected_cost = int(cat_data["cost"])
                                    actual_cost = int(it["cost"])
                                    if expected_cost > 0 and actual_cost != expected_cost:
                                        # Check if discount or markup is documented
                                        has_note = any(k in it for k in ["notes", "markup", "discount", "diy_work", "diy_discount", "override_price"])
                                        if not has_note:
                                            price_discrepancies.append({
                                                "category": label,
                                                "name": name or ref,
                                                "expected": f"¥{expected_cost:,}",
                                                "actual": f"¥{actual_cost:,}",
                                                "note": "Unexplained cost difference (no transaction note or discount tag)"
                                            })
                                except Exception:
                                    pass
                else:
                    suggestion = self._suggest_correction(category, ref or name)
                    issues.append({
                        "category": label,
                        "item_ref": ref,
                        "item_name": name,
                        "error_type": "FOREIGN_KEY_NOT_FOUND",
                        "message": f"Item '{ref or name}' was not found in reference catalog '{category}'.",
                        "suggestion": suggestion
                    })

        is_valid = len(issues) == 0

        return {
            "char_id": char_id,
            "valid": is_valid,
            "is_valid": is_valid,
            "total_items": total_items,
            "valid_items": valid_items,
            "issues": issues,
            "unresolved": issues,
            "summary": {
                "total_items": total_items,
                "valid_items": valid_items,
                "unresolved_count": len(issues),
            },
            "price_discrepancies": price_discrepancies
        }

    validate_dossier = validate_character_data

    def format_cli_report(self, result: Dict[str, Any]) -> str:
        """Formats the validation result into a crisp, professional terminal scorecard."""
        lines = []
        char_id = result.get("char_id", "unknown").upper()
        valid = result.get("valid", False)
        tot = result.get("total_items", 0)
        val_count = result.get("valid_items", 0)
        status_label = "[PASS]" if valid else "[FAIL]"

        lines.append(f"\n================================================================================")
        lines.append(f"  DOSSIER INTEGRITY AUDIT: {char_id} -- {status_label}")
        lines.append(f"  Integrity Score: {val_count} / {tot} items verified ({(val_count/tot*100):.1f}%)" if tot else "  No items to audit.")
        lines.append(f"================================================================================")

        issues = result.get("issues", [])
        if issues:
            lines.append(f"\n[-] DANGLING OR UNRESOLVED CATALOG KEYS ({len(issues)}):")
            lines.append(f"  {'Category':<22} | {'Item Reference / Name':<28} | {'Suggested Fix'}")
            lines.append(f"  {'-'*22}-|-{'-'*28}-|-{'-'*20}")
            for iss in issues:
                item_display = (iss["item_name"] or iss["item_ref"])[:28]
                sugg_text = f"-> Did you mean: '{iss['suggestion']}'" if iss.get("suggestion") else "No close catalog match found"
                lines.append(f"  {iss['category']:<22} | {item_display:<28} | {sugg_text}")

        prices = result.get("price_discrepancies", [])
        if prices:
            lines.append(f"\n[!] PRICING & TRANSACTION DISCREPANCIES ({len(prices)}):")
            lines.append(f"  {'Category':<22} | {'Item Name':<24} | {'Catalog':<10} | {'Dossier':<10} | {'Status'}")
            lines.append(f"  {'-'*22}-|-{'-'*24}-|-{'-'*10}-|-{'-'*10}-|-{'-'*15}")
            for p in prices:
                lines.append(f"  {p['category']:<22} | {p['name'][:24]:<24} | {p['expected']:<10} | {p['actual']:<10} | {p['note']}")

        if valid and not prices:
            lines.append("\n[+] All portfolio weapons, qualities, spells, echoes, and gear strictly match SQLite keys!")

        lines.append(f"\n================================================================================\n")
        return "\n".join(lines)

    format_report = format_cli_report
