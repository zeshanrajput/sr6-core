"""
Rules Atomization Engine for Shadowrun 6th Edition.
Splits converted markdown rulebooks and FAQs into atomic, frontmatter-enriched rules vault entries.
"""

import os
import re
import yaml
import shutil
from typing import Dict, Any, List, Optional, Tuple

FILE_MAP = {
    '391504-Missions_SR6_Guide_v2_4.md': {'abbrev': 'SRMG', 'level': 1, 'name': 'Shadowrun Missions Guide v2.4'},
    'SR6-Core-Rulebook-Errata-Feb-2020.md': {'abbrev': 'ERRATA', 'level': 1, 'name': 'Shadowrun Sixth World Errata (Feb 2020)'},
    'Shadowrun_Sixth_World_FAQ.md': {'abbrev': 'SSWFAQ', 'level': 2, 'name': 'Shadowrun Sixth World FAQ'},
    'CAT26062S_Adversary.md': {'abbrev': 'ADV', 'level': 2, 'name': 'Adversary'},
    'E-CAT27002S_Krime Katalog.md': {'abbrev': 'KK', 'level': 2, 'name': 'Krime Katalog'},
    'CAT27453_No Future 6E.md': {'abbrev': 'NF', 'level': 2, 'name': 'No Future 6E'},
    'CAT28002_Firing Squad.md': {'abbrev': 'FS', 'level': 2, 'name': 'Firing Squad'},
    'CAT28003_Street Wyrd.md': {'abbrev': 'SW', 'level': 2, 'name': 'Street Wyrd'},
    'CAT28004_Double Clutch.md': {'abbrev': 'DC', 'level': 2, 'name': 'Double Clutch'},
    'CAT28005_Sixth_World_Companion.md': {'abbrev': '6WC', 'level': 2, 'name': 'Sixth World Companion'},
    'CAT28006_Hack_and_Slash.md': {'abbrev': 'HnS', 'level': 2, 'name': 'Hack and Slash'},
    'CAT28007_Body_Shop.md': {'abbrev': 'BS', 'level': 2, 'name': 'Body Shop'},
    'CAT28008_Wild_Life.md': {'abbrev': 'WL', 'level': 2, 'name': 'Wild Life'},
    'CAT28009_Smooth_Operations.md': {'abbrev': 'SO', 'level': 2, 'name': 'Smooth Operations'},
    'CAT28011_Shadowrun_Deadly_Arts.md': {'abbrev': 'DA', 'level': 2, 'name': 'Deadly Arts'},
    'CAT28100_Emerald_City.md': {'abbrev': 'EC', 'level': 2, 'name': 'Emerald City'},
    'CAT28101_Astral_Ways.md': {'abbrev': 'AW', 'level': 2, 'name': 'Astral Ways'},
    'CAT28301_Slip Streams.md': {'abbrev': 'SS', 'level': 2, 'name': 'Slip Streams'},
    'CAT28302_The Kechibi Code.md': {'abbrev': 'KC', 'level': 2, 'name': 'The Kechibi Code'},
    'CAT28303_Scotophobia.md': {'abbrev': 'SP', 'level': 2, 'name': 'Scotophobia'},
    'CAT28305_Lethal_Harvest.md': {'abbrev': 'LH', 'level': 2, 'name': 'Lethal Harvest'},
    'CAT28404_Whisper_Nets.md': {'abbrev': 'WN', 'level': 2, 'name': 'Whisper Nets'},
    'CAT28450_Collapsing Now.md': {'abbrev': 'CN', 'level': 2, 'name': 'Collapsing Now'},
    'CAT28451_Power Plays.md': {'abbrev': 'PP', 'level': 2, 'name': 'Power Plays'},
    'CAT28452_Null_Value.md': {'abbrev': 'NV', 'level': 2, 'name': 'Null Value'},
    'CAT28453_Falling_Point.md': {'abbrev': 'FP', 'level': 2, 'name': 'Falling Point'},
    'CAT28455_Asphalt Jungles.md': {'abbrev': 'AJ', 'level': 2, 'name': 'Asphalt Jungles'},
    'Shadowrun_6e_Catalyst_Game_Labs_Risks_&_Rewards_CAT28454OEF2025.md': {'abbrev': 'RR', 'level': 2, 'name': 'Risks and Rewards'},
    'Shadowrun_6e_Catalyst_Game_labs_Desert_Wars_01_Para_Bellum_E_CAT28807SOEF2026.md': {'abbrev': 'DW1', 'level': 2, 'name': 'Desert Wars 1: Para Bellum'},
    'SR6E - Desert Wars 02 Cry Havoc.md': {'abbrev': 'DW2', 'level': 2, 'name': 'Desert Wars 2: Cry Havoc'},
    'SHadowrun 6E - Margin Calls.md': {'abbrev': 'MC', 'level': 2, 'name': 'Margin Calls'},
    'Shadowrun - Seoul Survivor (Republic of Korea Data Download).md': {'abbrev': 'SEOUL', 'level': 2, 'name': 'Seoul Survivor'},
    'CAT28510_Shadow_Cast.md': {'abbrev': 'SC', 'level': 2, 'name': 'Shadow Cast'},
    'CAT28513_Shoot_Straight.md': {'abbrev': 'SSt', 'level': 2, 'name': 'Shoot Straight'},
    'CAT28516_Tarnished_Star.md': {'abbrev': 'TS', 'level': 2, 'name': 'Tarnished Star'},
    'E-CAT28800S_Lifestyles_of_the_Shadowy_and_Infamous.md': {'abbrev': 'LSI', 'level': 2, 'name': 'Lifestyles of the Shadowy and Infamous'},
    'E-CAT28801S_Bestial_Nature.md': {'abbrev': 'BN', 'level': 2, 'name': 'Bestial Nature'},
    'E-CAT28802S_Easy_Come_Easy_Go.md': {'abbrev': 'ECEG', 'level': 2, 'name': 'Easy Come Easy Go'},
    'E-CAT28803S_That_Old_Voodoo.md': {'abbrev': 'TOV', 'level': 2, 'name': 'That Old Voodoo'},
    'E-CAT28805S_Dealers_of_Death.md': {'abbrev': 'DD', 'level': 2, 'name': 'Dealers of Death'},
    'E-CAT28840S_Age of Rust.md': {'abbrev': 'AR', 'level': 2, 'name': 'Age of Rust'},
    'E-CAT28880S_Lofwyrs_Legions.md': {'abbrev': 'LL', 'level': 2, 'name': 'Lofwyr\'s Legions'},
    'E-CAT28881S_Ingentis Athletes.md': {'abbrev': 'IA', 'level': 2, 'name': 'Ingentis Athletes'},
    'CAT28000B_SR6 Berlin Edition.md': {'abbrev': '6WB', 'level': 3, 'name': 'Berlin Edition'},
    'CAT28000S_SR6 Core City Edition Seattle.md': {'abbrev': '6WS', 'level': 3, 'name': 'City Edition: Seattle'},
    'Shadowrun_CGL_Sixth_Edition_Shadowrun_Sixth_World_Core_Rulebook.md': {'abbrev': 'SR6H', 'level': 3, 'name': 'City Edition: Hong Kong'},
    'Shadowrun_CGL_Sixth_Edition_Québec_The_Northern_Lily_OEF,_2026_06.md': {'abbrev': 'QNL', 'level': 2, 'name': 'Québec: The Northern Lily'},
    '6we Matrix FAQ.md': {'abbrev': 'MFAQ', 'level': 4, 'name': '6we Matrix FAQ'},
    'Shadowrun Missions Gamemaster Primer.md': {'abbrev': 'GMP', 'level': 4, 'name': 'Shadowrun Missions Gamemaster Primer'},
    'SR6-Character-Conversion-Guide-v1.md': {'abbrev': 'CCG', 'level': 4, 'name': 'Character Conversion Guide v1'},
    'Final Edit - Character Conversion Guide.md': {'abbrev': 'CCG2', 'level': 4, 'name': 'Character Conversion Guide (Final Edit)'}
}

