"""
Web Importer & HTML-to-Markdown Atomizer for Shadowrun Sixth World FAQs.
Fetches https://shadowrunsixthworld.com/shadowrun-sixth-world-faq/, normalizes content,
saves to converted_md, and atomizes into shadowrun_rules_vault as Authority Level 2 documents.
"""

import os
import re
import yaml
import urllib.request
from typing import Dict, Any, List, Optional, Tuple

DEFAULT_FAQ_URL = "https://shadowrunsixthworld.com/shadowrun-sixth-world-faq/"

HTML_ENTITIES = {
    "&#8211;": "–",
    "&#8212;": "—",
    "&#8216;": "'",
    "&#8217;": "'",
    "&#8220;": '"',
    "&#8221;": '"',
    "&#038;": "&",
    "&nbsp;": " ",
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&quot;": '"',
    "\xa0": " ",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "–",
    "\u2014": "—",
    "\u2026": "..."
}


def clean_html_entities(text: str) -> str:
    """Replaces common HTML and encoding artifacts with standard characters."""
    for k, v in HTML_ENTITIES.items():
        text = text.replace(k, v)
    return text


def fetch_faq_html(url: str = DEFAULT_FAQ_URL, fallback_cache: Optional[str] = None) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SR6-Core-RAG-Bot/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw_bytes = resp.read()
            return raw_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        if fallback_cache and os.path.exists(fallback_cache):
            with open(fallback_cache, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        raise RuntimeError(f"Failed fetching FAQ from {url}: {e}")


def parse_faq_html(html: str) -> List[Dict[str, Any]]:
    html = clean_html_entities(html)

    # Find where the actual Q&A starts (after the Table of Contents)
    # The first question has id="Tir-Tairngire" in an h2 tag
    first_h2_q = html.find('id="Tir-Tairngire"')
    if first_h2_q != -1:
        first_chap_idx = html.rfind('<h2 class="wp-block-heading">', 0, first_h2_q)
        if first_chap_idx != -1:
            body_html = html[first_chap_idx:]
        else:
            body_html = html[first_h2_q:]
    else:
        body_html = html

    h2_pattern = re.compile(r'<h2([^>]*)>(.*?)</h2>', re.DOTALL | re.IGNORECASE)
    matches = list(h2_pattern.finditer(body_html))

    parsed_items = []
    current_chapter = "General"

    for i, match in enumerate(matches):
        attrs_str = match.group(1)
        inner_html = match.group(2)
        header_text = re.sub(r'<[^>]+>', '', inner_html).strip()

        is_question = "has-medium-font-size" in attrs_str or 'id="' in attrs_str
        id_m = re.search(r'id=["\']([^"\']+)["\']', attrs_str)
        anchor = id_m.group(1) if id_m else ""

        if not is_question and not anchor:
            if header_text and header_text not in ["Shadowrun, Sixth World FAQs", "Shadowrun, Sixth World FAQ"]:
                current_chapter = header_text
        else:
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(body_html)
            section_html = body_html[start_pos:end_pos]

            section_clean = re.sub(r'\[\s*<a[^>]*>top</a>\s*\]', '', section_html, flags=re.IGNORECASE)
            section_clean = re.sub(r'\[\s*top\s*\]', '', section_clean, flags=re.IGNORECASE)

            p_items = []
            blocks = re.findall(r'<(p|li|ol|ul)[^>]*>(.*?)</\1>', section_clean, re.DOTALL | re.IGNORECASE)
            if blocks:
                for tag, b_content in blocks:
                    text = re.sub(r'<[^>]+>', '', b_content).strip()
                    if text and text != "[top]":
                        if tag == "li":
                            p_items.append(f"- {text}")
                        else:
                            p_items.append(text)
            else:
                raw = re.sub(r'<[^>]+>', ' ', section_clean).strip()
                if raw and raw != "[top]":
                    p_items.append(raw)

            parsed_items.append({
                "chapter": current_chapter,
                "question": header_text,
                "anchor": anchor,
                "answers": p_items
            })

    return parsed_items


def import_web_faq(
    url: str = DEFAULT_FAQ_URL,
    converted_dir: Optional[str] = None,
    vault_dir: Optional[str] = None,
    html_source: Optional[str] = None
) -> Tuple[int, str, str]:
    """
    Ingests official web FAQ, generates converted_md/Shadowrun_Sixth_World_FAQ.md,
    and atomizes all Q&As into shadowrun_rules_vault/SSWFAQ-*.md (Authority Level 2).
    """
    from sr6core.rules_db import DEFAULT_CONVERTED_DIR, DEFAULT_VAULT_DIR
    from sr6core.vault.atomizer import get_tags

    out_converted = converted_dir or DEFAULT_CONVERTED_DIR
    out_vault = vault_dir or DEFAULT_VAULT_DIR

    os.makedirs(out_converted, exist_ok=True)
    os.makedirs(out_vault, exist_ok=True)

    if html_source and os.path.exists(html_source):
        with open(html_source, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
    else:
        html = fetch_faq_html(url)

    questions = parse_faq_html(html)
    if not questions:
        raise ValueError("Failed to extract any FAQ questions from HTML source.")

    # 1. Generate full converted markdown file
    md_lines = [
        "# Shadowrun Sixth World FAQ\n",
        "Official Rules FAQ and Clarifications from ShadowrunSixthWorld.com (Catalyst Game Labs).\n"
    ]

    current_ch = ""
    for q in questions:
        if q["chapter"] != current_ch:
            current_ch = q["chapter"]
            md_lines.append(f"\n## {current_ch}\n")
        md_lines.append(f"### {q['question']}")
        for ans in q["answers"]:
            md_lines.append(f"\n{ans}")
        md_lines.append("")

    full_md_path = os.path.join(out_converted, "Shadowrun_Sixth_World_FAQ.md")
    with open(full_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    # 2. Generate atomic rule files (SSWFAQ-0001 through SSWFAQ-0155)
    pad_len = max(4, len(str(len(questions))))
    atomized_count = 0

    for idx, q in enumerate(questions, 1):
        rule_id = f"SSWFAQ-{idx:0{pad_len}d}"
        chapter = q["chapter"] or "General"
        topic = q["question"]
        page_ref = q["anchor"] or f"q-{idx}"

        answer_text = "\n\n".join(q["answers"])
        body_content = f"### {chapter}: {topic}\n\n{answer_text}".strip()
        tags = get_tags(f"{chapter} {topic} {body_content}")
        if "missions" not in tags:
            tags.append("missions")

        frontmatter = {
            "id": rule_id,
            "source": "Shadowrun Sixth World FAQ",
            "chapter": chapter,
            "topic": topic,
            "page": page_ref,
            "authority_level": 2,
            "tags": tags,
            "status": "active",
            "overrides": []
        }

        chunk_path = os.path.join(out_vault, f"{rule_id}.md")
        with open(chunk_path, "w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.dump(frontmatter, f, default_flow_style=False, sort_keys=False)
            f.write("---\n\n")
            f.write(body_content)
            f.write("\n")

        atomized_count += 1

    return atomized_count, full_md_path, out_vault
