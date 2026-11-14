"""
Official Fillable PDF Character Sheet Exporter for SR6 Core.

Populates Catalyst's official 2-page AcroForm PDF (`templates/SR6-Character-Sheet-Fillable.pdf`)
from a character's compiled dossier and `ModifierEngine` / `export_mobile_json` derivations.
Automatically repairs template defects (4 shared `/Parent` widget name collisions and missing
Multiline flags on the 10 large list containers) while keeping all fields editable for tabletop use.
"""

import os
import re
import textwrap
from typing import Any, Dict, List, Optional, Tuple

import pymupdf

from sr6core.character.ledger import get_log_totals
from sr6core.publishing.mobile_json import export_mobile_json

DEFAULT_TEMPLATE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "templates",
        "SR6-Character-Sheet-Fillable.pdf",
    )
)

# Narrow or dense fields where slightly smaller Helvetica keeps content legible without clipping.
_COMPACT_DA_FIELDS = {
    "Reputation": "(/Helv 6.5 Tf 0 g)",
    "Misc": "(/Helv 6.5 Tf 0 g)",
    "Ethnicity": "(/Helv 7 Tf 0 g)",
    "Primary Armor": "(/Helv 7 Tf 0 g)",
    "Primary Ranged Weapon": "(/Helv 7 Tf 0 g)",
    "Primary Melee Weapon": "(/Helv 7 Tf 0 g)",
    "Primary Ranged Stats": "(/Helv 6.5 Tf 0 g)",
    "Primary Melee Stats": "(/Helv 6.5 Tf 0 g)",
    "Initiative": "(/Helv 7 Tf 0 g)",
    "Matrix Initiative": "(/Helv 6.5 Tf 0 g)",
    "Astral Initiative": "(/Helv 7 Tf 0 g)",
    "Defense Rating": "(/Helv 7 Tf 0 g)",
    "Primary Lifestyle": "(/Helv 7 Tf 0 g)",
    "Licenses": "(/Helv 7 Tf 0 g)",
    "Fake IDs  Related Lifestyles  Funds  Licenses 1": "(/Helv 7 Tf 0 g)",
    "Fake IDs  Related Lifestyles  Funds  Licenses 2": "(/Helv 7 Tf 0 g)",
    "Fake IDs  Related Lifestyles  Funds  Licenses 3": "(/Helv 7 Tf 0 g)",
    "Devices/DR": "(/Helv 6.5 Tf 0 g)",
    "Programs 1": "(/Helv 6.5 Tf 0 g)",
    "Programs 2": "(/Helv 6.5 Tf 0 g)",
    "Programs 3": "(/Helv 6.5 Tf 0 g)",
    "Programs 4": "(/Helv 6.5 Tf 0 g)",
    "Sensor": "(/Helv 6.5 Tf 0 g)",
    "Notes": "(/Helv 5.5 Tf 0 g)",
}


def _clean_pdf_text(text: Any) -> str:
    """Sanitize Unicode punctuation so PDFDocEncoding (Helvetica) renders cleanly without glyphs missing."""
    if text is None:
        return ""
    s = str(text)
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2192": "->",
        "\u2022": "*",
        "\u2026": "...",
        "\u2264": "<=",
        "\u2265": ">=",
        "\u00d7": "x",
        "\ufffd": "-",
    }
    for src, dst in replacements.items():
        s = s.replace(src, dst)
    # Encode/decode via latin-1 to drop unrepresentable non-PDFDocEncoding symbols cleanly.
    return s.encode("latin-1", errors="ignore").decode("latin-1")


def _format_val(base: Any, buffed: Any) -> str:
    """Format an attribute or vehicle stat as `base(buffed)` when modified, else `buffed`."""
    if base is not None and buffed is not None and base != buffed:
        return f"{base}({buffed})"
    val = buffed if buffed is not None else base
    return "" if val is None else str(val)


def _format_ar(ar_val: Any) -> str:
    """Render Attack Rating list or string compactly (e.g., `21/23/21/14/-`)."""
    if isinstance(ar_val, list):
        return "/".join(str(x) if (isinstance(x, (int, float)) and x > 0) or (isinstance(x, str) and x.isdigit() and int(x) > 0) else "-" for x in ar_val[:5])
    if isinstance(ar_val, str) and "/" in ar_val:
        parts = [p.strip() for p in ar_val.split("/")]
        return "/".join("-" if p in ("0", "", "-", "\u2014") else p for p in parts[:5])
    s = _clean_pdf_text(ar_val)
    return "-" if s in ("0", "", "-") else s


def _resolve_repo_path(char_data: Dict[str, Any], char_repo_path: Optional[str]) -> Optional[str]:
    """Resolve character repository directory if caller omitted `char_repo_path`."""
    if char_repo_path and os.path.exists(char_repo_path):
        return char_repo_path
    raw_ident = char_data.get("identity", {}) if isinstance(char_data.get("identity"), dict) else {}
    cid = (
        raw_ident.get("id")
        or char_data.get("id")
        or str(raw_ident.get("handle", "")).lower()
        or str(char_data.get("handle", "")).lower()
    )
    if cid:
        try:
            from sr6core.character.manager import CharacterManager

            resolved = CharacterManager().get_character_repo_dir(cid)
            if resolved and os.path.exists(resolved):
                return resolved
        except Exception:
            pass
    return char_repo_path