TAG_RULES = {
    'Matrix': re.compile(r'\b(matrix|cybercombat|cyberdeck|persona|cyberjack|commlink|rcc|overwatch|pan|host|ic|technomancer|resonance|sprite|data\s+spike|asdf)\b', re.IGNORECASE),
    'Magic': re.compile(r'\b(magic|spell|sorcery|adept|power\s+point|mana|drain|reagent|ritual|initiation|astral|projection|perceive|spirit|enchanting|focus|alchemy|potency|conjuring)\b', re.IGNORECASE),
    'Rigging': re.compile(r'\b(rigger|rcc|rigging|drone|vehicle|pilot|jumped-in|control\s+rig|handling|speed\s+interval|chase|sensor|autosoft)\b', re.IGNORECASE),
    'Combat': re.compile(r'\b(combat|attack|defense|damage|edge|initiative|weapon|armor|wound|stun|physical\s+damage|major\s+action|minor\s+action|melee|firearms|range|ammo|grenade|recoil|cover)\b', re.IGNORECASE),
    'Qualities': re.compile(r'\b(quality|qualities|exceptional|attribute|karma|nuyen|debt|bribe|lifestyle|archetype)\b', re.IGNORECASE),
    'Adept Powers': re.compile(r'\b(adept\s+power|adept\s+powers|power\s+point|power\s+points|improved\s+reflexes|critical\s+strike|mystic\s+adept)\b', re.IGNORECASE),
    'Cyberware': re.compile(r'\b(cyberware|bioware|augmentation|augmentations|dermal|bone\s+lacing|wired\s+reflexes|synaptic\s+booster|cyberlimb|cybereye|datajack)\b', re.IGNORECASE),
    'Gear': re.compile(r'\b(gear|nuyen|commlink|deck|taser|pistol|rifle|shotgun|grenade|medkit|biotech|software|autosoft|focus)\b', re.IGNORECASE),
    'Missions': re.compile(r'\b(srm|missions|gamemaster|campaign|faq|guide|primer|season|reputation|heat)\b', re.IGNORECASE),
    'Critters': re.compile(r'\b(critter|critters|spirit|howl|nature|wild\s+life|beast|animal)\b', re.IGNORECASE),
    'Toxins': re.compile(r'\b(toxin|toxins|poison|gas|tear\s+gas|antidote|drug|drugs|nausea)\b', re.IGNORECASE),
    'Character Creation': re.compile(r'\b(priority\s+table|character\s+creation|karma|attributes|skill\s+points|customize)\b', re.IGNORECASE)
}

