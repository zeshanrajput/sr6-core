import pytest
from sr6core.rules_engine import get_multi_modifier_interactions, render_multi_modifier_interactions

def test_multi_modifier_interactions_venn():
    interactions = get_multi_modifier_interactions("venn", threshold=2)
    assert len(interactions) >= 4, f"Expected at least 4 multi-modifier pools for Venn, got {len(interactions)}"

    names = [i["name"] for i in interactions]
    assert any("Close Combat" in n for n in names)
    assert any("Cracking" in n for n in names)
    assert any("Firewall" in n for n in names)
    assert any("Damage Resistance" in n or "Soak" in n for n in names)

    # Check Close Combat pool details
    cc = next(i for i in interactions if "Close Combat" in i["name"])
    assert cc["count"] >= 3
    mod_sources = [m["source"] for m in cc["modifiers"]]
    assert any("Skillwires" in s for s in mod_sources)
    assert any("Neural Pattern" in s for s in mod_sources)
    assert any("Neuromuscular" in s for s in mod_sources)
    assert any("Bone Density" in s for s in mod_sources)

    # Verify Markdown rendering
    rendered = render_multi_modifier_interactions("venn", threshold=2)
    assert "⚡" in rendered
    assert "Automated Multi-Modifier Audit" in rendered
    assert "Close Combat" in rendered
    assert "Stacking Legality" in rendered
    assert "Operational Constraints" in rendered

def test_multi_modifier_interactions_threshold():
    # If threshold is very high (e.g. 10), no pools should be returned
    empty_interactions = get_multi_modifier_interactions("venn", threshold=10)
    assert len(empty_interactions) == 0

    rendered_empty = render_multi_modifier_interactions("venn", threshold=10)
    assert "No pools currently exceed" in rendered_empty

def test_multi_modifier_interactions_velvet():
    interactions = get_multi_modifier_interactions("velvet", threshold=2)
    assert len(interactions) >= 6, f"Expected at least 6 multi-modifier pools for Velvet, got {len(interactions)}"

    names = [i["name"] for i in interactions]
    assert any("Spellcasting" in n for n in names)
    assert any("Channeling" in n for n in names)
    assert any("Drain Resistance" in n for n in names)
    assert any("Leadership" in n for n in names)
    assert any("Social Negotiation" in n for n in names)
    assert any("Deception" in n for n in names)

    # Spellcasting should reflect Power Focus (+3) and Specialization (+2) -> 16d6
    sc = next(i for i in interactions if "Spellcasting" in i["name"])
    assert "16d6" in sc["total_pool"]
    sc_sources = [m["source"] for m in sc["modifiers"]]
    assert any("Power Focus" in s for s in sc_sources)
    assert any("Specialization" in s for s in sc_sources)

    # Channeling should reflect Power Focus (+3) and Initiate Grade (+2) -> 17d6
    ch = next(i for i in interactions if "Channeling" in i["name"])
    assert "17d6" in ch["total_pool"]
    ch_sources = [m["source"] for m in ch["modifiers"]]
    assert any("Power Focus" in s for s in ch_sources)
    assert any("Initiate Grade" in s for s in ch_sources)

    # Drain Resistance should reflect Sustained Spells -> 23d6
    dr = next(i for i in interactions if "Drain Resistance" in i["name"])
    assert "23d6" in dr["total_pool"]

    # Influence (Leadership) should reflect Sustained Charisma (+4) and Command Presence (+2) -> 21d6
    lead = next(i for i in interactions if "Leadership" in i["name"])
    assert "21d6" in lead["total_pool"]
    assert "+1 Edge" in lead["total_pool"]

    # Social Negotiation should reflect Sustained Charisma (+4) -> 19d6 (Social Rating 18)
    sn = next(i for i in interactions if "Social Negotiation" in i["name"])
    assert "19d6" in sn["total_pool"]
    assert "Social Rating 18" in sn["total_pool"]

    # Deception & Fast-Talk should reflect Sustained Charisma (+4) -> 18d6 (-1 Edge Cost)
    con = next(i for i in interactions if "Deception" in i["name"])
    assert "18d6" in con["total_pool"]

    # Verify Markdown rendering
    rendered = render_multi_modifier_interactions("velvet", threshold=2)
    assert "⚡" in rendered
    assert "Spellcasting (Sorcery)" in rendered
    assert "Power Focus" in rendered
    assert "16d6" in rendered
    assert "Spirit Channeling" in rendered
    assert "17d6" in rendered
    assert "Influence (Leadership)" in rendered
    assert "21d6" in rendered
    assert "Social Negotiation" in rendered
    assert "19d6" in rendered
    assert "Deception & Fast-Talk" in rendered
    assert "18d6" in rendered


def test_multi_modifier_interactions_reiko():
    interactions = get_multi_modifier_interactions("reiko", threshold=2)
    assert len(interactions) >= 3, f"Expected at least 3 multi-modifier pools for Reiko, got {len(interactions)}"

    names = [i["name"] for i in interactions]
    assert any("Cracking" in n for n in names)
    assert any("Electronics" in n for n in names)
    assert any("ASDF" in n or "Resonance" in n for n in names)

    # Check Cracking pool details (21d6 with Resonance Focus, Taz Symbiosis, Specialization)
    cr = next(i for i in interactions if "Cracking" in i["name"])
    assert "21d6" in cr["total_pool"]
    rf_mod = next(m for m in cr["modifiers"] if "Resonance Focus" in m["source"])
    assert rf_mod["value"] == 4
    assert rf_mod["type"] == "focus"
    assert "rules_matrix.html#foci" in rf_mod["rule_anchor"]

    # Check Electronics pool details (21d6)
    el = next(i for i in interactions if "Electronics" in i["name"])
    assert "21d6" in el["total_pool"]
    el_sources = [m["source"] for m in el["modifiers"]]
    assert any("Resonance Focus" in s for s in el_sources)

    # Verify Markdown rendering
    rendered = render_multi_modifier_interactions("reiko", threshold=2)
    assert "⚡" in rendered
    assert "Automated Multi-Modifier Audit" in rendered
    assert "Cracking" in rendered
    assert "Resonance Focus" in rendered
    assert "21d6" in rendered


