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