CATEGORY_RESTRICTIONS = {
    'positive virtual life form qualities': 'virtual-life-forms',
    'negative virtual life form qualities': 'virtual-life-forms',
    'inherent virtual life form qualities': 'virtual-life-forms',
    'adept powers': 'adepts',
    'resonant streams': 'technomancers',
    'new technomancer qualities': 'technomancers'
}


def clean_header(text: str) -> str:
    text = re.sub(r'[*_~`#]', '', text)
    return text.strip()


def get_tags(content: str) -> List[str]:
    tags = []
    for tag, pattern in TAG_RULES.items():
        if pattern.search(content):
            tags.append(tag.lower().replace(" ", "-"))
    return tags


def chunk_has_content(chunk_lines: List[str]) -> bool:
    for line in chunk_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('**==>') and not stripped.startswith('**-----'):
            return True
    return False


def is_header_footer_artifact(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith('|'):
        return False
    if re.match(r'^\d+$', stripped):
        return True
    if '//' in stripped and '://' not in stripped:
        cleaned = re.sub(r'[^a-zA-Z]', '', stripped)
        if not cleaned or cleaned.isupper():
            return True
    if stripped.lower() == "shadowrun missions guide":
        return True
    return False


def is_valid_header(text: str) -> bool:
    if len(text) > 120:
        return False
    if '<br>' in text or '-----' in text or 'picture' in text.lower() or 'start of' in text.lower() or 'end of' in text.lower():
        return False
    return True


def chunk_markdown(content: str) -> List[Dict[str, Any]]:
    lines = content.split('\n')
    chunks = []
    current_h1 = ""
    current_h2 = ""
    current_h3 = ""
    current_page = 1
    current_chunk = {'h1': "", 'h2': "", 'h3': "", 'start_page': 1, 'lines': []}

    for line in lines:
        stripped = line.strip()
        page_match = re.search(r'^\s*(\d+)\s*$', stripped)
        if page_match:
            val = int(page_match.group(1))
            if 0 < val < 2000:
                current_page = val + 1

        h1_match = re.match(r'^#\s+(.+)$', line)
        h2_match = re.match(r'^##\s+(.+)$', line)
        h3_match = re.match(r'^###\s+(.+)$', line)

        is_sub_section = False
        if h2_match and clean_header(h2_match.group(1)).lower() in ('advantages', 'disadvantages'):
            is_sub_section = True
        elif h3_match and clean_header(h3_match.group(1)).lower() in ('advantages', 'disadvantages'):
            is_sub_section = True

        if h1_match and is_valid_header(h1_match.group(1)):
            h1_text = clean_header(h1_match.group(1))
            if not chunk_has_content(current_chunk['lines']):
                current_h1 = f"{current_h1} - {h1_text}" if current_h1 else h1_text
                current_chunk['h1'] = current_h1
                current_chunk['lines'].append(line)
            else:
                chunks.append(current_chunk)
                current_h1 = h1_text
                current_h2 = ""
                current_h3 = ""
                current_chunk = {'h1': current_h1, 'h2': current_h2, 'h3': current_h3, 'start_page': current_page, 'lines': [line]}
        elif h2_match and not is_sub_section and is_valid_header(h2_match.group(1)):
            h2_text = clean_header(h2_match.group(1))
            if not chunk_has_content(current_chunk['lines']):
                current_h2 = f"{current_h2} - {h2_text}" if current_h2 else h2_text
                current_chunk['h2'] = current_h2
                current_chunk['lines'].append(line)
            else:
                chunks.append(current_chunk)
                current_h2 = h2_text
                current_h3 = ""
                current_chunk = {'h1': current_h1, 'h2': current_h2, 'h3': current_h3, 'start_page': current_page, 'lines': [line]}
        elif h3_match and not is_sub_section and is_valid_header(h3_match.group(1)):
            h3_text = clean_header(h3_match.group(1))
            if not chunk_has_content(current_chunk['lines']):
                current_h3 = f"{current_h3} - {h3_text}" if current_h3 else h3_text
                current_chunk['h3'] = current_h3
                current_chunk['lines'].append(line)
            else:
                chunks.append(current_chunk)
                current_h3 = h3_text
                current_chunk = {'h1': current_h1, 'h2': current_h2, 'h3': current_h3, 'start_page': current_page, 'lines': [line]}
        else:
            current_chunk['lines'].append(line)

    if any(l.strip() for l in current_chunk['lines']):
        chunks.append(current_chunk)

    return chunks


def stitch_interrupted_chunks(chunks: List[Dict[str, Any]]):
    for i in range(1, len(chunks)):
        prev_chunk = chunks[i-1]
        curr_chunk = chunks[i]
        if not prev_chunk['lines'] or not curr_chunk['lines']:
            continue
        prev_last_line = ""
        for line in reversed(prev_chunk['lines']):
            if line.strip():
                prev_last_line = line.strip()
                break
        cleaned_prev_last = re.sub(r'[*_~`#]+$', '', prev_last_line).strip()
        ends_abruptly = bool(cleaned_prev_last and cleaned_prev_last[-1] not in ('.', '!', '?', '"', "'", ')'))
        if ends_abruptly:
            paragraphs = []
            current_para = []
            for line in curr_chunk['lines']:
                if line.strip().startswith('#'):
                    if current_para:
                        paragraphs.append(current_para)
                        current_para = []
                    paragraphs.append([line])
                elif not line.strip():
                    if current_para:
                        paragraphs.append(current_para)
                        current_para = []
                else:
                    current_para.append(line)
            if current_para:
                paragraphs.append(current_para)

            if len(paragraphs) > 2:
                last_para = paragraphs[-1]
                first_text_line = ""
                for line in last_para:
                    if line.strip():
                        first_text_line = line.strip()
                        break
                cleaned_first_text = re.sub(r'^[*_~`#]+', '', first_text_line).strip()
                if cleaned_first_text and cleaned_first_text[0].islower():
                    curr_lines = curr_chunk['lines']
                    last_para_set = set(last_para)
                    split_idx = -1
                    for idx, line in enumerate(curr_lines):
                        if line in last_para_set:
                            split_idx = idx
                            break
                    if split_idx != -1:
                        para_lines = curr_lines[split_idx:]
                        curr_chunk['lines'] = curr_lines[:split_idx]
                        prev_chunk['lines'].append("")
                        prev_chunk['lines'].extend(para_lines)


def normalize_topic(topic: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '', topic or '').lower()


def aggregate_entities(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not chunks:
        return []
    aggregated = []
    current_chunk = chunks[0]
    for next_chunk in chunks[1:]:
        topic_curr = current_chunk['h3'] or current_chunk['h2'] or current_chunk['h1']
        topic_next = next_chunk['h3'] or next_chunk['h2'] or next_chunk['h1']
        norm_curr = normalize_topic(topic_curr)
        norm_next = normalize_topic(topic_next)
        if norm_curr and norm_next and norm_curr == norm_next:
            current_chunk['lines'].append("")
            current_chunk['lines'].extend(next_chunk['lines'])
        else:
            aggregated.append(current_chunk)
            current_chunk = next_chunk
    aggregated.append(current_chunk)
    return aggregated


def super_chunk_processes(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not chunks:
        return []
    step_pattern = re.compile(r'\b(step|phase)\s+(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b', re.IGNORECASE)
    new_chunks = []
    i = 0
    n = len(chunks)
    while i < n:
        chunk = chunks[i]
        topic = chunk['h3'] or chunk['h2'] or chunk['h1']
        if step_pattern.search(topic):
            furthest_step_idx = i
            j = i + 1
            while j < n:
                next_chunk = chunks[j]
                if next_chunk['h1'] != chunk['h1']:
                    break
                next_topic = next_chunk['h3'] or next_chunk['h2'] or next_chunk['h1']
                if step_pattern.search(next_topic):
                    furthest_step_idx = j
                if j - furthest_step_idx > 15:
                    break
                j += 1
            if furthest_step_idx > i:
                merged_chunk = chunks[i]
                first_topic = merged_chunk['h2'] or merged_chunk['h3'] or merged_chunk['h1']
                last_chunk = chunks[furthest_step_idx]
                last_topic = last_chunk['h2'] or last_chunk['h3'] or last_chunk['h1']
                combined_topic = f"{first_topic} to {last_topic} Process"
                start_page = merged_chunk['start_page']
                end_page = last_chunk['start_page']
                merged_chunk['page_range'] = f"{start_page}-{end_page}" if start_page != end_page else start_page
                for k in range(i + 1, furthest_step_idx + 1):
                    merged_chunk['lines'].append("")
                    merged_chunk['lines'].extend(chunks[k]['lines'])
                merged_chunk['h2'] = combined_topic
                merged_chunk['h3'] = ""
                new_chunks.append(merged_chunk)
                i = furthest_step_idx + 1
                continue
        new_chunks.append(chunk)
        i += 1
    return new_chunks


def process_file(filename: str, input_dir: str, output_dir: str) -> int:
    if filename not in FILE_MAP:
        return 0
    file_info = FILE_MAP[filename]
    abbrev = file_info['abbrev']
    level = file_info['level']
    source_name = file_info['name']

    filepath = os.path.join(input_dir, filename)
    if not os.path.exists(filepath):
        return 0

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    chunks = chunk_markdown(content)
    stitch_interrupted_chunks(chunks)
    chunks = aggregate_entities(chunks)
    chunks = super_chunk_processes(chunks)

    pad_len = max(4, len(str(len(chunks))))
    active_restriction = None
    restriction_level = 999
    processed_count = 0

    for idx, chunk in enumerate(chunks, 1):
        filtered_lines = []
        for line in chunk['lines']:
            if line.strip().startswith('#') or not is_header_footer_artifact(line):
                filtered_lines.append(line)

        chunk_content = '\n'.join(filtered_lines).strip()
        if not chunk_content:
            continue

        has_body = any(
            l.strip() and not l.strip().startswith('#') and not l.strip().startswith('**==>') and not l.strip().startswith('**-----')
            for l in filtered_lines
        )
        if not has_body:
            continue

        part_id = f"{abbrev}-{idx:0{pad_len}d}"
        chapter = chunk['h1'] or "General"
        if chunk['h3']:
            topic = chunk['h3']
            matched_level = 3
        elif chunk['h2']:
            topic = chunk['h2']
            matched_level = 2
        elif chunk['h1']:
            topic = chunk['h1']
            matched_level = 1
        else:
            topic = "Introduction"
            matched_level = 0

        if idx > 1:
            prev_chunk = chunks[idx-2]
            reset_restriction = False
            if restriction_level == 1 and chunk['h1'] != prev_chunk['h1']:
                reset_restriction = True
            elif restriction_level == 2 and (chunk['h1'] != prev_chunk['h1'] or chunk['h2'] != prev_chunk['h2']):
                reset_restriction = True
            elif restriction_level == 3 and (chunk['h1'] != prev_chunk['h1'] or chunk['h2'] != prev_chunk['h2'] or chunk['h3'] != prev_chunk['h3']):
                reset_restriction = True
            if reset_restriction:
                active_restriction = None
                restriction_level = 999

        topic_lower = topic.lower()
        category_matched = False
        for cat_name, restriction in CATEGORY_RESTRICTIONS.items():
            if cat_name in topic_lower:
                active_restriction = restriction
                restriction_level = matched_level
                category_matched = True
                break

        if not category_matched and any(x in topic_lower for x in ['game information', 'game mechanics', 'step ', 'phase ', 'introduction', 'credits', 'contents']):
            active_restriction = None
            restriction_level = 999

        restricted_to_val = active_restriction if (active_restriction and not category_matched) else None

        page_citation = None
        for header in [chunk['h3'], chunk['h2'], chunk['h1']]:
            if header:
                match = re.search(r'\bpp?\.\s*(\d+[-–]\d+|\d+)\b', header, re.IGNORECASE)
                if match:
                    page_citation = match.group(1)
                    break

        if 'page_range' in chunk:
            page_field = chunk['page_range']
        else:
            if not page_citation and chunk['start_page']:
                page_citation = chunk['start_page']
            if page_citation and isinstance(page_citation, str) and page_citation.isdigit():
                page_field = int(page_citation)
            else:
                page_field = page_citation or 1

        tags = get_tags(chunk_content)
        frontmatter = {
            'id': part_id,
            'source': source_name,
            'chapter': chapter,
            'topic': topic,
            'page': page_field,
            'authority_level': level,
            'tags': tags,
            'status': 'active',
            'overrides': []
        }
        if restricted_to_val:
            frontmatter['restricted_to'] = restricted_to_val

        out_filepath = os.path.join(output_dir, f"{part_id}.md")
        with open(out_filepath, 'w', encoding='utf-8') as out_f:
            out_f.write("---\n")
            yaml.dump(frontmatter, out_f, default_flow_style=False, sort_keys=False)
            out_f.write("---\n\n")
            out_f.write(chunk_content)
            out_f.write("\n")

        processed_count += 1

    return processed_count


def atomize_vault(
    input_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    single_file: Optional[str] = None,
    clear_output: bool = False
) -> Tuple[int, int]:
    """
    Atomizes markdown rulebooks from input_dir into individual rule chunks in output_dir.
    """
    from sr6core.rules_db import DEFAULT_VAULT_DIR, DEFAULT_CONVERTED_DIR
    in_dir = input_dir or DEFAULT_CONVERTED_DIR
    out_dir = output_dir or DEFAULT_VAULT_DIR

    if not os.path.exists(in_dir):
        os.makedirs(in_dir, exist_ok=True)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    if clear_output:
        for filename in os.listdir(out_dir):
            fp = os.path.join(out_dir, filename)
            try:
                if os.path.isfile(fp) or os.path.islink(fp):
                    os.unlink(fp)
                elif os.path.isdir(fp):
                    shutil.rmtree(fp)
            except Exception:
                pass

    total_chunks = 0
    processed_files = 0

    if single_file:
        files = [single_file]
    else:
        files = [f for f in os.listdir(in_dir) if f in FILE_MAP]

    for fname in files:
        if fname == "Shadowrun_Sixth_World_FAQ.md":
            try:
                from sr6core.vault.web_importer import import_web_faq
                cnt, _, _ = import_web_faq(converted_dir=in_dir, vault_dir=out_dir)
                total_chunks += cnt
                processed_files += 1
                continue
            except Exception:
                pass

        if fname in FILE_MAP:
            cnt = process_file(fname, in_dir, out_dir)
            total_chunks += cnt
            processed_files += 1

    return processed_files, total_chunks
