"""
Campaign Roadmap & Missions Visualizer for Quarto Character Books.
Renders responsive HTML dashboards illustrating:
- Total career mission progress and career runway KPIs.
- Core Campaigns (Seattle 2081, New Orleans 2083).
- Individual Convention Mission Packs (CMPs: Blood Diamonds, Kentucky Fried Shadows, etc.).
- Prime Missions and Special Holiday runs.
- Detailed historical run telemetry (date, GM, payouts) and available mission briefings.
"""

import html
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from sr6core.character.manager import CharacterManager
from sr6core.character.mission_registry import get_mission_record, CANONICAL_MISSIONS
from sr6core.character.mission_match import (
    get_available_missions,
    calculate_runway,
    parse_character_missions_log,
    _get_character_log_path,
)

CORE_CAMPAIGNS = ["Seattle 2081", "New Orleans 2083"]
CMP_PACKS = [
    "Neo-Tokyo Twilight",
    "Blood Diamonds",
    "Big Easy Blues",
    "Kentucky Fried Shadows 2",
    "Bad Blood",
    "The Price of Flesh",
    "K-Pocalypse",
    "Denver War",
]


def render_campaign_roadmap(char_id: str) -> str:
    """
    Generates a Quarto-compatible HTML dashboard showing campaign and mission pack progress.
    """
    cm = CharacterManager()
    all_chars = cm.discover_characters()
    if char_id not in all_chars:
        return f"<div class='alert alert-warning'>Character '{html.escape(char_id)}' not found in portfolio.</div>"

    cinfo = all_chars[char_id]
    name = cinfo.get("name", char_id)
    avail = get_available_missions(char_id)
    runway = calculate_runway(char_id)

    log_path = _get_character_log_path(cinfo)
    runs_by_code: Dict[str, Dict[str, Any]] = {}
    if log_path:
        log_data = parse_character_missions_log(log_path)
        for m in log_data["missions"]:
            runs_by_code[m["norm_code"]] = m

    # Overall progress
    total_missions = avail["total_missions"]
    played_count = avail["played_count"]
    pct = avail["completion_pct"]

    # HTML builder
    h = []
    h.append("<div class='campaign-roadmap-container my-4'>")

    # 1. Macro Telemetry Banner
    h.append(f"""
    <div class='card mb-4' style='background: #0b0e14; border: 1px solid #1e293b; border-top: 3px solid #00f0ff; box-shadow: 0 4px 20px rgba(0, 240, 255, 0.08);'>
      <div class='card-body p-4'>
        <div class='row align-items-center mb-3'>
          <div class='col-md-7'>
            <h3 class='m-0' style='color: #00f0ff; font-family: "Orbitron", monospace; letter-spacing: 0.05em;'>
              CAMPAIGN ROADMAP // {html.escape(name.upper())}
            </h3>
            <p class='text-muted small mb-0 mt-1'>
              Sanctioned Shadowrun Missions (SRM) Organized Play Portfolio Tracker • 2081 & 2083 Arcs
            </p>
          </div>
          <div class='col-md-5 text-md-end mt-3 mt-md-0'>
            <span class='badge' style='background: rgba(0, 240, 255, 0.15); color: #00f0ff; border: 1px solid #00f0ff; font-size: 0.95rem; padding: 0.5rem 0.8rem;'>
              {played_count} / {total_missions} MISSIONS COMPLETED ({pct}%)
            </span>
          </div>
        </div>

        <div class='progress mb-4' style='height: 12px; background-color: #1e293b; border-radius: 6px; overflow: hidden;'>
          <div class='progress-bar' role='progressbar' style='width: {pct}%; background: linear-gradient(90deg, #00f0ff, #38bdf8);' aria-valuenow='{pct}' aria-valuemin='0' aria-valuemax='100'></div>
        </div>

        <div class='row g-3 text-center'>
          <div class='col-6 col-lg-3'>
            <div class='p-3 rounded' style='background: rgba(255,255,255,0.02); border: 1px solid #1e293b;'>
              <div class='text-muted small'>REMAINING RUNWAY</div>
              <div class='h4 m-0 mt-1' style='color: #ffb700; font-family: "Share Tech Mono", monospace;'>
                {runway['remaining_missions']} Missions
              </div>
              <div class='small text-muted mt-1'>{runway['remaining_srms']} SRMs • {runway['remaining_cmps']} CMPs • {runway['remaining_pms']} PM</div>
            </div>
          </div>
          <div class='col-6 col-lg-3'>
            <div class='p-3 rounded' style='background: rgba(255,255,255,0.02); border: 1px solid #1e293b;'>
              <div class='text-muted small'>PROJECTED KARMA</div>
              <div class='h4 m-0 mt-1' style='color: #00f0ff; font-family: "Share Tech Mono", monospace;'>
                ~{runway['projected_karma']['expected_veteran']} Karma
              </div>
              <div class='small text-muted mt-1'>{runway['projected_karma']['conservative']} base – {runway['projected_karma']['max_with_work_for_people']} max</div>
            </div>
          </div>
          <div class='col-6 col-lg-3'>
            <div class='p-3 rounded' style='background: rgba(255,255,255,0.02); border: 1px solid #1e293b;'>
              <div class='text-muted small'>PROJECTED NET NUYEN</div>
              <div class='h4 m-0 mt-1' style='color: #10b981; font-family: "Share Tech Mono", monospace;'>
                ¥{runway['projected_nuyen']['net_veteran']:,}
              </div>
              <div class='small text-muted mt-1'>After -¥{runway['projected_nuyen']['rent_drag']:,} rent drag</div>
            </div>
          </div>
          <div class='col-6 col-lg-3'>
            <div class='p-3 rounded' style='background: rgba(255,255,255,0.02); border: 1px solid #1e293b;'>
              <div class='text-muted small'>MECHANICAL PIPELINE</div>
              <div class='h4 m-0 mt-1' style='color: {"#00f0ff" if runway["mechanical_plan"]["achievable"] else "#f87171"}; font-family: "Share Tech Mono", monospace;'>
                {runway['mechanical_plan']['total_karma_queued']} Karma
              </div>
              <div class='small text-muted mt-1'>{"Consumes " + str(runway["mechanical_plan"]["runway_consumption_pct"]) + "% runway" if runway["mechanical_plan"]["achievable"] else "Exceeds runway"}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    """)

    # Helper to render an arc card
    def _render_arc_card(arc_name: str, m_list: List[Dict[str, Any]], border_color: str = "#00f0ff") -> str:
        played = [m for m in m_list if m["played"]]
        p_count = len(played)
        t_count = len(m_list)
        arc_pct = round((p_count / t_count) * 100, 1) if t_count else 0

        badge_color = "#00f0ff" if arc_pct == 100 else ("#ffb700" if arc_pct > 0 else "#64748b")
        badge_bg = f"rgba({0 if arc_pct==100 else (255 if arc_pct>0 else 100)}, {240 if arc_pct==100 else (183 if arc_pct>0 else 116)}, {255 if arc_pct==100 else 0}, 0.12)"
        status_label = "100% COMPLETE" if arc_pct == 100 else (f"{p_count}/{t_count} IN PROGRESS" if arc_pct > 0 else "AVAILABLE")

        card_html = []
        card_html.append(f"""
        <div class='col-12 mb-4'>
          <div class='card h-100' style='background: #0b0e14; border: 1px solid #1e293b; border-left: 4px solid {border_color};'>
            <div class='card-header d-flex justify-content-between align-items-center py-3' style='background: rgba(255,255,255,0.015); border-bottom: 1px solid #1e293b;'>
              <div>
                <h5 class='m-0' style='color: #e2e8f0; font-family: "Orbitron", monospace; letter-spacing: 0.04em;'>
                  {html.escape(arc_name.upper())}
                </h5>
                <span class='small text-muted'>{t_count} Missions in Campaign</span>
              </div>
              <span class='badge' style='background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_color}; font-size: 0.85rem; padding: 0.35rem 0.65rem;'>
                {status_label} ({arc_pct}%)
              </span>
            </div>
            <div class='card-body p-3'>
              <div class='progress mb-3' style='height: 6px; background-color: #1e293b; border-radius: 3px;'>
                <div class='progress-bar' style='width: {arc_pct}%; background-color: {badge_color};'></div>
              </div>
              <div class='row g-2'>
        """)

        for m in m_list:
            mid = m["id"]
            code = m["code"]
            title = m["title"]
            is_played = m["played"]
            run_info = runs_by_code.get(mid)
            full_rec = get_mission_record(mid) or {}
            synopsis = full_rec.get("synopsis", "")
            fpath = full_rec.get("file_path", "")

            if is_played:
                card_style = "border-left: 3px solid #00f0ff; background: rgba(0, 240, 255, 0.04);"
                badge_html = f"<span class='badge' style='background: rgba(0,240,255,0.2); color: #00f0ff;'>✓ PLAYED</span>"
                details_text = ""
                if run_info:
                    r_date = run_info.get("date") or "Logged"
                    r_k = run_info.get("karma", 0)
                    r_n = run_info.get("nuyen", 0)
                    r_gm = f" • GM: {html.escape(run_info['gm'])}" if run_info.get("gm") else ""
                    details_text = f"<div class='small text-muted mt-1'>{r_date} • +{r_k} Karma • +¥{r_n:,}{r_gm}</div>"
            else:
                card_style = "border-left: 3px solid #334155; background: rgba(255, 255, 255, 0.015); opacity: 0.85;"
                badge_html = f"<span class='badge' style='background: rgba(100,116,139,0.2); color: #94a3b8;'>AVAILABLE</span>"
                details_text = "<div class='small text-muted mt-1'>Unplayed • Open for Registration</div>"

            syn_html = ""
            if synopsis:
                syn_snip = html.escape(synopsis[:220].strip()) + ("..." if len(synopsis) > 220 else "")
                syn_html = f"""
                <details class='mt-2'>
                  <summary class='small text-info' style='cursor: pointer;'>Briefing / Hook Preview</summary>
                  <p class='small text-muted mt-1 mb-0' style='font-style: italic;'>{syn_snip}</p>
                </details>
                """

            card_html.append(f"""
            <div class='col-md-6 col-lg-4 mb-2'>
              <div class='p-2 rounded h-100 d-flex flex-column justify-content-between' style='{card_style} border: 1px solid #1e293b;'>
                <div>
                  <div class='d-flex justify-content-between align-items-center'>
                    <span class='small fw-bold' style='color: #00f0ff; font-family: "Share Tech Mono", monospace;'>{html.escape(code)}</span>
                    {badge_html}
                  </div>
                  <div class='fw-semibold text-truncate mt-1' title='{html.escape(title)}' style='color: #e2e8f0; font-size: 0.95rem;'>
                    {html.escape(title)}
                  </div>
                  {details_text}
                </div>
                {syn_html}
              </div>
            </div>
            """)

        card_html.append("""
              </div>
            </div>
          </div>
        </div>
        """)
        return "".join(card_html)

    # 2. SECTION 1: Core Campaigns (Seattle 2081 & New Orleans 2083)
    h.append("""
    <div class='mt-4 mb-3 d-flex align-items-center'>
      <h4 class='m-0' style='color: #ffb700; font-family: "Orbitron", monospace; letter-spacing: 0.05em;'>
        01 // CORE SANCTIONED CAMPAIGNS
      </h4>
      <div class='ms-3 flex-grow-1' style='height: 1px; background: rgba(255, 183, 0, 0.2);'></div>
    </div>
    <div class='row'>
    """)

    for cname in CORE_CAMPAIGNS:
        if cname in avail["arcs"]:
            # Seattle 2081 core is 24 SRMs, NOLA is 20 SRMs (filter out CMPs/specials for this card if any)
            srm_missions = [m for m in avail["arcs"][cname] if m["type"] == "SRM"]
            border = "#00f0ff" if cname == "Seattle 2081" else "#a855f7"
            h.append(_render_arc_card(f"{cname} Core Story Arc", srm_missions, border_color=border))

    h.append("</div>")

    # 3. SECTION 2: Convention Mission Packs (CMPs)
    h.append("""
    <div class='mt-4 mb-3 d-flex align-items-center'>
      <h4 class='m-0' style='color: #ffb700; font-family: "Orbitron", monospace; letter-spacing: 0.05em;'>
        02 // THEMED CONVENTION MISSION PACKS (CMPs)
      </h4>
      <div class='ms-3 flex-grow-1' style='height: 1px; background: rgba(255, 183, 0, 0.2);'></div>
    </div>
    <div class='row'>
    """)

    for p_name in CMP_PACKS:
        if p_name in avail["arcs"]:
            h.append(_render_arc_card(p_name, avail["arcs"][p_name], border_color="#38bdf8"))

    h.append("</div>")

    # 4. SECTION 3: Prime Missions & Special Events
    h.append("""
    <div class='mt-4 mb-3 d-flex align-items-center'>
      <h4 class='m-0' style='color: #ffb700; font-family: "Orbitron", monospace; letter-spacing: 0.05em;'>
        03 // PRIME MISSIONS & SPECIAL OPERATIONS
      </h4>
      <div class='ms-3 flex-grow-1' style='height: 1px; background: rgba(255, 183, 0, 0.2);'></div>
    </div>
    <div class='row'>
    """)

    # Collect Prime Missions & Specials across arcs
    special_missions = []
    for arc_name, m_list in avail["arcs"].items():
        for m in m_list:
            if m["type"] in ["PM", "SMH", "Special"] or "Prime" in m.get("arc", ""):
                special_missions.append(m)

    if special_missions:
        h.append(_render_arc_card("Prime Missions & Holiday Operations", special_missions, border_color="#ec4899"))

    h.append("</div>")
    h.append("</div>") # End container

    return "".join(h)