def _unlink_collided_widgets(doc: pymupdf.Document) -> List[Tuple[int, int]]:
    """
    Break shared `/Parent` chains on the 4 duplicated field groups in Catalyst's template:
      1. `Age` vs `Height` (Page 1)
      2. `Primary Ranged Stats` vs `Primary Melee Stats` (Page 1, both named `Stats`)
      3. `Body` (Page 1) vs `Vehicle Body` (Page 2)
      4. `Armor` (Page 2 multiline) vs `Vehicle Armor` (Page 2 vehicle grid)

    Returns a list of `(old_parent_xref, child_xref)` tuples for AcroForm `/Fields` sync.
    """
    candidates: Dict[str, List[Tuple[int, pymupdf.Widget]]] = {}
    for pno, page in enumerate(doc):
        for w in page.widgets():
            if w.field_type_string == "Text" and w.field_name in ("Age", "Stats", "Body", "Armor"):
                candidates.setdefault(w.field_name, []).append((pno, w))

    rename_plan: List[Tuple[pymupdf.Widget, str, str]] = []

    age_widgets = sorted(candidates.get("Age", []), key=lambda item: item[1].rect.x0)
    if len(age_widgets) == 2:
        rename_plan.append((age_widgets[0][1], "Age", "/Helv 8 Tf 0 g"))
        rename_plan.append((age_widgets[1][1], "Height", "/Helv 8 Tf 0 g"))

    stats_widgets = sorted(candidates.get("Stats", []), key=lambda item: item[1].rect.y0)
    if len(stats_widgets) == 2:
        rename_plan.append((stats_widgets[0][1], "Primary Ranged Stats", "/Helv 6.5 Tf 0 g"))
        rename_plan.append((stats_widgets[1][1], "Primary Melee Stats", "/Helv 6.5 Tf 0 g"))

    body_widgets = sorted(candidates.get("Body", []), key=lambda item: item[0])
    if len(body_widgets) == 2:
        rename_plan.append((body_widgets[0][1], "Body", "/Helv 8 Tf 0 g"))
        rename_plan.append((body_widgets[1][1], "Vehicle Body", "/Helv 8 Tf 0 g"))

    armor_widgets = sorted(candidates.get("Armor", []), key=lambda item: -item[1].rect.height)
    if len(armor_widgets) == 2:
        rename_plan.append((armor_widgets[0][1], "Armor", "/Helv 6.5 Tf 0 g"))
        rename_plan.append((armor_widgets[1][1], "Vehicle Armor", "/Helv 8 Tf 0 g"))

    reparented: List[Tuple[int, int]] = []
    for widget, new_name, da_str in rename_plan:
        raw_obj = doc.xref_object(widget.xref)
        m = re.search(r"/Parent\s+(\d+)\s+0\s+R", raw_obj)
        if m:
            reparented.append((int(m.group(1)), widget.xref))
        doc.xref_set_key(widget.xref, "Parent", "null")
        doc.xref_set_key(widget.xref, "FT", "/Tx")
        doc.xref_set_key(widget.xref, "T", f"({new_name})")
        doc.xref_set_key(widget.xref, "DA", f"({da_str})")
        if new_name in ("Primary Ranged Stats", "Primary Melee Stats"):
            # Catalyst placed static faint watermark labels inside these two widget rects;
            # an opaque white background keeps populated stats legible.
            doc.xref_set_key(widget.xref, "MK", "<< /BG [ 1 1 1 ] >>")

    return reparented


def _sync_acroform_fields(doc: pymupdf.Document, reparented: List[Tuple[int, int]]) -> None:
    """Replace dead parent xrefs in AcroForm `/Fields` with the newly independent child xrefs."""
    if not reparented:
        return
    cat_xref = doc.pdf_catalog()
    acro_key = doc.xref_get_key(cat_xref, "AcroForm")
    if acro_key[0] != "xref":
        return
    acro_xref = int(acro_key[1].split()[0])
    fields_key = doc.xref_get_key(acro_xref, "Fields")
    if fields_key[0] != "array":
        return

    grouped: Dict[int, List[int]] = {}
    for parent_xref, child_xref in reparented:
        grouped.setdefault(parent_xref, []).append(child_xref)

    fields_str = fields_key[1]
    for parent_xref, child_xrefs in grouped.items():
        parent_token = f"{parent_xref} 0 R"
        children_tokens = " ".join(f"{cx} 0 R" for cx in child_xrefs)
        if parent_token in fields_str:
            fields_str = fields_str.replace(parent_token, children_tokens)

    doc.xref_set_key(acro_xref, "Fields", fields_str)


def _repair_template_fields(doc: pymupdf.Document) -> None:
    """
    Repair Catalyst's official fillable template in-memory before populating values:
      - Unlink the 4 shared `/Parent` widget pairs into independent fields.
      - Set `/Ff 4096` (`PDF_TX_FIELD_IS_MULTILINE`) and 6.5pt Helvetica on the 10 large boxes.
      - Adjust `/DA` font sizing on compact single-line fields so dense strings remain readable.
    """
    reparented = _unlink_collided_widgets(doc)
    _sync_acroform_fields(doc, reparented)

    for page in doc:
        for w in page.widgets():
            if w.field_type_string != "Text":
                continue
            if w.rect.height > 20:
                existing_flags = w.field_flags or 0
                new_flags = existing_flags | pymupdf.PDF_TX_FIELD_IS_MULTILINE
                doc.xref_set_key(w.xref, "Ff", str(new_flags))
                doc.xref_set_key(w.xref, "DA", "(/Helv 6.5 Tf 0 g)")
            elif w.field_name in _COMPACT_DA_FIELDS:
                doc.xref_set_key(w.xref, "DA", f"({_COMPACT_DA_FIELDS[w.field_name]})")


