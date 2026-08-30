"""
Mobile HTML Application Exporter for SR6 Characters.
Generates an ultra-responsive, standalone, offline-ready mobile web application (PWA)
with bottom tab navigation, multi-character switcher, high-contrast buffed pools as primary tap targets,
universal drill-down information drawers, and deep links into character Quarto rule dossiers.
"""

import json
from typing import Dict, Any, Optional

from sr6core.exporters.mobile_json import export_mobile_json


def get_mobile_html_template(character_data_bundle: Dict[str, Any], initial_char_id: str = "reiko") -> str:
    """
    Renders the complete self-contained HTML/CSS/JS mobile application.
    """
    bundle_json_str = json.dumps(character_data_bundle, indent=2, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <meta name="theme-color" content="#0b0f19">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <title>SR6 Tactical Character Dossier</title>
  <link rel="manifest" href="manifest.json">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Outfit:wght@400;500;600;700;800&family=Chakra+Petch:wght@500;600;700&display=swap" rel="stylesheet">
  
  <style>
    :root {{
      --bg-base: #080c14;
      --bg-card: rgba(16, 24, 40, 0.85);
      --bg-card-hover: rgba(24, 36, 60, 0.95);
      --bg-card-subtle: rgba(255, 255, 255, 0.03);
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-accent: rgba(99, 102, 241, 0.4);
      --gold-primary: #f59e0b;
      --gold-glow: rgba(245, 158, 11, 0.25);
      --indigo-primary: #6366f1;
      --cyan-accent: #06b6d4;
      --emerald-accent: #10b981;
      --rose-accent: #f43f5e;
      --purple-accent: #a855f7;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      --font-display: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'Fira Code', monospace;
      --nav-height: 64px;
      --safe-bottom: env(safe-area-inset-bottom, 0px);
    }}

    /* Reiko Theme (Technoshaman AI - Matrix Cyan & Electric Purple) */
    body[data-theme="reiko"], body[data-theme="yuriko"] {{
      --bg-base: #060913;
      --bg-card: rgba(11, 18, 33, 0.88);
      --bg-card-hover: rgba(18, 30, 56, 0.95);
      --border-accent: rgba(0, 240, 255, 0.45);
      --gold-primary: #00f0ff;
      --gold-glow: rgba(0, 240, 255, 0.25);
      --indigo-primary: #8b5cf6;
      --cyan-accent: #00f0ff;
      --emerald-accent: #10b981;
      --purple-accent: #a855f7;
      background-image: radial-gradient(circle at top right, rgba(0, 240, 255, 0.12), transparent 45%),
                        radial-gradient(circle at bottom left, rgba(168, 85, 247, 0.10), transparent 45%);
    }}

    /* Velvet Theme (Mystic Adept Face - Shinto Gold & Mana Pink) */
    body[data-theme="velvet"] {{
      --bg-base: #0a0614;
      --bg-card: rgba(22, 13, 38, 0.88);
      --bg-card-hover: rgba(36, 21, 61, 0.95);
      --border-accent: rgba(217, 70, 239, 0.45);
      --gold-primary: #f59e0b;
      --gold-glow: rgba(245, 158, 11, 0.3);
      --indigo-primary: #d946ef;
      --cyan-accent: #00f0ff;
      --emerald-accent: #10b981;
      --purple-accent: #c084fc;
      background-image: radial-gradient(circle at top right, rgba(217, 70, 239, 0.14), transparent 45%),
                        radial-gradient(circle at bottom left, rgba(245, 158, 11, 0.10), transparent 45%);
    }}

    /* Venn Theme (Monad Street Samurai - Nanite Emerald & Overdrive Amber) */
    body[data-theme="venn"], body[data-theme="union"] {{
      --bg-base: #040a0b;
      --bg-card: rgba(8, 20, 22, 0.88);
      --bg-card-hover: rgba(12, 34, 38, 0.95);
      --border-accent: rgba(0, 255, 157, 0.45);
      --gold-primary: #00ff9d;
      --gold-glow: rgba(0, 255, 157, 0.25);
      --indigo-primary: #ffb700;
      --cyan-accent: #06b6d4;
      --emerald-accent: #00ff9d;
      --rose-accent: #f87171;
      --purple-accent: #14b8a6;
      background-image: radial-gradient(circle at top right, rgba(0, 255, 157, 0.14), transparent 45%),
                        radial-gradient(circle at bottom left, rgba(255, 183, 0, 0.10), transparent 45%);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-tap-highlight-color: transparent;
    }}

    body {{
      background-color: var(--bg-base);
      color: var(--text-primary);
      font-family: var(--font-display);
      min-height: 100vh;
      min-height: -webkit-fill-available;
      overflow-x: hidden;
      padding-bottom: calc(var(--nav-height) + var(--safe-bottom) + 24px);
      user-select: none;
      transition: background 0.3s ease, color 0.3s ease;
    }}

    /* Top App Bar */
    header.app-bar {{
      position: sticky;
      top: 0;
      z-index: 50;
      background: rgba(8, 12, 20, 0.92);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-subtle);
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .header-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }}

    .char-select-wrap {{
      position: relative;
      flex: 1;
      max-width: 240px;
    }}

    .char-select {{
      width: 100%;
      background: var(--bg-card);
      border: 1px solid var(--border-accent);
      color: var(--gold-primary);
      font-family: var(--font-display);
      font-weight: 700;
      font-size: 1.05rem;
      padding: 6px 32px 6px 12px;
      border-radius: 10px;
      appearance: none;
      outline: none;
      cursor: pointer;
    }}

    .char-select-arrow {{
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      pointer-events: none;
      color: var(--gold-primary);
      font-size: 0.8rem;
    }}

    .header-badges {{
      display: flex;
      gap: 6px;
      align-items: center;
      flex-shrink: 0;
    }}

    .nuyen-badge {{
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.3);
      color: var(--gold-primary);
      font-family: var(--font-mono);
      font-weight: 600;
      font-size: 0.82rem;
      padding: 4px 8px;
      border-radius: 8px;
    }}

    .karma-badge {{
      background: rgba(99, 102, 241, 0.15);
      border: 1px solid rgba(99, 102, 241, 0.35);
      color: #a5b4fc;
      font-family: var(--font-mono);
      font-weight: 600;
      font-size: 0.82rem;
      padding: 4px 8px;
      border-radius: 8px;
    }}

    .search-input {{
      width: 100%;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-subtle);
      color: var(--text-primary);
      font-family: var(--font-display);
      font-size: 0.9rem;
      padding: 8px 12px;
      border-radius: 8px;
      outline: none;
      transition: border-color 0.2s;
    }}
    .search-input:focus {{
      border-color: var(--indigo-primary);
    }}

    /* Main Container */
    main.content-area {{
      padding: 16px;
      max-width: 680px;
      margin: 0 auto;
    }}

    .tab-pane {{
      display: none;
      animation: fadeIn 0.2s ease-out;
    }}
    .tab-pane.active {{
      display: block;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(4px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Card System */
    .card {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 14px;
      backdrop-filter: blur(12px);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }}

    .card-title {{
      font-size: 0.95rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-weight: 700;
      color: var(--text-muted);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    /* Attribute Grid with Interactive Drilldown */
    .attr-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
    }}

    .attr-box {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 10px 4px;
      text-align: center;
      display: flex;
      flex-direction: column;
      gap: 2px;
      cursor: pointer;
      position: relative;
      transition: all 0.15s ease;
    }}
    .attr-box:hover {{
      background: var(--bg-card-hover);
      border-color: var(--border-accent);
    }}
    .attr-box.augmented {{
      border-color: rgba(245, 158, 11, 0.5);
      background: rgba(245, 158, 11, 0.05);
    }}

    .attr-name {{
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--text-secondary);
      letter-spacing: 0.05em;
    }}

    .attr-val {{
      font-family: var(--font-mono);
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--text-primary);
    }}
    .attr-box.augmented .attr-val {{
      color: var(--gold-primary);
      text-shadow: 0 0 8px var(--gold-glow);
    }}

    .attr-sublabel {{
      font-size: 0.65rem;
      color: var(--text-muted);
      font-weight: 500;
    }}

    /* Condition Monitors */
    .track-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-top: 10px;
    }}

    .track-card {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 12px;
      text-align: center;
    }}

    .track-header {{
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }}

    .track-boxes {{
      font-family: var(--font-mono);
      font-size: 1.3rem;
      font-weight: 700;
      color: var(--cyan-accent);
    }}

    /* Derived Ratings Grid */
    .derived-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      font-size: 0.85rem;
    }}

    .derived-item {{
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 8px 10px;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .derived-item:hover {{
      border-color: var(--border-accent);
      background: var(--bg-card-hover);
    }}

    /* Pool Row Component */
    .pool-item {{
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 12px 14px;
      margin-bottom: 10px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      transition: all 0.15s ease;
    }}
    .pool-item:hover {{
      background: var(--bg-card-hover);
      border-color: var(--border-accent);
    }}

    .pool-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .skill-title-wrap {{
      display: flex;
      align-items: baseline;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .skill-name {{
      font-weight: 700;
      font-size: 1.05rem;
      color: var(--text-primary);
    }}

    .skill-spec {{
      font-size: 0.78rem;
      color: var(--gold-primary);
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.3);
      padding: 2px 6px;
      border-radius: 6px;
      font-weight: 600;
    }}

    .info-btn {{
      background: rgba(99, 102, 241, 0.15);
      border: 1px solid rgba(99, 102, 241, 0.3);
      color: #a5b4fc;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.85rem;
      cursor: pointer;
      transition: all 0.15s ease;
      flex-shrink: 0;
    }}
    .info-btn:hover {{
      background: rgba(99, 102, 241, 0.3);
      transform: scale(1.05);
    }}

    .pool-main {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .pool-target {{
      flex: 1;
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(245, 158, 11, 0.15));
      border: 1px solid var(--border-accent);
      border-radius: 10px;
      padding: 10px;
      text-align: center;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}
    .pool-target:active {{
      transform: scale(0.98);
    }}

    .pool-d6 {{
      font-family: var(--font-mono);
      font-size: 1.6rem;
      font-weight: 800;
      color: #ffffff;
      text-shadow: 0 0 12px var(--indigo-primary);
    }}

    .pool-sublabel {{
      font-size: 0.75rem;
      color: var(--text-muted);
      font-weight: 500;
    }}

    .bought-hits-box {{
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.3);
      border-radius: 10px;
      padding: 10px 14px;
      text-align: center;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .bought-hits-num {{
      font-family: var(--font-mono);
      font-size: 1.3rem;
      font-weight: 700;
      color: var(--emerald-accent);
    }}

    .bought-hits-lbl {{
      font-size: 0.7rem;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
    }}

    /* Universal Expandable Breakdown Drawer */
    .breakdown-drawer {{
      display: none;
      background: rgba(0, 0, 0, 0.45);
      border-radius: 8px;
      padding: 10px 12px;
      margin-top: 6px;
      border-left: 3px solid var(--indigo-primary);
      font-size: 0.85rem;
      animation: fadeIn 0.15s ease-out;
    }}
    .breakdown-drawer.open {{
      display: block;
    }}

    .breakdown-math {{
      font-family: var(--font-mono);
      color: #cbd5e1;
      margin-bottom: 6px;
      font-size: 0.82rem;
    }}

    .buff-checklist {{
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin-bottom: 6px;
    }}

    .buff-chip {{
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--text-secondary);
      font-size: 0.8rem;
    }}

    .doc-link-btn {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: rgba(99, 102, 241, 0.15);
      border: 1px solid rgba(99, 102, 241, 0.35);
      color: #c7d2fe;
      font-size: 0.75rem;
      font-weight: 600;
      padding: 4px 8px;
      border-radius: 6px;
      cursor: pointer;
      text-decoration: none;
      margin-top: 4px;
      transition: all 0.15s ease;
    }}
    .doc-link-btn:hover {{
      background: rgba(99, 102, 241, 0.3);
      color: #ffffff;
    }}

    /* Weapon Cards */
    .weapon-card {{
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 14px;
      margin-bottom: 12px;
      transition: all 0.15s ease;
    }}
    .weapon-card:hover {{
      border-color: var(--border-accent);
      background: var(--bg-card-hover);
    }}

    .weapon-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}

    .weapon-name {{
      font-weight: 700;
      font-size: 1.1rem;
      color: var(--text-primary);
    }}

    .weapon-dv {{
      font-family: var(--font-mono);
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--rose-accent);
      background: rgba(244, 63, 94, 0.12);
      padding: 3px 8px;
      border-radius: 6px;
    }}

    .range-bands {{
      display: flex;
      gap: 4px;
      margin: 8px 0;
    }}

    .range-band {{
      flex: 1;
      text-align: center;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      padding: 4px 2px;
      font-family: var(--font-mono);
      font-size: 0.8rem;
    }}
    .range-band .rb-lbl {{
      font-size: 0.65rem;
      color: var(--text-muted);
      display: block;
      margin-bottom: 2px;
    }}

    /* Powers & Augmentations Cards */
    .power-item {{
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 10px 12px;
      margin-bottom: 8px;
      transition: all 0.15s ease;
    }}
    .power-item:hover {{
      background: var(--bg-card-hover);
      border-color: var(--border-accent);
    }}

    .power-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .power-badge {{
      font-family: var(--font-mono);
      font-size: 0.75rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 6px;
      background: rgba(99, 102, 241, 0.15);
      border: 1px solid rgba(99, 102, 241, 0.3);
      color: #a5b4fc;
    }}

    /* Vehicle & Drone Cards */
    .vehicle-card {{
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 14px;
      margin-bottom: 12px;
    }}

    .rigged-pool-badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: rgba(99, 102, 241, 0.12);
      border: 1px solid rgba(99, 102, 241, 0.3);
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 0.8rem;
      font-family: var(--font-mono);
      color: #c7d2fe;
      margin: 2px 4px 2px 0;
    }}

    .quality-badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 600;
      margin: 2px 4px 4px 0;
    }}
    .quality-badge.pos {{
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.35);
      color: #6ee7b7;
    }}
    .quality-badge.neg {{
      background: rgba(244, 63, 94, 0.12);
      border: 1px solid rgba(244, 63, 94, 0.35);
      color: #fda4af;
    }}

    /* Contacts Directory & Filter Bar */
    .filter-bar {{
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 8px;
      margin-bottom: 12px;
    }}

    .filter-chip {{
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      font-size: 0.78rem;
      font-weight: 600;
      padding: 6px 12px;
      border-radius: 20px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
    }}
    .filter-chip.active {{
      background: var(--gold-primary);
      color: #080c14;
      border-color: var(--gold-primary);
      font-weight: 700;
    }}

    .contact-item {{
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 12px;
      margin-bottom: 8px;
      transition: all 0.15s ease;
    }}
    .contact-item:hover {{
      border-color: var(--border-accent);
      background: var(--bg-card-hover);
    }}

    .contact-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
    }}

    .favor-badge {{
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.35);
      color: var(--emerald-accent);
      font-size: 0.75rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 6px;
    }}

    .contact-group-header {{
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-weight: 700;
      color: var(--gold-primary);
      margin: 14px 0 8px 0;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    /* Bottom Navigation Bar */
    nav.bottom-nav {{
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: calc(var(--nav-height) + var(--safe-bottom));
      padding-bottom: var(--safe-bottom);
      background: rgba(8, 12, 20, 0.94);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-top: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-around;
      z-index: 100;
    }}

    .nav-tab {{
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: var(--text-muted);
      cursor: pointer;
      transition: color 0.15s ease;
      font-size: 0.72rem;
      font-weight: 600;
      gap: 4px;
    }}
    .nav-tab.active {{
      color: var(--gold-primary);
    }}
    .nav-tab-icon {{
      font-size: 1.25rem;
    }}

    /* Toast Notification */
    .toast {{
      position: fixed;
      top: 80px;
      left: 50%;
      transform: translateX(-50%) translateY(-20px);
      background: var(--bg-card);
      border: 1px solid var(--indigo-primary);
      color: var(--text-primary);
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 0.85rem;
      box-shadow: 0 8px 24px rgba(0,0,0,0.6);
      opacity: 0;
      pointer-events: none;
      transition: all 0.25s ease;
      z-index: 200;
    }}
    .toast.show {{
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }}
  </style>
</head>
<body>

  <!-- App Header -->
  <header class="app-bar">
    <div class="header-row">
      <div class="char-select-wrap">
        <select id="charSelect" class="char-select">
          <!-- Populated by JS -->
        </select>
        <div class="char-select-arrow">▼</div>
      </div>
      <div class="header-badges">
        <div id="nuyenBadge" class="nuyen-badge">¥ 0</div>
        <div id="karmaBadge" class="karma-badge">0 K</div>
      </div>
    </div>
    <input type="search" id="searchInput" class="search-input" placeholder="🔍 Search skills, weapons, powers, contacts...">
  </header>

  <!-- Main Content Area -->
  <main class="content-area">
    
    <!-- Tab 1: Core & Attributes -->
    <section id="tab-core" class="tab-pane active">
      <div class="card">
        <div class="card-title">Identity & Baseline</div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
          <div><strong id="charRealName" style="color: #cbd5e1;">Real Name</strong></div>
          <div id="charMetatype" style="color: var(--text-secondary);">Metatype</div>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px;" id="charRoleTradition">Role & Tradition</div>

        <div class="card-title" style="margin-top: 14px;">Attributes (Buffed vs Base)</div>
        <div class="attr-grid" id="attrGrid">
          <!-- Generated via JS -->
        </div>

        <div id="attrDrilldownArea" style="margin-top: 10px;"></div>

        <div class="card-title" style="margin-top: 16px;">Condition Monitors</div>
        <div class="track-grid">
          <div class="track-card">
            <div class="track-header">PHYSICAL (Base BOD)</div>
            <div class="track-boxes" id="physBoxes">10 Boxes</div>
          </div>
          <div class="track-card">
            <div class="track-header">STUN (Base WIL)</div>
            <div class="track-boxes" id="stunBoxes">11 Boxes</div>
          </div>
        </div>

        <div class="card-title" style="margin-top: 16px;">Derived Pools & Ratings</div>
        <div class="derived-grid" id="derivedGrid">
          <!-- Generated via JS -->
        </div>

        <div class="card-title" style="margin-top: 16px;">Qualities & Edge Enhancements</div>
        <div id="qualitiesList">
          <!-- Generated via JS -->
        </div>
      </div>
    </section>

    <!-- Tab 2: Skills & Dice Pools -->
    <section id="tab-skills" class="tab-pane">
      <div id="skillsList">
        <!-- Generated via JS -->
      </div>
    </section>

    <!-- Tab 3: Combat & Tactical Defense -->
    <section id="tab-combat" class="tab-pane">
      <div class="card">
        <div class="card-title">Tactical Weapon Arrays</div>
        <div id="weaponsList">
          <!-- Generated via JS -->
        </div>
      </div>

      <div class="card">
        <div class="card-title">Ballistic Armor & Defense</div>
        <div id="armorsList">
          <!-- Generated via JS -->
        </div>
      </div>
    </section>

    <!-- Tab 4: Magic / Resonance / Powers -->
    <section id="tab-powers" class="tab-pane">
      <div id="powersContent">
        <!-- Generated via JS -->
      </div>
    </section>

    <!-- Tab 5: Drones & Gear -->
    <section id="tab-drones" class="tab-pane">
      <div class="card">
        <div class="card-title">Vehicles & Rigged Drones</div>
        <div id="vehiclesList">
          <!-- Generated via JS -->
        </div>
      </div>

      <div class="card">
        <div class="card-title">Matrix Devices & Software</div>
        <div id="inventoryList">
          <!-- Generated via JS -->
        </div>
      </div>
    </section>

    <!-- Tab 6: Contacts & Network -->
    <section id="tab-contacts" class="tab-pane">
      <div class="card">
        <div class="card-title">SRM Canonical Contacts</div>
        <div class="filter-bar" id="contactFilterBar">
          <button class="filter-chip active" data-sort="all">All Contacts</button>
          <button class="filter-chip" data-sort="region">By Region</button>
          <button class="filter-chip" data-sort="type">By Archetype</button>
          <button class="filter-chip" data-sort="loyalty">Sort Loyalty</button>
          <button class="filter-chip" data-sort="connection">Sort Connection</button>
        </div>
        <div id="contactsList">
          <!-- Generated via JS -->
        </div>
      </div>
    </section>

  </main>

  <!-- Toast Element -->
  <div id="toast" class="toast">Copied pool to clipboard</div>

  <!-- Bottom Navigation -->
  <nav class="bottom-nav">
    <div class="nav-tab active" data-tab="tab-core">
      <div class="nav-tab-icon">👤</div>
      <span>Core</span>
    </div>
    <div class="nav-tab" data-tab="tab-skills">
      <div class="nav-tab-icon">⚡</div>
      <span>Skills</span>
    </div>
    <div class="nav-tab" data-tab="tab-combat">
      <div class="nav-tab-icon">🎯</div>
      <span>Combat</span>
    </div>
    <div class="nav-tab" data-tab="tab-powers">
      <div class="nav-tab-icon">🔮</div>
      <span>Powers</span>
    </div>
    <div class="nav-tab" data-tab="tab-drones">
      <div class="nav-tab-icon">🤖</div>
      <span>Drones</span>
    </div>
    <div class="nav-tab" data-tab="tab-contacts">
      <div class="nav-tab-icon">🗂️</div>
      <span>Contacts</span>
    </div>
  </nav>

  <!-- Embedded Data Payload & Script -->
  <script>
    const CHARACTERS_DATA = {bundle_json_str};
    let activeCharId = "{initial_char_id}";
    let contactFilterMode = "all";

    // Initialize DOM
    document.addEventListener("DOMContentLoaded", () => {{
      initCharacterSelector();
      setupTabs();
      setupSearch();
      setupContactFilters();
      renderActiveCharacter();
      registerServiceWorker();
    }});

    function showToast(msg) {{
      const toast = document.getElementById("toast");
      toast.textContent = msg;
      toast.classList.add("show");
      setTimeout(() => toast.classList.remove("show"), 2000);
    }}

    function getDocUrl(charId, docLink) {{
      if (!docLink) return "#";
      // Determine if running inside /output/mobile/ or master /app/
      const currentPath = window.location.pathname.replace(/\\\\/g, "/");
      if (currentPath.includes("/output/mobile/")) {{
        return `../../_book/${{docLink}}`;
      }} else {{
        return `../characters/${{charId}}/_book/${{docLink}}`;
      }}
    }}

    function initCharacterSelector() {{
      const sel = document.getElementById("charSelect");
      sel.innerHTML = "";
      Object.keys(CHARACTERS_DATA).forEach(cid => {{
        const c = CHARACTERS_DATA[cid];
        const opt = document.createElement("option");
        opt.value = cid;
        opt.textContent = c.identity.handle || cid.toUpperCase();
        if (cid === activeCharId) opt.selected = true;
        sel.appendChild(opt);
      }});

      sel.addEventListener("change", (e) => {{
        activeCharId = e.target.value;
        renderActiveCharacter();
      }});
    }}

    function setupTabs() {{
      const tabs = document.querySelectorAll(".nav-tab");
      tabs.forEach(tab => {{
        tab.addEventListener("click", () => {{
          tabs.forEach(t => t.classList.remove("active"));
          document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
          tab.classList.add("active");
          const target = tab.getAttribute("data-tab");
          document.getElementById(target).classList.add("active");
          window.scrollTo({{ top: 0, behavior: "smooth" }});
        }});
      }});
    }}

    function setupSearch() {{
      const input = document.getElementById("searchInput");
      input.addEventListener("input", (e) => {{
        const query = e.target.value.toLowerCase().trim();
        filterContent(query);
      }});
    }}

    function filterContent(query) {{
      if (!query) {{
        document.querySelectorAll(".pool-item, .weapon-card, .vehicle-card, .contact-item, .power-item, .attr-box").forEach(el => el.style.display = "");
        return;
      }}
      document.querySelectorAll(".pool-item, .weapon-card, .vehicle-card, .contact-item, .power-item, .attr-box").forEach(el => {{
        const text = el.textContent.toLowerCase();
        el.style.display = text.includes(query) ? "" : "none";
      }});
    }}

    function setupContactFilters() {{
      const chips = document.querySelectorAll("#contactFilterBar .filter-chip");
      chips.forEach(chip => {{
        chip.addEventListener("click", () => {{
          chips.forEach(c => c.classList.remove("active"));
          chip.classList.add("active");
          contactFilterMode = chip.getAttribute("data-sort");
          renderContacts();
        }});
      }});
    }}

    function renderActiveCharacter() {{
      const char = CHARACTERS_DATA[activeCharId];
      if (!char) return;

      // Apply dynamic character theme
      document.body.dataset.theme = activeCharId.toLowerCase();

      // Header Info
      document.getElementById("nuyenBadge").textContent = `¥ ${{char.identity.nuyen.toLocaleString()}}`;
      document.getElementById("karmaBadge").textContent = `${{char.identity.karma}} Karma`;
      document.getElementById("charRealName").textContent = char.identity.real_name || "Unknown";
      document.getElementById("charMetatype").textContent = char.identity.metatype || "Human";
      document.getElementById("charRoleTradition").textContent = `${{char.identity.role || "Shadowrunner"}} • ${{char.identity.stream || char.identity.tradition || char.identity.mortype || "Street Runner"}}`;

      // Attributes Grid (Using enriched attributes_list)
      const attrGrid = document.getElementById("attrGrid");
      const attrDrillArea = document.getElementById("attrDrilldownArea");
      attrGrid.innerHTML = "";
      attrDrillArea.innerHTML = "";

      const attrsList = char.attributes_list || [];
      
      attrsList.forEach((attr, idx) => {{
        const box = document.createElement("div");
        box.className = "attr-box" + (attr.is_buffed ? " augmented" : "");
        const displayVal = typeof attr.buffed === "number" ? (Number.isInteger(attr.buffed) ? attr.buffed : attr.buffed.toFixed(2)) : attr.buffed;
        const subLbl = attr.is_buffed ? `Base ${{attr.base}}` : "";

        box.innerHTML = `
          <span class="attr-name">${{attr.code}}</span>
          <span class="attr-val">${{displayVal}}</span>
          ${{subLbl ? `<span class="attr-sublabel">${{subLbl}}</span>` : ""}}
        `;

        // Drilldown toggle
        box.addEventListener("click", () => {{
          const isSelected = box.classList.contains("selected");
          document.querySelectorAll(".attr-box").forEach(b => b.classList.remove("selected"));
          
          if (isSelected) {{
            attrDrillArea.innerHTML = "";
          }} else {{
            box.classList.add("selected");
            const buffsHtml = attr.buffs && attr.buffs.length ? 
              attr.buffs.map(b => `<div class="buff-chip">✔ <strong>${{b.source}}</strong>: +${{b.value}} <span style="color: var(--text-muted);">(${{b.notes || ''}})</span></div>`).join("") :
              '<div class="buff-chip">Baseline natural attribute value</div>';

            const docLink = attr.doc_link ? `<a class="doc-link-btn" href="${{getDocUrl(activeCharId, attr.doc_link)}}" target="_blank" rel="noopener">📖 View Rules & Mechanics ↗</a>` : "";

            attrDrillArea.innerHTML = `
              <div class="breakdown-drawer open">
                <div style="font-weight: 700; color: var(--gold-primary); margin-bottom: 4px;">${{attr.name}} (${{attr.code}}): ${{attr.buffed}}</div>
                <div class="breakdown-math">📊 ${{attr.breakdown || `Base ${{attr.base}}`}}</div>
                <div class="buff-checklist">${{buffsHtml}}</div>
                ${{docLink}}
              </div>
            `;
          }}
        }});

        attrGrid.appendChild(box);
      }});

      // Condition Monitors
      document.getElementById("physBoxes").textContent = `${{char.derived.physical_boxes}} Boxes`;
      document.getElementById("stunBoxes").textContent = `${{char.derived.stun_boxes}} Boxes`;

      // Derived Ratings with Drilldown
      const dGrid = document.getElementById("derivedGrid");
      dGrid.innerHTML = `
        <div class="derived-item">
          <strong>Composure:</strong> ${{char.derived.composure}}d6 (${{Math.floor(char.derived.composure/4)}}H)
          <div style="font-size: 0.72rem; color: var(--text-muted);">WIL + CHA</div>
        </div>
        <div class="derived-item">
          <strong>Judge Int:</strong> ${{char.derived.judge_intentions}}d6 (${{Math.floor(char.derived.judge_intentions/4)}}H)
          <div style="font-size: 0.72rem; color: var(--text-muted);">WIL + INT</div>
        </div>
        <div class="derived-item">
          <strong>Memory:</strong> ${{char.derived.memory}}d6 (${{Math.floor(char.derived.memory/4)}}H)
          <div style="font-size: 0.72rem; color: var(--text-muted);">WIL + LOG</div>
        </div>
        <div class="derived-item">
          <strong>Physical Def:</strong> ${{char.derived.physical_defense}}d6 (${{Math.floor(char.derived.physical_defense/4)}}H)
          <div style="font-size: 0.72rem; color: var(--text-muted);">REA + INT</div>
        </div>
        <div class="derived-item">
          <strong>Defense Rating:</strong> ${{char.derived.defense_rating}} DR
          <div style="font-size: 0.72rem; color: var(--text-muted);">Armor + Soak</div>
        </div>
        <div class="derived-item">
          <strong>Full Matrix Def:</strong> ${{char.matrix.matrix_defense}}d6 (${{char.matrix.matrix_defense_hits}}H)
          <div style="font-size: 0.72rem; color: var(--text-muted);">${{char.matrix.matrix_defense_breakdown || 'WIL + FW'}}</div>
        </div>
      `;

      // Qualities & Edge Enhancements Rendering
      const qList = document.getElementById("qualitiesList");
      if (qList && char.qualities) {{
        qList.innerHTML = "";
        const posQ = char.qualities.positive || [];
        const negQ = char.qualities.negative || [];
        
        let qHtml = '<div style="display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 6px;">';
        posQ.forEach(q => {{
          const qName = typeof q === 'object' ? (q.name || q.ref) : q;
          const choice = (typeof q === 'object' && q.choice) ? ` (${{q.choice}})` : "";
          const rtg = (typeof q === 'object' && q.rating) ? ` R${{q.rating}}` : "";
          qHtml += `<span class="quality-badge pos">✔ ${{qName}}${{rtg}}${{choice}}</span>`;
        }});
        negQ.forEach(q => {{
          const qName = typeof q === 'object' ? (q.name || q.ref) : q;
          const choice = (typeof q === 'object' && q.choice) ? ` (${{q.choice}})` : "";
          const rtg = (typeof q === 'object' && q.rating) ? ` R${{q.rating}}` : "";
          qHtml += `<span class="quality-badge neg">✖ ${{qName}}${{rtg}}${{choice}}</span>`;
        }});
        qHtml += '</div>';

        const allQ = [...posQ, ...negQ];
        const notesQ = allQ.filter(q => typeof q === 'object' && (q.notes || q.choice));
        if (notesQ.length > 0) {{
          qHtml += '<div style="margin-top: 6px; font-size: 0.75rem; color: var(--text-secondary); line-height: 1.4;">';
          notesQ.forEach(q => {{
            qHtml += `<div>• <strong>${{q.name || q.ref}}</strong>: ${{q.notes || q.choice}}</div>`;
          }});
          qHtml += '</div>';
        }}

        qList.innerHTML = qHtml;
      }}

      // Skills Tab
      const sList = document.getElementById("skillsList");
      sList.innerHTML = "";
      char.skills.forEach(s => {{
        const item = document.createElement("div");
        item.className = "pool-item";
        
        const specHtml = s.specialization ? `<span class="skill-spec">+2 ${{s.specialization}}</span>` : "";
        const buffsHtml = s.buffs.map(b => `<div class="buff-chip">${{b.active ? '✔' : '⚡'}} ${{b.source}} (+${{b.value}})</div>`).join("");
        const docLink = s.doc_link ? `<a class="doc-link-btn" href="${{getDocUrl(activeCharId, s.doc_link)}}" target="_blank" rel="noopener">📖 View Rules & Mechanics ↗</a>` : "";

        item.innerHTML = `
          <div class="pool-top">
            <div class="skill-title-wrap">
              <span class="skill-name">${{s.name}}</span>
              ${{specHtml}}
            </div>
            <button class="info-btn" title="Inspect Breakdown">ℹ</button>
          </div>
          <div class="pool-main">
            <div class="pool-target" title="Tap to Roll">
              <span class="pool-d6">${{s.buffed_pool}}d6</span>
              <span class="pool-sublabel">Base: ${{s.base_pool}}d6 ${{s.specialization ? `| Spec: ${{s.specialized_pool}}d6` : ''}}</span>
            </div>
            <div class="bought-hits-box">
              <span class="bought-hits-num">${{s.bought_hits}}</span>
              <span class="bought-hits-lbl">Bought Hits</span>
            </div>
          </div>
          <div class="breakdown-drawer">
            <div class="breakdown-math">📊 ${{s.breakdown_text}}</div>
            ${{s.specialization ? `<div style="font-size: 0.8rem; color: var(--gold-primary); margin-bottom: 4px;"><strong>Specialized Action:</strong> ${{s.specialized_pool}}d6 (${{s.specialized_hits}} Bought Hits)</div>` : ''}}
            <div class="buff-checklist">
              ${{buffsHtml || '<div class="buff-chip">No active buffs</div>'}}
            </div>
            ${{docLink}}
          </div>
        `;

        // Click target to copy/toast
        item.querySelector(".pool-target").addEventListener("click", () => {{
          showToast(`⚡ ${{s.name}}: ${{s.buffed_pool}}d6 (${{s.bought_hits}} Hits)${{s.specialization ? ` [${{s.specialization}}: ${{s.specialized_pool}}d6]` : ''}}`);
        }});

        // Toggle Breakdown Drawer
        item.querySelector(".info-btn").addEventListener("click", () => {{
          const drawer = item.querySelector(".breakdown-drawer");
          drawer.classList.toggle("open");
        }});

        sList.appendChild(item);
      }});

      // Weapons Tab
      const wList = document.getElementById("weaponsList");
      wList.innerHTML = "";
      if (char.weapons.length === 0) {{
        wList.innerHTML = "<div style='color: var(--text-muted);'>No tactical weapons listed.</div>";
      }} else {{
        char.weapons.forEach(w => {{
          const wCard = document.createElement("div");
          wCard.className = "weapon-card";
          const arBands = Array.isArray(w.attack_rating) ? w.attack_rating : [10, 10, 8, 0, 0];
          const labels = ["C", "N", "M", "F", "E"];
          const arHtml = labels.map((lbl, idx) => `
            <div class="range-band">
              <span class="rb-lbl">${{lbl}}</span>
              <span>${{arBands[idx] > 0 ? arBands[idx] : "—"}}</span>
            </div>
          `).join("");

          const docLink = w.doc_link ? `<a class="doc-link-btn" href="${{getDocUrl(activeCharId, w.doc_link)}}" target="_blank" rel="noopener">📖 View Weapon Protocols ↗</a>` : "";

          // Melee weapons omit fire mode and ammo
          const modeAmmoHtml = w.is_melee ? 
            `<div style="font-size: 0.8rem; color: var(--gold-primary); margin-bottom: 4px;">⚔️ <strong>Physical Melee Weapon</strong> (No fire mode / ammo)</div>` :
            `<div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px;">
              Modes: <strong>${{w.modes_str}}</strong> | Ammo: <strong>${{w.ammo}}</strong> ${{w.loaded_ammo ? `(${{w.loaded_ammo}})` : ""}}
            </div>`;

          wCard.innerHTML = `
            <div class="weapon-header">
              <span class="weapon-name">${{w.name}}</span>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span class="weapon-dv">${{w.damage}}</span>
                <button class="info-btn" title="Weapon Breakdown">ℹ</button>
              </div>
            </div>
            ${{modeAmmoHtml}}
            <div class="range-bands">${{arHtml}}</div>
            ${{w.accessories.length ? `<div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">Mods: ${{w.accessories.join(", ")}}</div>` : ""}}
            ${{w.notes ? `<div style="font-size: 0.75rem; color: var(--gold-primary); margin-top: 4px;">${{w.notes}}</div>` : ""}}
            <div class="breakdown-drawer">
              <div class="breakdown-math">📊 Base Stats: ${{w.base_damage}} | AR: ${{w.base_attack_rating_str}} ${{w.is_melee ? '' : `| Modes: ${{w.base_modes_str}} | Cap: ${{w.base_ammo}}`}}</div>
              ${{w.accessories.length ? `<div class="buff-checklist">${{w.accessories.map(a => `<div class="buff-chip">✔ ${{a}}</div>`).join("")}}</div>` : '<div class="buff-chip">Unmodified chassis</div>'}}
              ${{docLink}}
            </div>
          `;

          wCard.querySelector(".info-btn").addEventListener("click", () => {{
            const drawer = wCard.querySelector(".breakdown-drawer");
            drawer.classList.toggle("open");
          }});

          wList.appendChild(wCard);
        }});
      }}

      // Armor Tab
      const aList = document.getElementById("armorsList");
      aList.innerHTML = "";
      char.armors.forEach(a => {{
        const div = document.createElement("div");
        div.style.marginBottom = "8px";
        div.innerHTML = `<strong>${{a.name}}</strong> (+${{a.defense_rating}} DR) ${{a.modifications.length ? `— <em>${{a.modifications.join(", ")}}</em>` : ""}}`;
        aList.appendChild(div);
      }});

      // Powers Tab with Drilldowns and Doc Links
      const pContent = document.getElementById("powersContent");
      pContent.innerHTML = "";
      
      const cf = char.powers.complex_forms || [];
      const spPowers = char.powers.sprite_powers || [];
      const spells = char.powers.spells || [];
      const adept = char.powers.adept_powers || [];
      const echoes = char.powers.echoes || [];
      const monad = char.powers.monad_abilities || [];
      const augs = char.powers.augmentations || [];

      if (cf.length > 0) {{
        let cfItems = cf.map(c => `
          <div class="power-item">
            <div class="power-header">
              <strong>${{c.name}}</strong>
              <span class="power-badge">FV: ${{c.fading}} | ${{c.duration}}</span>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px;">Target: ${{c.target}}</div>
            ${{c.notes ? `<div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">${{c.notes}}</div>` : ""}}
            ${{c.doc_link ? `<a class="doc-link-btn" href="${{getDocUrl(activeCharId, c.doc_link)}}" target="_blank" rel="noopener">📖 View Complex Form Rules ↗</a>` : ""}}
          </div>
        `).join("");

        pContent.innerHTML += `
          <div class="card">
            <div class="card-title">Complex Forms & Resonance</div>
            ${{cfItems}}
            ${{echoes.length ? `<div style="margin-top: 10px; font-size: 0.85rem; color: var(--gold-primary);"><strong>Submersion Echoes:</strong> ${{echoes.map(e => typeof e === 'object' ? e.name : e).join(", ")}}</div>` : ""}}
          </div>
        `;
      }}

      if (spPowers.length > 0) {{
        let spItems = spPowers.map(sp => `
          <div class="power-item">
            <div class="power-header">
              <strong style="color: var(--cyan-accent);">${{sp.name}}</strong>
              <span class="power-badge">${{sp.action}}</span>
            </div>
            <div style="font-size: 0.8rem; color: var(--gold-primary); margin-top: 2px;">Target: ${{sp.target}}</div>
            <div style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 4px;">${{sp.effect}}</div>
            ${{sp.doc_link ? `<a class="doc-link-btn" href="${{getDocUrl(activeCharId, sp.doc_link)}}" target="_blank" rel="noopener">📖 View Symbiosis Rules ↗</a>` : ""}}
          </div>
        `).join("");

        pContent.innerHTML += `
          <div class="card">
            <div class="card-title">⚡ Sprite Symbiosis Powers (Taz)</div>
            ${{spItems}}
          </div>
        `;
      }}

      if (spells.length > 0 || adept.length > 0) {{
        let spellItems = spells.map(s => `
          <div class="power-item">
            <div class="power-header">
              <strong>${{s.name}}</strong>
              <span class="power-badge">Drain: ${{s.drain}} | ${{s.duration}}</span>
            </div>
            ${{s.notes ? `<div style="font-size: 0.78rem; color: var(--gold-primary); margin-top: 4px;">${{s.notes}}</div>` : ""}}
            ${{s.doc_link ? `<a class="doc-link-btn" href="${{getDocUrl(activeCharId, s.doc_link)}}" target="_blank" rel="noopener">📖 View Spellcasting Rules ↗</a>` : ""}}
          </div>
        `).join("");

        let adeptItems = adept.map(a => `
          <div class="power-item">
            <div class="power-header">
              <strong>${{a.name}}</strong>
              <span class="power-badge">Cost: ${{a.cost}} PP</span>
            </div>
            ${{a.notes ? `<div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">${{a.notes}}</div>` : ""}}
            ${{a.doc_link ? `<a class="doc-link-btn" href="${{getDocUrl(activeCharId, a.doc_link)}}" target="_blank" rel="noopener">📖 View Power Rules ↗</a>` : ""}}
          </div>
        `).join("");

        pContent.innerHTML += `
          <div class="card">
            <div class="card-title">Spells & Adept Powers</div>
            ${{spellItems}}
            ${{adeptItems}}
          </div>
        `;
      }}

      if (monad.length > 0) {{
        let monadItems = monad.map(m => `
          <div class="power-item">
            <div class="power-header">
              <strong style="color: var(--cyan-accent);">${{m.name}}</strong>
            </div>
            <div style="color: var(--text-secondary); font-size: 0.82rem; margin-top: 4px;">${{m.effect}}</div>
            ${{m.doc_link ? `<a class="doc-link-btn" href="${{getDocUrl(activeCharId, m.doc_link)}}" target="_blank" rel="noopener">📖 View Monad Protocols ↗</a>` : ""}}
          </div>
        `).join("");

        pContent.innerHTML += `
          <div class="card">
            <div class="card-title">Monad Swarm Abilities</div>
            ${{monadItems}}
          </div>
        `;
      }}

      if (augs.length > 0) {{
        let augItems = augs.map(a => `
          <div class="power-item">
            <div class="power-header">
              <strong>${{a.name}} ${{a.rating ? `R${{a.rating}}` : ""}}</strong>
              <span class="power-badge">[${{a.grade}}] ${{a.essence ? `${{a.essence}} Ess` : ''}}</span>
            </div>
            ${{a.notes ? `<div style="font-size: 0.78rem; color: var(--gold-primary); margin-top: 4px;">${{a.notes}}</div>` : ""}}
            ${{a.doc_link ? `<a class="doc-link-btn" href="${{getDocUrl(activeCharId, a.doc_link)}}" target="_blank" rel="noopener">📖 View Augmentation Rules ↗</a>` : ""}}
          </div>
        `).join("");

        pContent.innerHTML += `
          <div class="card">
            <div class="card-title">Cyberware & Bioware Augmentations</div>
            ${{augItems}}
          </div>
        `;
      }}

      // Vehicles & Drones Tab
      const vList = document.getElementById("vehiclesList");
      vList.innerHTML = "";
      if (char.vehicles.length === 0) {{
        vList.innerHTML = "<div style='color: var(--text-muted);'>No vehicles or drones deployed.</div>";
      }} else {{
        char.vehicles.forEach(v => {{
          const vCard = document.createElement("div");
          vCard.className = "vehicle-card";
          
          let poolsHtml = "";
          if (v.rigged_pools) {{
            Object.keys(v.rigged_pools).forEach(pk => {{
              const p = v.rigged_pools[pk];
              poolsHtml += `<span class="rigged-pool-badge">${{pk.toUpperCase()}}: ${{p.pool}}d6 (${{p.hits}}H)</span>`;
            }});
          }}

          const docLink = v.doc_link ? `<a class="doc-link-btn" href="${{getDocUrl(activeCharId, v.doc_link)}}" target="_blank" rel="noopener">📖 View Drone Statblocks ↗</a>` : "";

          vCard.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;">
              <strong style="font-size: 1.05rem;">${{v.name}}</strong>
              <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 0.8rem; color: var(--gold-primary);">${{v.role || ""}}</span>
                <button class="info-btn" title="Drone Specs">ℹ</button>
              </div>
            </div>
            <div style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px;">
              HAN: ${{v.handling}} | ACC: ${{v.accel}} | SPD: ${{v.speed}} | BOD: ${{v.body}} | ARM: ${{v.armor}} | PIL: ${{v.pilot}} | SEN: ${{v.sensor}}
            </div>
            ${{v.mobility_str ? `<div style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--gold-primary); margin-bottom: 6px;">⚙️ ${{v.mobility_str}}</div>` : ""}}
            ${{poolsHtml ? `<div style="margin: 6px 0;">${{poolsHtml}}</div>` : ""}}
            ${{v.modifications.length ? `<div style="font-size: 0.75rem; color: var(--text-muted);">Mods: ${{v.modifications.join(", ")}}</div>` : ""}}
            <div class="breakdown-drawer">
              <div class="breakdown-math">📊 Base Stats: Base BOD ${{v.base_body || v.body}} | Base ARM ${{v.base_armor || v.armor}} | Base PIL ${{v.base_pilot || v.pilot}} | Base SEN ${{v.base_sensor || v.sensor}}</div>
              ${{v.profile_notes && v.profile_notes.length ? `<div style="font-size: 0.75rem; color: var(--gold-primary); margin-bottom: 4px;"><strong>Active Enhancements:</strong> ${{v.profile_notes.join(" • ")}}</div>` : ""}}
              ${{v.modifications.length ? `<div class="buff-checklist">${{v.modifications.map(m => `<div class="buff-chip">✔ ${{m}}</div>`).join("")}}</div>` : '<div class="buff-chip">Standard factory chassis</div>'}}
              ${{docLink}}
            </div>
          `;

          vCard.querySelector(".info-btn").addEventListener("click", () => {{
            const drawer = vCard.querySelector(".breakdown-drawer");
            drawer.classList.toggle("open");
          }});

          vList.appendChild(vCard);
        }});
      }}

      // Inventory & Software Tab
      const iList = document.getElementById("inventoryList");
      const progs = char.inventory.programs || [];
      const autos = char.inventory.autosofts || [];
      const gear = char.inventory.gear || [];
      iList.innerHTML = `
        <div style="margin-bottom: 8px;"><strong>Programs:</strong> <span style="color: var(--text-secondary); font-size: 0.85rem;">${{progs.join(", ") || "None"}}</span></div>
        <div style="margin-bottom: 8px;"><strong>Autosofts:</strong> <span style="color: var(--text-secondary); font-size: 0.85rem;">${{autos.join(", ") || "None"}}</span></div>
        <div><strong>Field Gear:</strong> <span style="color: var(--text-secondary); font-size: 0.85rem;">${{gear.join(", ") || "Standard runner kit"}}</span></div>
      `;

      // Contacts Tab
      renderContacts();
    }}

    function renderContacts() {{
      const char = CHARACTERS_DATA[activeCharId];
      if (!char) return;

      const cList = document.getElementById("contactsList");
      cList.innerHTML = "";
      const rawContacts = [...(char.contacts || [])];

      if (rawContacts.length === 0) {{
        cList.innerHTML = "<div style='color: var(--text-muted);'>No recorded contacts.</div>";
        return;
      }}

      let sorted = rawContacts;

      if (contactFilterMode === "loyalty") {{
        sorted.sort((a, b) => (b.loyalty || 0) - (a.loyalty || 0));
      }} else if (contactFilterMode === "connection") {{
        sorted.sort((a, b) => (b.connection || 0) - (a.connection || 0));
      }} else if (contactFilterMode === "region") {{
        // Group by region
        const groups = {{}};
        sorted.forEach(c => {{
          const reg = c.region || "Seattle / Global";
          if (!groups[reg]) groups[reg] = [];
          groups[reg].push(c);
        }});

        Object.keys(groups).sort().forEach(reg => {{
          const header = document.createElement("div");
          header.className = "contact-group-header";
          header.innerHTML = `📍 ${{reg}} (${{groups[reg].length}})`;
          cList.appendChild(header);

          groups[reg].forEach(c => {{
            cList.appendChild(createContactElement(c));
          }});
        }});
        return;
      }} else if (contactFilterMode === "type") {{
        // Group by type / archetype
        const groups = {{}};
        sorted.forEach(c => {{
          const arch = c.archetype || "Contact";
          if (!groups[arch]) groups[arch] = [];
          groups[arch].push(c);
        }});

        Object.keys(groups).sort().forEach(arch => {{
          const header = document.createElement("div");
          header.className = "contact-group-header";
          header.innerHTML = `👥 ${{arch}} (${{groups[arch].length}})`;
          cList.appendChild(header);

          groups[arch].forEach(c => {{
            cList.appendChild(createContactElement(c));
          }});
        }});
        return;
      }}

      // Default rendering
      sorted.forEach(c => {{
        cList.appendChild(createContactElement(c));
      }});
    }}

    function createContactElement(c) {{
      const cItem = document.createElement("div");
      cItem.className = "contact-item";
      cItem.innerHTML = `
        <div class="contact-header">
          <strong style="color: var(--text-primary); font-size: 1.02rem;">${{c.name}} (${{c.archetype}})</strong>
          ${{c.favors ? `<span class="favor-badge">+${{c.favors}} Favor</span>` : ""}}
        </div>
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px;">
          Connection: <strong>${{c.connection}}</strong> | Loyalty: <strong>${{c.loyalty}}</strong> ${{c.region ? `| 📍 ${{c.region}}` : ""}}
        </div>
        ${{c.description ? `<div style="font-size: 0.75rem; color: var(--text-muted);">${{c.description}}</div>` : ""}}
      `;
      return cItem;
    }}

    function registerServiceWorker() {{
      if ('serviceWorker' in navigator) {{
        navigator.serviceWorker.register('sw.js').catch(err => console.log('SW registration error', err));
      }}
    }}
  </script>
</body>
</html>
"""


def export_mobile_html(char_data: Dict[str, Any], char_id: str = "reiko", char_repo_path: Optional[str] = None) -> str:
    """
    Exports a standalone single-character mobile HTML application.
    """
    char_json = export_mobile_json(char_data, char_repo_path=char_repo_path)
    bundle = {char_id: char_json}
    return get_mobile_html_template(bundle, initial_char_id=char_id)
