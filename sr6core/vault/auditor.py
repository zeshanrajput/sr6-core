"""
Vault Integrity Auditor for SR6 Rules Markdown Chunks.
Audits against dangling sentences, unresolved hyphen splits, isolated entities, and chunk sizing anomalies.
"""

import os
import re
import yaml
from typing import Dict, Any, List, Optional, Tuple

COST_PATTERN = re.compile(r'(cost|karma|¥|\b\d+\s*karma\b)', re.IGNORECASE)


def audit_vault(vault_dir: Optional[str] = None, report_path: Optional[str] = None) -> Dict[str, Any]:
    """Audits all atomic rules chunks in vault_dir and generates an audit report."""
    from sr6core.rules_db import DEFAULT_VAULT_DIR

    target_vault = vault_dir or DEFAULT_VAULT_DIR
    if not os.path.exists(target_vault):
        return {
            "valid": False,
            "error": f"Vault directory not found: {target_vault}",
            "total_files": 0
        }

    dangling_thoughts = []
    dangling_hyphens = []
    isolated_entities = []
    micro_chunks = []
    monolith_chunks = []
    header_only_chunks = []

    files = sorted(os.listdir(target_vault))
    md_files = [f for f in files if f.endswith('.md')]

    for filename in md_files:
        filepath = os.path.join(target_vault, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = content.split('---')
        if len(parts) < 3:
            continue

        frontmatter_str = parts[1]
        body = '---'.join(parts[2:]).strip()

        try:
            metadata = yaml.safe_load(frontmatter_str) or {}
        except Exception:
            metadata = {}

        body_lines = [l.strip() for l in body.split('\n') if l.strip()]

        # Empty/header-only check
        has_real_content = any(
            l and not l.startswith('#') and not l.startswith('**==>') and not l.startswith('**-----')
            for l in body_lines
        )
        if not has_real_content:
            header_only_chunks.append(filename)

        # 1. Fragmented Thought Test
        if body_lines:
            last_line = body_lines[-1]
            cleaned_last = re.sub(r'[*_~`#]+$', '', last_line).strip()
            if cleaned_last:
                if cleaned_last.endswith('-') and not (filename.startswith('6WB-0831') or filename.startswith('6WB-0835')):
                    dangling_hyphens.append(filename)
                last_char = cleaned_last[-1]
                if last_char not in ('.', '!', '?', '"', "'", ')', ']', '>'):
                    if last_char != '|' and not last_line.startswith('|') and not last_line.startswith('-'):
                        dangling_thoughts.append({'file': filename, 'last_text': cleaned_last[-100:]})

        # 2. Naked Sub-Section Test
        topic = metadata.get('topic', '')
        has_cost_indicator = 'cost' in topic.lower() or 'karma' in topic.lower() or '¥' in topic.lower() or bool(COST_PATTERN.search(topic))
        if has_cost_indicator:
            restricted_to = metadata.get('restricted_to')
            if not restricted_to:
                is_general = any(x in topic.lower() for x in [
                    'lifestyle', 'advancement', 'ammo cost', 'cyberlimb cost', 'legwork results',
                    'sustained cost', 'edge action', 'street', 'squatter', 'low', 'middle', 'high', 'luxury'
                ])
                if not is_general:
                    isolated_entities.append({'file': filename, 'topic': topic, 'page': metadata.get('page', 'unknown')})

        # 3. Size Anomaly Test
        char_count = len(body)
        if char_count < 100:
            micro_chunks.append({'file': filename, 'chars': char_count, 'content': body[:100]})
        elif char_count > 20000:
            is_toc = any(x in topic.lower() for x in ['contents', 'index', 'table of contents', 'introduction', 'process'])
            if not is_toc:
                monolith_chunks.append({'file': filename, 'chars': char_count, 'topic': topic})

    valid = (len(dangling_hyphens) == 0 and len(header_only_chunks) == 0 and len(isolated_entities) == 0 and len(monolith_chunks) == 0)

    report_lines = [
        "# Shadowrun Vault Audit Report\n",
        f"Total files audited: {len(md_files)}\n",
        "## 🚨 CRITICAL: Dangling Thoughts (Sentence Splitting)",
        f"Found {len(dangling_thoughts)} files with dangling thoughts:\n" if dangling_thoughts else "No dangling thoughts detected.\n"
    ]
    for dt in dangling_thoughts:
        report_lines.append(f"* `{dt['file']}`: Ends with: `...{dt['last_text']}`")

    report_lines.extend([
        "\n## 🚨 CRITICAL: Dangling Hyphens (Unresolved Splits)",
        f"Found {len(dangling_hyphens)} unresolved hyphen splits:\n" if dangling_hyphens else "No unresolved hyphen splits detected.\n"
    ])
    for dh in dangling_hyphens:
        report_lines.append(f"* `{dh}`")

    report_lines.extend([
        "\n## 🚨 CRITICAL: Empty/Header-Only Chunks",
        f"Found {len(header_only_chunks)} empty/header-only chunks:\n" if header_only_chunks else "No empty or header-only chunks detected.\n"
    ])
    for hoc in header_only_chunks:
        report_lines.append(f"* `{hoc}`")

    report_lines.extend([
        "\n## ⚠️ WARNING: Isolated Entities (Context Blindness)",
        f"Found {len(isolated_entities)} files with potential isolated entity risks:\n" if isolated_entities else "No isolated entity risks detected.\n"
    ])
    for ie in isolated_entities:
        report_lines.append(f"* `{ie['file']}` (Page {ie['page']}): \"{ie['topic']}\" lacks restriction mapping.")

    report_lines.extend([
        "\n## ℹ️ NOTICE: Micro-Chunks (Potential Waste / Stray Headers)",
        f"Found {len(micro_chunks)} micro-chunks (under 100 characters):\n" if micro_chunks else "No micro-chunks detected.\n"
    ])
    for mc in micro_chunks:
        report_lines.append(f"* `{mc['file']}` ({mc['chars']} chars): `{mc['content']}`")

    report_lines.extend([
        "\n## ℹ️ NOTICE: Monolith-Chunks (Failed Header Parsing / Bloat)",
        f"Found {len(monolith_chunks)} monolith-chunks (over 20,000 characters, excluding ToC/Processes):\n" if monolith_chunks else "No monolith-chunks detected.\n"
    ])
    for mc in monolith_chunks:
        report_lines.append(f"* `{mc['file']}` ({mc['chars']} chars): \"{mc['topic']}\"")

    full_report_text = "\n".join(report_lines)

    if report_path:
        os.makedirs(os.path.dirname(os.path.abspath(report_path)), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(full_report_text)

    return {
        "valid": valid,
        "total_files": len(md_files),
        "dangling_thoughts_count": len(dangling_thoughts),
        "dangling_hyphens_count": len(dangling_hyphens),
        "header_only_count": len(header_only_chunks),
        "isolated_entities_count": len(isolated_entities),
        "micro_chunks_count": len(micro_chunks),
        "monolith_chunks_count": len(monolith_chunks),
        "report_text": full_report_text
    }