def _sort_vehicles(vehicles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Order primary inhabited chassis ahead of support vehicles and recon micro-drones."""
    priority_tiers = ("man-at-arms", "man_at_arms", "primary chassis", "home", "sky commander")

    def _tier(v: Dict[str, Any]) -> int:
        name = str(v.get("name", "")).lower()
        return next((idx for idx, key in enumerate(priority_tiers) if key in name), len(priority_tiers))

    return sorted(vehicles, key=_tier)


def _build_skills_text(skills: List[Dict[str, Any]], knowledge_skills: List[Dict[str, Any]]) -> str:
    """Format active skills (with specializations) and knowledge/language skills for Page 1."""
    lines: List[str] = []
    for sk in skills:
        s_name = _clean_pdf_text(sk.get("name", "Skill"))
        s_rtg = sk.get("rating", 0)
        s_base = sk.get("base_pool", s_rtg)
        s_buff = sk.get("buffed_pool", s_base)
        pool_str = f"{s_base}({s_buff})d6" if s_base != s_buff else f"{s_buff}d6"
        lines.append(f"{s_name} R{s_rtg} [{pool_str}]")
        specs = sk.get("specializations") or ([sk["specialization"]] if sk.get("specialization") else [])
        spec_pool = sk.get("specialized_pool", s_buff + 2)
        for sp in specs:
            lines.append(f"  * {_clean_pdf_text(sp)}: {spec_pool}d6")

    if knowledge_skills:
        lines.append("-- Knowledge & Languages --")
        for ks in knowledge_skills:
            k_name = _clean_pdf_text(ks.get("name", "Knowledge"))
            rtg = ks.get("rating")
            if ks.get("is_knowsoft"):
                tag = f"Knowsoft R{rtg}" if rtg else "Knowsoft"
            elif ks.get("is_linguasoft"):
                tag = f"Linguasoft R{rtg}" if rtg else "Linguasoft"
            elif ks.get("is_native") or ks.get("level") == "Native":
                tag = "Native"
            elif ks.get("level"):
                tag = _clean_pdf_text(ks.get("level"))
            elif rtg:
                tag = f"R{rtg}"
            else:
                tag = "Knowledge"
            pool = ks.get("pool")
            pool_sfx = f", {pool}d6" if pool else ""
            lines.append(f"{k_name} ({tag}{pool_sfx})")

    return "\n".join(lines)


def _build_qualities_text(qualities_data: Any) -> str:
    """Format positive (`[+]`) and negative (`[-]`) qualities cleanly for the Page 1 box."""
    lines: List[str] = []
    if not isinstance(qualities_data, dict):
        return ""
    for sign, key in (("+", "positive"), ("-", "negative")):
        for q in qualities_data.get(key, []) or []:
            if isinstance(q, dict):
                q_name = _clean_pdf_text(q.get("name", "Quality"))
                details: List[str] = []
                if q.get("rating") is not None:
                    details.append(f"R{q['rating']}")
                if q.get("choice") and str(q["choice"]).lower() not in q_name.lower():
                    details.append(_clean_pdf_text(q["choice"]))
                sfx = f" ({', '.join(details)})" if details else ""
                lines.append(f"[{sign}] {q_name}{sfx}")
            else:
                lines.append(f"[{sign}] {_clean_pdf_text(q)}")
    return "\n".join(lines)


def _build_contacts_text(contacts: List[Dict[str, Any]]) -> str:
    """Format contacts with Connection, Loyalty, and Favor Points (`FP`) for the Page 1 box."""
    lines: List[str] = []
    for c in contacts:
        name = _clean_pdf_text(c.get("name", "Contact"))
        conn = c.get("connection", 1)
        loy = c.get("loyalty", 1)
        fp = c.get("favors", 0)
        arch = _clean_pdf_text(c.get("archetype", ""))
        fp_str = f", {fp:+d} FP" if fp else ""
        arch_str = f" - {arch}" if arch else ""
        lines.append(f"{name} (C{conn}/L{loy}{fp_str}){arch_str}")
    return "\n".join(lines)


def _build_weapons_texts(weapons: List[Dict[str, Any]]) -> Tuple[str, str, Dict[str, str]]:
    """Build Page 2 Ranged & Melee multiline lists plus Page 1 Primary Weapon summary fields."""
    ranged = [w for w in weapons if not w.get("is_melee")]
    melee = [w for w in weapons if w.get("is_melee")]

    ranged_lines: List[str] = []
    for w in ranged:
        name = _clean_pdf_text(w.get("name", "Weapon"))
        dmg = _clean_pdf_text(w.get("damage", "-"))
        ar = _format_ar(w.get("attack_rating") or w.get("attack_rating_str", "-"))
        modes = _clean_pdf_text(w.get("modes_str", "-"))
        ammo = _clean_pdf_text(w.get("ammo", "-"))
        ranged_lines.append(f"{name} | DV {dmg} | {modes} | AR {ar} | {ammo}")

    melee_lines: List[str] = []
    for w in melee:
        name = _clean_pdf_text(w.get("name", "Weapon"))
        dmg = _clean_pdf_text(w.get("damage", "-"))
        ar = _format_ar(w.get("attack_rating") or w.get("attack_rating_str", "-"))
        melee_lines.append(f"{name} | DV {dmg} | AR {ar}")

    primary_fields: Dict[str, str] = {}
    if ranged:
        w0 = ranged[0]
        primary_fields["Primary Ranged Weapon"] = _clean_pdf_text(w0.get("name", ""))
        ar0 = _format_ar(w0.get("attack_rating") or w0.get("attack_rating_str", "-"))
        primary_fields["Primary Ranged Stats"] = _clean_pdf_text(
            f"DV {w0.get('damage', '-')} | {w0.get('modes_str', '-')} | AR {ar0} | {w0.get('ammo', '-')}"
        )
    if melee:
        m0 = melee[0]
        primary_fields["Primary Melee Weapon"] = _clean_pdf_text(m0.get("name", ""))
        mar0 = _format_ar(m0.get("attack_rating") or m0.get("attack_rating_str", "-"))
        primary_fields["Primary Melee Stats"] = _clean_pdf_text(
            f"DV {m0.get('damage', '-')} | AR {mar0}"
        )

    return "\n".join(ranged_lines), "\n".join(melee_lines), primary_fields


def _build_powers_and_spells_texts(
    bundle: Dict[str, Any],
    raw_identity: Dict[str, Any],
    char_data: Dict[str, Any],
) -> Tuple[str, str]:
    """
    Build Page 2 text for:
      1. `Spells/Preparations/Rituals/Complex Forms`
      2. `Adept Powers or Other Abilities` (Echoes, Sprite Symbiosis, Adept Powers, Metamagics, Monad)
    """
    cf_spell_lines: List[str] = []
    for cf in bundle.get("complex_forms", []):
        name = _clean_pdf_text(cf.get("name", "Complex Form"))
        fade = _clean_pdf_text(cf.get("fading", 0))
        dur = _clean_pdf_text(cf.get("duration", "Instant"))
        tgt = _clean_pdf_text(cf.get("target", ""))
        tgt_s = f" [{tgt}]" if tgt else ""
        cf_spell_lines.append(f"{name}{tgt_s} | FV {fade} | {dur}")

    for sp in bundle.get("spells", []):
        name = _clean_pdf_text(sp.get("name", "Spell"))
        drain = _clean_pdf_text(sp.get("drain", 0))
        rng = _clean_pdf_text(sp.get("range", "LOS"))
        dur = _clean_pdf_text(sp.get("duration", "Instant"))
        cf_spell_lines.append(f"{name} | Drain {drain} | {rng} | {dur}")

    other_lines: List[str] = []
    echo_names = [_clean_pdf_text(echo.get("name", "Echo")) for echo in bundle.get("powers", {}).get("echoes", [])]
    if echo_names:
        if len(echo_names) > 4:
            echo_blob = f"Echoes ({len(echo_names)}): " + ", ".join(echo_names)
            other_lines.extend(textwrap.wrap(echo_blob, width=62))
        else:
            for e_name in echo_names:
                other_lines.append(f"[Echo] {e_name}")

    metamagic_names = [
        _clean_pdf_text(mm.get("name", mm) if isinstance(mm, dict) else str(mm))
        for mm in char_data.get("metamagic", []) + char_data.get("metamagics", [])
    ]
    if metamagic_names:
        if len(metamagic_names) > 4:
            other_lines.extend(textwrap.wrap(f"Metamagics ({len(metamagic_names)}): " + ", ".join(metamagic_names), width=62))
        else:
            for m_name in metamagic_names:
                other_lines.append(f"[Metamagic] {m_name}")

    for sp_p in bundle.get("sprite_powers", []):
        name = _clean_pdf_text(sp_p.get("name", "Sprite Power"))
        act = _clean_pdf_text(sp_p.get("action", "Minor")).replace(" Action", "")
        other_lines.append(f"[Symbiosis] {name} ({act})")

    for ap in bundle.get("adept_powers", []):
        name = _clean_pdf_text(ap.get("name", "Power"))
        rtg = f" R{ap['rating']}" if ap.get("rating") is not None else ""
        cost = ap.get("cost", 0)
        other_lines.append(f"[Adept] {name}{rtg} ({cost} PP)")

    for ma in bundle.get("monad_abilities", []):
        name = _clean_pdf_text(ma.get("name", "Monad Ability"))
        act = _clean_pdf_text(ma.get("action", "Passive"))
        other_lines.append(f"[Monad] {name} ({act})")

    sub_grade = raw_identity.get("submersion")
    init_grade = raw_identity.get("initiation")
    if sub_grade and not bundle.get("powers", {}).get("echoes"):
        other_lines.insert(0, f"Submersion Grade: {sub_grade}")
    if init_grade and not char_data.get("metamagic"):
        other_lines.insert(0, f"Initiation Grade: {init_grade}")

    return "\n".join(cf_spell_lines), "\n".join(other_lines)


def _build_sin_license_lines(compiled_sins: List[Dict[str, Any]], lifetime_nuyen: int) -> Tuple[str, str, str, str]:
    """Build single-line `Licenses` summary and up to 3 `Fake IDs / Related Lifestyles / Funds` rows."""
    all_lics: List[str] = []
    id_rows: List[str] = []
    for sin in compiled_sins:
        s_name = _clean_pdf_text(sin.get("name", "Fake SIN")).replace(":  ", ": ")
        s_rtg = sin.get("rating", 1)
        lics = [_clean_pdf_text(l) for l in sin.get("licenses", [])]
        all_lics.extend(lics)
        lic_str = f" | Lics: {', '.join(lics)}" if lics else ""
        if s_name.lower().startswith("fake sin:"):
            id_rows.append(f"R{s_rtg} {s_name}{lic_str}")
        else:
            id_rows.append(f"R{s_rtg} SIN: {s_name}{lic_str}")

    if lifetime_nuyen:
        id_rows.append(f"Lifetime Nuyen Earned: {lifetime_nuyen:,}\u00a5")

    padded = (id_rows + ["", "", ""])[:3]
    licenses_str = ", ".join(dict.fromkeys(all_lics)) if all_lics else "-"
    if len(licenses_str) > 22:
        licenses_str = re.sub(r"\bLicense\b", "Lic", licenses_str)
    return licenses_str, padded[0], padded[1], padded[2]


def _compute_unarmed_summary(attrs_dict: Dict[str, Any], bundle_attrs: Dict[str, Any], modifiers: List[Dict[str, Any]]) -> str:
    """Derive Unarmed DV and Attack Rating (including Bone Density / Neuromuscular bonuses)."""
    rea_v = attrs_dict.get("REA", {}).get("buffed", bundle_attrs.get("reaction", 1))
    str_v = attrs_dict.get("STR", {}).get("buffed", bundle_attrs.get("strength", 1))
    ar_val = int(str_v) + int(rea_v)

    base_dv = 2
    dmg_type = "S"
    additive_dv = 0
    for mod in modifiers or []:
        if not isinstance(mod, dict) or not mod.get("enabled", True):
            continue
        if str(mod.get("target", "")).lower().strip() == "damage:unarmed":
            val = mod.get("value", 0)
            notes_low = str(mod.get("notes", "")).lower()
            if isinstance(val, (int, float)):
                if "base unarmed dv" in notes_low or "bone density" in str(mod.get("name", "")).lower():
                    base_dv = max(base_dv, int(val))
                    if f"{int(val)}p" in notes_low:
                        dmg_type = "P"
                else:
                    additive_dv += int(val)
    return f"AR {ar_val} / {base_dv + additive_dv}{dmg_type}"


def _format_essence(ess_raw: Any, is_ai: bool) -> str:
    if is_ai:
        return "N/A (AI)"
    try:
        ess_f = float(ess_raw)
    except Exception:
        return "6.0"
    if round(ess_f, 2) == round(ess_f, 1):
        return f"{ess_f:.1f}"
    return f"{ess_f:.2f}"


def _chunk_programs(items: List[str], num_slots: int = 4) -> List[str]:
    """Distribute Matrix programs/autosofts evenly across `Programs 1..4` lines."""
    slots = ["", "", "", ""]
    if not items:
        return slots
    idx = 0
    for item in items:
        clean = _clean_pdf_text(item)
        if not slots[idx]:
            slots[idx] = clean
        elif len(slots[idx]) + 2 + len(clean) <= 55:
            slots[idx] = f"{slots[idx]}, {clean}"
        else:
            idx = min(num_slots - 1, idx + 1)
            slots[idx] = clean if not slots[idx] else f"{slots[idx]}, {clean}"
    return slots


def build_pdf_field_map(
    char_data: Dict[str, Any],
    char_repo_path: Optional[str] = None,
) -> Dict[str, str]:
    """
    Compile an `{acroform_field_name: value}` dictionary covering all populated fields
    on Catalyst's official 2-page Shadowrun 6e fillable character sheet.
    """
    resolved_repo = _resolve_repo_path(char_data, char_repo_path)
    bundle = export_mobile_json(char_data, char_repo_path=resolved_repo)
    totals = get_log_totals(resolved_repo) if resolved_repo and os.path.exists(resolved_repo) else {}

    raw_identity = char_data.get("identity", {}) if isinstance(char_data.get("identity"), dict) else {}
    identity = bundle.get("identity", {})
    bundle_attrs = bundle.get("attributes", {})
    attr_dict = {a["code"]: a for a in bundle.get("attributes_list", []) if isinstance(a, dict) and a.get("code")}
    derived = bundle.get("derived", {})

    handle = str(identity.get("handle") or raw_identity.get("handle") or raw_identity.get("name") or "Unknown")
    real_name = str(identity.get("real_name") or raw_identity.get("real_name") or "")
    display_char = f"{handle} ({real_name})" if real_name and real_name != "N/A" and real_name != handle else handle
    metatype = str(identity.get("metatype") or raw_identity.get("metatype") or "Human")
    is_ai = bool(identity.get("is_ai")) or "ai" in metatype.lower()

    archetype_parts = [
        p for p in [
            raw_identity.get("archetype") or identity.get("role"),
            raw_identity.get("mortype"),
            identity.get("stream"),
            identity.get("tradition"),
        ] if p and str(p).lower() != "shadowrunner"
    ]
    if raw_identity.get("submersion"):
        archetype_parts.append(f"Submersion {raw_identity['submersion']}")
    if raw_identity.get("initiation"):
        archetype_parts.append(f"Initiation {raw_identity['initiation']}")
    if identity.get("nanite_volume"):
        archetype_parts.append(f"Nanite Vol {identity['nanite_volume']}")
    notes_header = _clean_pdf_text(" | ".join(dict.fromkeys(str(p) for p in archetype_parts)) or "Shadowrunner")

    karma_avail = totals.get("Karma", identity.get("karma_avail", identity.get("karma", 0)))
    karma_life = totals.get("Lifetime_Karma", identity.get("lifetime_karma", karma_avail))
    raw_nuyen = totals.get("Nuyen", identity.get("nuyen", 0))
    raw_life_nuyen = totals.get("Lifetime_Nuyen", identity.get("lifetime_nuyen", raw_nuyen))
    nuyen_avail = int(float(raw_nuyen or 0))
    nuyen_life = int(float(raw_life_nuyen or 0))

    heat = totals.get("Heat", raw_identity.get("heat", char_data.get("heat", 0)))
    raw_rep = totals.get("Reputation", char_data.get("reputation", {}))
    total_rep = totals.get("Total_Reputation", char_data.get("total_reputation"))
    if isinstance(raw_rep, dict) and raw_rep:
        if len(raw_rep) <= 3:
            rep_str = ", ".join(f"{k}:{v}" for k, v in raw_rep.items())
        else:
            top_reps = sorted(raw_rep.items(), key=lambda kv: abs(kv[1]), reverse=True)[:2]
            top_str = ", ".join(f"{k}:{v}" for k, v in top_reps)
            total_val = total_rep if total_rep is not None else sum(raw_rep.values())
            rep_str = f"{total_val} ({top_str})"
    elif total_rep is not None:
        rep_str = str(total_rep)
    else:
        rep_str = str(raw_rep or 0)

    def _attr_str(code: str, fallback: Any = 1) -> str:
        entry = attr_dict.get(code)
        if entry:
            return _format_val(entry.get("base"), entry.get("buffed"))
        return str(fallback)

    # Magic / Resonance box on Page 1
    if "RES" in attr_dict:
        mag_res_str = _attr_str("RES")
    elif "MAG" in attr_dict:
        mag_res_str = _attr_str("MAG")
    elif bundle_attrs.get("resonance", 0) > 0:
        mag_res_str = str(bundle_attrs["resonance"])
    elif bundle_attrs.get("magic", 0) > 0:
        mag_res_str = str(bundle_attrs["magic"])
    else:
        mag_res_str = "-"

    # Initiatives
    init_obj = bundle.get("initiative", {})
    init_modes = init_obj.get("modes", {}) if isinstance(init_obj, dict) else {}
    phys_mode = init_modes.get("physical") or init_modes.get(init_obj.get("default_mode", "vr_hotsim"), {})
    phys_init_str = f"{phys_mode.get('score', 5)} + {phys_mode.get('dice_str', '1d6')}" if phys_mode else "-"
    if phys_mode and "physical" not in init_modes and phys_mode.get("name"):
        phys_init_str += " (VR)"

    mat_init_raw = _clean_pdf_text(bundle.get("matrix", {}).get("matrix_initiative", "-"))
    mat_init_str = (
        re.sub(r"\s*\([^\)]*Overclock[^\)]*\)", " (VR)", mat_init_raw)
        .replace("(Hot-Sim VR)", "VR")
        .replace("(AR)", "AR")
        .replace(" + ", "+")
        .replace(" / ", "/")
    )

    mag_val = bundle_attrs.get("magic", 0)
    mortype_low = str(raw_identity.get("mortype", "")).lower()
    if mag_val > 0 and ("mystic" in mortype_low or "magician" in mortype_low or bundle.get("spells")):
        log_b = attr_dict.get("LOG", {}).get("buffed", bundle_attrs.get("logic", 1))
        int_b = attr_dict.get("INT", {}).get("buffed", bundle_attrs.get("intuition", 1))
        astral_init_str = f"{int(log_b) + int(int_b)} + 2d6"
    else:
        astral_init_str = "-"

    # Defense Rating & Primary Armor
    armors = bundle.get("armors", [])
    vehicles = _sort_vehicles(bundle.get("vehicles", []))
    primary_v = vehicles[0] if vehicles else None
    bod_b = attr_dict.get("BOD", {}).get("buffed", 1 if is_ai else bundle_attrs.get("body", 1))
    total_dr = derived.get("defense_rating", 0)
    if armors:
        primary_armor_name = _clean_pdf_text(armors[0].get("name", ""))
        primary_armor_rtg = str(armors[0].get("defense_rating", 0))
        def_rating_str = f"{int(bod_b) + int(total_dr)}"
    elif is_ai and primary_v:
        primary_armor_name = f"{_clean_pdf_text(primary_v.get('name', 'Chassis'))} Armor"
        primary_armor_rtg = str(primary_v.get("armor", 0))
        def_rating_str = f"{int(primary_v.get('body', 0)) + int(primary_v.get('armor', 0))} (Chass)"
    else:
        primary_armor_name = "None"
        primary_armor_rtg = "0"
        def_rating_str = str(bod_b)

    ranged_txt, melee_txt, primary_w_fields = _build_weapons_texts(bundle.get("weapons", []))

    armor_lines = []
    for a in armors:
        cleaned_mods = []
        for m in a.get("accessories", []):
            if not m:
                continue
            ms = _clean_pdf_text(m).strip()
            if ms.startswith("{") and ms.endswith("}") and ":" in ms:
                ms = ms.strip("{}").replace("'", "").replace('"', "")
            cleaned_mods.append(ms)
        mods = ", ".join(cleaned_mods)
        mod_s = f" [{mods}]" if mods else ""
        armor_lines.append(f"{_clean_pdf_text(a.get('name', 'Armor'))} (DR +{a.get('defense_rating', 0)}){mod_s}")
    if not armor_lines and is_ai and primary_v:
        armor_lines.append(f"{_clean_pdf_text(primary_v.get('name', 'Chassis'))} Base Armor (DR +{primary_v.get('armor', 0)})")

    aug_lines = []
    for aug in bundle.get("augmentations", []):
        g = _clean_pdf_text(aug.get("grade", "Standard"))
        rtg = f" R{aug['rating']}" if aug.get("rating") is not None else ""
        ess_c = aug.get("essence", 0)
        aug_lines.append(f"{_clean_pdf_text(aug.get('name', 'Augmentation'))}{rtg} [{g}, Ess {ess_c}]")
    if bundle.get("nanohive"):
        nh = bundle["nanohive"]
        aug_lines.append(f"Nanohive Rating {nh.get('rating', 6)} ({nh.get('max_volume', 18)} Max NV, {nh.get('replenish_rate', '')})")

    gear_lines = []
    for g in bundle.get("gear_items", []):
        g_name = _clean_pdf_text(g.get("name", "Gear"))
        qty = g.get("qty", 1)
        qty_s = f"{qty}x " if qty and int(qty) > 1 and not re.match(r"^\s*\d+\s*x\b", g_name, re.I) else ""
        rtg = g.get("rating")
        has_rtg = rtg is not None and (f"rating {rtg}" in g_name.lower() or bool(re.search(rf"\bR{rtg}\b", g_name)))
        rtg_s = f" (R{rtg})" if rtg is not None and not has_rtg else ""
        gear_lines.append(f"{qty_s}{g_name}{rtg_s}")
    for md in bundle.get("matrix_devices", []):
        gear_lines.append(f"[Commlink] {_clean_pdf_text(md.get('name', 'Device'))} (DR {md.get('rating', 3)})")
    for extra_v in vehicles[1:]:
        gear_lines.append(
            f"[Drone] {_clean_pdf_text(extra_v.get('name', 'Drone'))} "
            f"(B:{_format_val(extra_v.get('base_body'), extra_v.get('body'))} "
            f"A:{_format_val(extra_v.get('base_armor'), extra_v.get('armor'))} "
            f"P:{_format_val(extra_v.get('base_pilot'), extra_v.get('pilot'))})"
        )

    cf_spell_txt, other_abs_txt = _build_powers_and_spells_texts(bundle, raw_identity, char_data)

    licenses_str, id_row1, id_row2, id_row3 = _build_sin_license_lines(bundle.get("sins", []), nuyen_life)

    lifestyles = bundle.get("lifestyles", [])
    primary_lifestyle = _clean_pdf_text(
        f"{lifestyles[0].get('name', 'Lifestyle')} ({lifestyles[0].get('comfort', '')})".strip()
        if lifestyles else ""
    )

    asdf = bundle.get("matrix", {}).get("asdf", {})
    matrix_devs = bundle.get("matrix_devices", [])
    if bundle.get("identity", {}).get("is_ai") or bundle_attrs.get("resonance", 0) > 0:
        lp_label = f"Living Persona (MDef {bundle.get('matrix', {}).get('matrix_defense', 0)}d6)"
        if matrix_devs:
            lp_label += f" + {_clean_pdf_text(matrix_devs[0].get('name', 'Commlink'))} DR{matrix_devs[0].get('rating', '')}"
        devices_dr_str = lp_label
    elif matrix_devs:
        devices_dr_str = ", ".join(f"{_clean_pdf_text(d.get('name', 'Device'))} (DR {d.get('rating', 1)})" for d in matrix_devs[:3])
    else:
        devices_dr_str = f"MDef {bundle.get('matrix', {}).get('matrix_defense', 0)}d6"

    inv = bundle.get("inventory", {})
    all_progs = list(inv.get("programs", []) or []) + list(inv.get("autosofts", []) or [])
    prog_slots = _chunk_programs(all_progs, 4)

    ethnicity = raw_identity.get("ethnicity") or ("Emergent AI" if is_ai else raw_identity.get("heritage") or "-")
    if len(str(ethnicity)) > 26:
        ethnicity = str(ethnicity).split("(")[0].strip()[:26]

    raw_attrs = char_data.get("attributes", {}) if isinstance(char_data.get("attributes"), dict) else {}
    misc_parts = []
    if raw_identity.get("submersion"):
        misc_parts.append(f"Submersion {raw_identity['submersion']}")
    if raw_identity.get("initiation"):
        misc_parts.append(f"Init {raw_identity['initiation']}")
    pp_val = raw_identity.get("power_points") or raw_attrs.get("power_points")
    if pp_val:
        misc_parts.append(f"PP {pp_val}")
    if raw_identity.get("nanite_volume"):
        misc_parts.append(f"NV {raw_identity['nanite_volume']}")
    misc_str = ", ".join(misc_parts) or "-"

    field_map: Dict[str, str] = {
        "CHARACTER": _clean_pdf_text(display_char),
        "CHARACTER_2": _clean_pdf_text(display_char),
        "PLAYER": _clean_pdf_text(raw_identity.get("player") or "SR6 Campaign"),
        "PLAYER_2": _clean_pdf_text(raw_identity.get("player") or "SR6 Campaign"),
        "NOTES": notes_header,
        "NOTES_2": notes_header,
        "Name/Primary Alias": _clean_pdf_text(display_char),
        "Metatype": _clean_pdf_text(metatype),
        "Ethnicity": _clean_pdf_text(ethnicity),
        "Age": _clean_pdf_text(raw_identity.get("age", "-")),
        "Sex": _clean_pdf_text(identity.get("gender") or raw_identity.get("gender") or "-"),
        "Height": _clean_pdf_text(raw_identity.get("size") or raw_identity.get("height") or "-"),
        "Weight": _clean_pdf_text(raw_identity.get("weight") or "-"),
        "Reputation": _clean_pdf_text(rep_str),
        "Heat": str(heat),
        "Karma": str(karma_avail),
        "Total Karma": str(karma_life),
        "Misc": _clean_pdf_text(misc_str),
        "Body": (
            f"FW: {asdf.get('firewall', attr_dict.get('FW', {}).get('buffed', 1))}"
            if (is_ai and "BOD" not in attr_dict)
            else _attr_str("BOD", 1)
        ),
        "Agility": (
            f"DP: {asdf.get('data_processing', attr_dict.get('DP', {}).get('buffed', 1))}"
            if (is_ai and "AGI" not in attr_dict)
            else _attr_str("AGI", 1)
        ),
        "Reaction": (
            f"SLZ: {asdf.get('sleaze', attr_dict.get('SLZ', {}).get('buffed', 1))}"
            if (is_ai and "REA" not in attr_dict)
            else _attr_str("REA", 1)
        ),
        "Strength": (
            f"ATT: {asdf.get('attack', attr_dict.get('ATT', {}).get('buffed', 1))}"
            if (is_ai and "STR" not in attr_dict)
            else _attr_str("STR", 1)
        ),
        "Willpower": _attr_str("WIL", 1),
        "Logic": _attr_str("LOG", 1),
        "Intuition": _attr_str("INT", 1),
        "Charisma": _attr_str("CHA", 1),
        "Edge": _attr_str("EDG", 1),
        "Essence": _format_essence(bundle_attrs.get("essence", 6.0), is_ai),
        "MagicResonance": mag_res_str,
        "Initiative": _clean_pdf_text(phys_init_str),
        "Matrix Initiative": _clean_pdf_text(mat_init_str),
        "Astral Initiative": _clean_pdf_text(astral_init_str),
        "Composure": str(derived.get("composure", "")),
        "Judge Intentions": str(derived.get("judge_intentions", "")),
        "Memory": str(derived.get("memory", "")),
        "LiftCarry": str(derived.get("lift_carry", "")),
        "Movement": "Drone Chassis" if is_ai else "10/15/+1",
        "Defense Rating": def_rating_str,
        "Unarmed": _compute_unarmed_summary(attr_dict, bundle_attrs, char_data.get("modifiers", [])),
        "Primary Armor": primary_armor_name,
        "Rating": primary_armor_rtg,
        "Primary Ranged Weapon": primary_w_fields.get("Primary Ranged Weapon", ""),
        "Primary Ranged Stats": primary_w_fields.get("Primary Ranged Stats", ""),
        "Primary Melee Weapon": primary_w_fields.get("Primary Melee Weapon", ""),
        "Primary Melee Stats": primary_w_fields.get("Primary Melee Stats", ""),
        "Skills": _build_skills_text(bundle.get("skills", []), bundle.get("knowledge_skills", [])),
        "Qualities": _build_qualities_text(char_data.get("qualities", {})),
        "Contacts": _build_contacts_text(bundle.get("contacts", [])),
        "Primary Lifestyle": primary_lifestyle,
        "Nuyen": f"{nuyen_avail:,}\u00a5",
        "Licenses": licenses_str,
        "Fake IDs  Related Lifestyles  Funds  Licenses 1": id_row1,
        "Fake IDs  Related Lifestyles  Funds  Licenses 2": id_row2,
        "Fake IDs  Related Lifestyles  Funds  Licenses 3": id_row3,
        "Ranged Weapons": ranged_txt,
        "Melee Weapons": melee_txt,
        "Armor": "\n".join(armor_lines),
        "Augmentations": "\n".join(aug_lines),
        "Gear": "\n".join(gear_lines),
        "Spells/Preparations/Rituals/Complex Forms": cf_spell_txt,
        "Adept Powers or Other Abilities": other_abs_txt,
        "Attack": str(asdf.get("attack", "-")),
        "Sleaze": str(asdf.get("sleaze", "-")),
        "Data Proc": str(asdf.get("data_processing", "-")),
        "Firewall": str(asdf.get("firewall", "-")),
        "Devices/DR": _clean_pdf_text(devices_dr_str),
        "Programs 1": prog_slots[0],
        "Programs 2": prog_slots[1],
        "Programs 3": prog_slots[2],
        "Programs 4": prog_slots[3],
    }

    if primary_v:
        v_pools = primary_v.get("rigged_pools", {})
        abbr = {"piloting": "PLT", "gunnery": "GUN", "evasion": "EVA", "perception": "PER", "stealth": "STL"}
        pool_summary = " ".join(
            f"{abbr.get(k, k[:3].upper())}:{v_obj['pool']}d6"
            for k, v_obj in list(v_pools.items())[:4]
            if isinstance(v_obj, dict) and v_obj.get("pool") is not None
        )
        mob_short = _clean_pdf_text(primary_v.get("mobility_str") or ", ".join(primary_v.get("profile_notes", [])[:2]))
        mob_short = mob_short.replace(" (Iron-Man thrusters)", "").replace("Vector Thrust (LAV):", "LAV:")
        v_notes = " | ".join(p for p in (pool_summary, mob_short) if p)
        sensor_s = _format_val(primary_v.get("hardware_sensor", primary_v.get("base_sensor")), primary_v.get("enlightened_sensor", primary_v.get("sensor")))
        field_map.update(
            {
                "Vehicle": _clean_pdf_text(primary_v.get("name", "")),
                "Handling": _clean_pdf_text(primary_v.get("handling", "")),
                "Acceleration.0.0": _clean_pdf_text(primary_v.get("accel", "")),
                "Speed Interval": _clean_pdf_text(primary_v.get("interval", "")),
                "Top Speed": _clean_pdf_text(primary_v.get("speed", "")),
                "Vehicle Body": _format_val(primary_v.get("base_body"), primary_v.get("body")),
                "Vehicle Armor": _format_val(primary_v.get("base_armor"), primary_v.get("armor")),
                "Pilot": _format_val(primary_v.get("base_pilot"), primary_v.get("pilot")),
                "Sensor": sensor_s,
                "Seats": _clean_pdf_text(primary_v.get("seats", "-")),
                "Notes": v_notes,
            }
        )

    return field_map


def export_fillable_pdf(
    char_data: Dict[str, Any],
    char_repo_path: Optional[str] = None,
    output_path: Optional[str] = None,
    template_path: Optional[str] = None,
) -> str:
    """
    Populate Catalyst's official fillable PDF sheet for a compiled character and save to disk.

    Args:
        char_data: Loaded character dictionary (typically from `{char}_master.yaml`).
        char_repo_path: Character directory root; resolved automatically if omitted.
        output_path: Destination file path. Defaults to
            `{char_repo_path}/output/pdf/{char_id}_sheet.pdf`.
        template_path: Override path to the blank AcroForm template PDF.

    Returns:
        Absolute path to the generated fillable PDF file.
    """
    resolved_repo = _resolve_repo_path(char_data, char_repo_path)
    raw_ident = char_data.get("identity", {}) if isinstance(char_data.get("identity"), dict) else {}
    char_id = (
        raw_ident.get("id")
        or char_data.get("id")
        or (os.path.basename(resolved_repo) if resolved_repo else None)
        or str(raw_ident.get("handle", "character")).lower()
    )

    target_file = output_path
    if not target_file:
        if resolved_repo:
            target_file = os.path.join(resolved_repo, "output", "pdf", f"{char_id}_sheet.pdf")
        else:
            target_file = os.path.abspath(f"{char_id}_sheet.pdf")

    tpl_file = template_path or DEFAULT_TEMPLATE_PATH
    if not os.path.exists(tpl_file):
        raise FileNotFoundError(f"Fillable PDF template not found at '{tpl_file}'.")

    field_map = build_pdf_field_map(char_data, char_repo_path=resolved_repo)

    doc = pymupdf.open(tpl_file)
    try:
        _repair_template_fields(doc)
        for page in doc:
            for widget in page.widgets():
                fname = widget.field_name
                if fname in field_map:
                    widget.field_value = field_map[fname]
                    widget.update()
        os.makedirs(os.path.dirname(os.path.abspath(target_file)), exist_ok=True)
        doc.save(target_file)
    finally:
        doc.close()

    return os.path.abspath(target_file)
