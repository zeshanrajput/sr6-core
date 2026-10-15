"""
PDF to Markdown Converter Module for SR6 Rulebooks and Sourcebooks.
Supports GPU-accelerated Docling (IBM Granite / DocLayNet + TableFormer with CUDA),
PyMuPDF4LLM fallback, and a domain-specific Shadowrun post-processing engine.
"""

import os
import re
import pathlib
from typing import Optional, List, Tuple, Dict, Any

# Optional / dynamic imports
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

try:
    import pymupdf4llm
except ImportError:
    pymupdf4llm = None

try:
    import mdformat
except ImportError:
    mdformat = None


# Common Shadowrun word-split / kerning repair dictionary
COMMON_KERNING_REPAIRS = [
    (r"\binf\s+amous\b", "infamous"),
    (r"\bshado\s*wrunner\b", "shadowrunner"),
    (r"\bshado\s*wrunners\b", "shadowrunners"),
    (r"\bshado\s*wrun\b", "shadowrun"),
    (r"\bcompa\s+tible\b", "compatible"),
    (r"\bcharac\s+ter\b", "character"),
    (r"\bcharac\s+ters\b", "characters"),
    (r"\bcyber\s+ware\b", "cyberware"),
    (r"\bbiow\s+are\b", "bioware"),
    (r"\bmeta\s+human\b", "metahuman"),
    (r"\bmeta\s+humans\b", "metahumans"),
    (r"\bmeta\s+type\b", "metatype"),
    (r"\bmeta\s+types\b", "metatypes"),
    (r"\binitia\s+tive\b", "initiative"),
    (r"\bexperi\s+ence\b", "experience"),
    (r"\bavail\s+ability\b", "availability"),
    (r"\bconnec\s+tion\b", "connection"),
    (r"\brestric\s+tion\b", "restriction"),
    (r"\brestric\s+tions\b", "restrictions"),
    (r"\bmodifi\s+cation\b", "modification"),
    (r"\bmodifi\s+cations\b", "modifications"),
    (r"\bdisad\s+vantage\b", "disadvantage"),
    (r"\bdisad\s+vantages\b", "disadvantages"),
    (r"\badvan\s+tage\b", "advantage"),
    (r"\badvan\s+tages\b", "advantages"),
    (r"\bunder\s+ground\b", "underground"),
    (r"\bintel\s+ligence\b", "intelligence"),
    (r"\bsurveil\s+lance\b", "surveillance"),
]

# Running headers / footers to strip from raw markdown
RUNNING_HEADER_PATTERNS = [
    r"(?m)^.*SHADOWRUN\s*//\s*SIXTH\s*WORLD.*$",
    r"(?m)^.*SHADOWRUN\s*//\s*CORE\s*RULES.*$",
    r"(?m)^.*SHADOWRUN\s*//\s*CITY\s*EDITION.*$",
    r"(?m)^.*SHADOWRUN\s*MISSIONS\s*GUIDE.*$",
    r"(?m)^.*RUNNING\s*A\s*LA\s*CARTE.*$",
    r"(?m)^.*ADVANCED\s*LIFESTYLES.*$",
    r"(?m)^.*OPTIONAL\s*RULES.*$",
    r"(?m)^.*CREDITS\s*Writing:.*$",
]


def clean_markdown_artifacts(text: str) -> str:
    """Removes common PDF conversion artifacts, hyphenation linebreaks, and normalizes ligatures."""
    # 1. Normalize HTML entities
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    
    # 2. Fix hyphenation issues at line breaks (word-\nword -> wordword)
    text = re.sub(r"(\w+)-\s*\n(\w+)", r"\1\2", text)
    
    # 3. Remove weird control characters
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    
    # 4. Normalize non-breaking spaces and zero-width spaces
    text = text.replace("\xa0", " ").replace("\xad", "").replace("\u200b", "").replace("\ufeff", "")
    
    # 5. Normalize common ligatures to standard ASCII characters
    ligature_map = {
        "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl",
        "ﬅ": "ft", "ﬆ": "st", "Æ": "AE", "æ": "ae", "Œ": "OE", "œ": "oe",
        "’": "'", "‘": "'", "“": '"', "”": '"', "—": " - ", "–": " - "
    }
    for lig, rep in ligature_map.items():
        text = text.replace(lig, rep)
    
    # 6. Remove excessive empty lines (more than 2)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def clean_shadowrun_markdown(text: str) -> str:
    """
    Shadowrun domain-specific post-processor:
    - Cleans image placeholders (<!-- image -->) and decorative borders
    - Strips running headers/footers
    - Repairs OCR kerning splits (e.g. inf amous -> infamous)
    - Formats JackPoint forum commentary into styled Markdown blockquotes
    - Normalizes stat blocks and table alignments
    - Standardizes header hierarchy
    """
    # 1. Base artifact cleanup
    text = clean_markdown_artifacts(text)

    # 2. Strip image placeholders and picture wrappers
    text = re.sub(r"<!--\s*image\s*-->", "", text)
    text = re.sub(r"\*\*==>\s*picture.*?intentionally omitted\s*<==\*\*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\*\*-----\s*Start of picture text\s*-----\*\*<br>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\*\*-----\s*End of picture text\s*-----\*\*<br>", "", text, flags=re.IGNORECASE)

    # 3. Strip running headers and footers
    for pat in RUNNING_HEADER_PATTERNS:
        text = re.sub(pat, "", text, flags=re.IGNORECASE)

    # 4. Repair kerning and word splits
    for pat, rep in COMMON_KERNING_REPAIRS:
        text = re.sub(pat, rep, text, flags=re.IGNORECASE)

    # 5. Format JackPoint shadowland commentary blocks
    # Format: > Posted by: Glitch (12:44:09/10-14-80) OR > User: comment
    def _format_jackpoint(match):
        header = match.group(1).strip()
        body = match.group(2).strip()
        return f"\n> **[JackPoint] {header}**\n> {body}\n"

    text = re.sub(
        r"(?m)^>\s*(?:Posted by:\s*)?([A-Za-z0-9_\-\s]+(?:\([\d/:\-\s]+\))?)\s*\n>\s*(.+)$",
        _format_jackpoint,
        text
    )

    # 6. Normalize header formatting
    # Clean leading/trailing spaces in headers and empty headers
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        # Remove empty headers like '## ' or '### ' or '## '
        if re.match(r"^#{1,6}\s*(?:|[^\w\s])?$", stripped):
            continue
        # Remove repeated redundant subheadings
        if stripped.lower() in ("## optional rules", "## advanced lifestyles", "## introduction"):
            if stripped.lower() == "## introduction":
                lines.append("## Introduction")
            continue
        lines.append(line)

    text = "\n".join(lines)

    # 7. Collapse leftover excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def is_cuda_available() -> bool:
    """Checks whether PyTorch has CUDA GPU support enabled."""
    return TORCH_AVAILABLE and torch.cuda.is_available()


def convert_pdf_with_docling(pdf_path: str, use_cuda: bool = True) -> str:
    """
    Converts a PDF file using Docling's deep learning document layout engine
    (DocLayNet + TableFormer) with optional CUDA acceleration on the GPU.
    """
    if not DOCLING_AVAILABLE:
        raise ImportError("docling is not installed. Run 'uv pip install docling'")

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True

    # If CUDA is requested and available, Docling automatically utilizes PyTorch CUDA
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    result = converter.convert(pdf_path)
    return result.document.export_to_markdown()


BOOK_PAGE_OFFSETS: Dict[str, Dict[str, int]] = {
    "SR6 Core Rulebook": {"start_pdf_page": 3, "offset": -2},
    "Firing Squad": {"start_pdf_page": 2, "offset": -1},
    "Street Wyrd": {"start_pdf_page": 2, "offset": -1},
    "Double Clutch": {"start_pdf_page": 2, "offset": -1},
    "Sixth World Companion": {"start_pdf_page": 3, "offset": -2},
    "Hack and Slash": {"start_pdf_page": 2, "offset": -1},
    "Body Shop": {"start_pdf_page": 2, "offset": -1},
    "Wild Life": {"start_pdf_page": 2, "offset": -1},
    "City Edition Seattle": {"start_pdf_page": 2, "offset": -1},
    "Berlin Edition": {"start_pdf_page": 2, "offset": -1},
    "State of the Art 2084": {"start_pdf_page": 2, "offset": -1},
}


def extract_page_number(page: Any, doc: Any, book_title: str = "") -> int:
    """
    Extracts the true printed page number using native /PageLabels,
    cropped footer bounding-box validation, or calibrated book offsets.
    """
    # 1. Primary: Native PDF /PageLabels
    try:
        label = page.get_label()
        if label and label.isdigit():
            val = int(label)
            if 0 < val < 2000:
                return val
    except Exception:
        pass

    # 2. Secondary: Cropped footer bounding box (bottom 7% of page)
    try:
        rect = page.rect
        footer_rect = page.rect.__class__(0, rect.height * 0.93, rect.width, rect.height)
        footer_text = page.get_text("text", clip=footer_rect).strip()
        digits = re.findall(r'\b\d{1,4}\b', footer_text)
        if digits:
            for d in digits:
                val = int(d)
                if 0 < val < 1500:
                    return val
    except Exception:
        pass

    # 3. Tertiary: Calibrated book offset
    for title_key, cfg in BOOK_PAGE_OFFSETS.items():
        if title_key.lower() in book_title.lower():
            return max(1, page.number + cfg.get("offset", 0))

    # 4. Fallback: 1-indexed physical page
    return page.number + 1


def reconstruct_statblock_table(block_dict: Dict[str, Any]) -> str:
    """Reconstructs attribute tables from PyMuPDF dict blocks if present."""
    lines = block_dict.get("lines", [])
    if not lines:
        return ""

    span_items = []
    for line in lines:
        for span in line.get("spans", []):
            t = span.get("text", "").strip()
            if t:
                span_items.append((span["bbox"][0], span["bbox"][1], t))

    texts = [t for _, _, t in span_items]

    # Check for primary attributes: B A R S W L I C (EDG, ESS)
    attr_keys = ["B", "A", "R", "S", "W", "L", "I", "C"]
    if all(k in texts[:12] for k in attr_keys):
        val_start = -1
        for i, t in enumerate(texts):
            if i > 7 and (t.replace(".", "").isdigit() or "(" in t or "+" in t):
                val_start = i
                break
        if val_start != -1:
            header_keys = texts[:val_start]
            values = texts[val_start:val_start + len(header_keys)]
            if len(values) == len(header_keys):
                md_table = "| " + " | ".join(header_keys) + " |\n"
                md_table += "| " + " | ".join(["---"] * len(header_keys)) + " |\n"
                md_table += "| " + " | ".join(values) + " |\n\n"
                return md_table

    # Check for secondary attributes: DR I/ID AC CM MOVE
    if all(k in texts[:8] for k in ["DR", "I/ID", "CM"]):
        val_start = -1
        for i, t in enumerate(texts):
            if i >= 3 and (t.isdigit() or "/" in t or "A" in t):
                val_start = i
                break
        if val_start != -1:
            header_keys = texts[:val_start]
            values = texts[val_start:val_start + len(header_keys)]
            if len(values) == len(header_keys):
                md_table = "| " + " | ".join(header_keys) + " |\n"
                md_table += "| " + " | ".join(["---"] * len(header_keys)) + " |\n"
                md_table += "| " + " | ".join(values) + " |\n\n"
                return md_table

    return ""


def convert_pdf_with_layout_stream(pdf_path: str) -> str:
    """
    Layout-aware, continuous stream extractor:
    - Resolves true printed page numbers via native /PageLabels and footer bounding box.
    - Injects deterministic inline <!-- PAGE: {n} --> anchors.
    - Sequences multi-column text geometry (x0, y0, width > 70%) to avoid column interleaving.
    - Reconstructs borderless / shaded stat blocks into standard Markdown tables.
    - Isolates JackPoint commentary into styled blockquotes.
    - Uses font metadata (size, font family, color) to tag H1/H2/H3 headings.
    """
    try:
        import pymupdf
    except ImportError:
        raise ImportError("pymupdf is required for layout stream conversion. Run 'uv pip install pymupdf'")

    doc = pymupdf.open(pdf_path)
    book_title = pathlib.Path(pdf_path).stem
    stream_output = []

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_num = extract_page_number(page, doc, book_title=book_title)
        page_rect = page.rect
        mid_x = page_rect.width / 2.0

        stream_output.append(f"\n\n<!-- PAGE: {page_num} -->\n\n")

        d = page.get_text("dict")
        blocks = d.get("blocks", [])

        # Filter out running header (top 5%) and running footer (bottom 6%)
        # Note: PyMuPDF's internal layout engine already orders blocks by natural reading flow.
        page_blocks = []
        for b in blocks:
            if "lines" not in b:
                continue
            x0, y0, x1, y1 = b["bbox"]
            if y1 <= page_rect.height * 0.05 or y0 >= page_rect.height * 0.94:
                continue
            page_blocks.append(b)

        for b in page_blocks:
            # Check for attribute stat block
            stat_table = reconstruct_statblock_table(b)
            if stat_table:
                stream_output.append(stat_table)
                continue

            block_lines = []
            lines = b.get("lines", [])
            idx = 0
            while idx < len(lines):
                line = lines[idx]
                spans = [s for s in line.get("spans", []) if s.get("text", "").strip()]
                if not spans:
                    idx += 1
                    continue

                line_text = "".join(s.get("text", "") for s in line.get("spans", []))
                first_sz = spans[0].get("size", 10.0)
                all_bold = all("bold" in s.get("font", "").lower() or "njord" in s.get("font", "").lower() for s in spans)
                clean_lt = line_text.strip()

                # Check if this line is an all-bold question (or start of a multi-line question)
                if all_bold and first_sz <= 12.5 and ("?" in clean_lt or (idx + 1 < len(lines) and "?" in "".join(s.get("text", "") for s in lines[idx+1].get("spans", [])))):
                    q_lines = [clean_lt]
                    while not q_lines[-1].endswith("?") and idx + 1 < len(lines):
                        next_spans = [s for s in lines[idx+1].get("spans", []) if s.get("text", "").strip()]
                        if next_spans and all("bold" in s.get("font", "").lower() or "njord" in s.get("font", "").lower() for s in next_spans):
                            idx += 1
                            q_lines.append("".join(s.get("text", "") for s in lines[idx].get("spans", [])).strip())
                        else:
                            break
                    full_q = " ".join(q_lines)
                    block_lines.append(f"\n### {full_q}\n")
                    idx += 1
                    continue

                # Check for all-caps section header (e.g. SECTION 2: ORGANIZED PLAY)
                if all_bold and clean_lt.isupper() and len(clean_lt) > 3 and not clean_lt.endswith("?"):
                    block_lines.append(f"\n## {clean_lt}\n")
                    idx += 1
                    continue

                formatted_line = ""
                for span in line.get("spans", []):
                    stext = span.get("text", "")
                    sz = span.get("size", 10.0)
                    fn = span.get("font", "").lower()
                    color = span.get("color", 0)

                    # Tag headings based on font properties
                    if sz >= 18.0:
                        stext = f"\n# {stext.strip()}\n"
                    elif sz >= 12.5 and ("njord" in fn or "bold" in fn or color in (0x960470, 0xbd1a8d)):
                        stext = f"\n## {stext.strip()}\n"
                    elif sz >= 11.0 and ("njord" in fn or "bold" in fn):
                        stext = f"\n### {stext.strip()}\n"
                    formatted_line += stext
                if formatted_line.strip():
                    block_lines.append(formatted_line)
                idx += 1

            if block_lines:
                if any(l.strip().startswith("#") for l in block_lines):
                    full_block = "\n".join(block_lines)
                else:
                    full_block = " ".join(block_lines)
                stream_output.append(full_block + "\n\n")

    return "".join(stream_output)


def convert_pdf_with_pymupdf(pdf_path: str) -> str:
    """
    Converts a PDF file using PyMuPDF4LLM fast layout parser.
    """
    if pymupdf4llm is None:
        raise ImportError("pymupdf4llm is not installed. Run 'uv pip install pymupdf4llm'")
    return pymupdf4llm.to_markdown(pdf_path, header=False, footer=False)


def convert_pdf_to_md(
    pdf_path: str,
    md_path: str,
    engine: str = "auto",
    use_cuda: bool = True,
    post_process: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Converts a single PDF file to cleaned Markdown using the specified engine.
    
    Engines:
      - 'auto': Uses 'layout' (column-aware + inline page markers) by default, or 'docling' if requested
      - 'layout': Layout-aware continuous stream with native /PageLabels and stat table reconstruction
      - 'docling': GPU-accelerated DocLayNet + TableFormer layout parser
      - 'pymupdf': Fast local PyMuPDF4LLM extractor
    """
    if not os.path.exists(pdf_path):
        return False, f"Source PDF not found: {pdf_path}"

    os.makedirs(os.path.dirname(os.path.abspath(md_path)), exist_ok=True)

    selected_engine = engine.lower()
    if selected_engine == "auto":
        selected_engine = "layout"

    try:
        if selected_engine == "layout":
            md_text = convert_pdf_with_layout_stream(pdf_path)
        elif selected_engine == "docling":
            md_text = convert_pdf_with_docling(pdf_path, use_cuda=use_cuda)
        elif selected_engine == "pymupdf":
            md_text = convert_pdf_with_pymupdf(pdf_path)
        else:
            return False, f"Unknown PDF conversion engine: '{engine}'. Use 'layout', 'docling', or 'pymupdf'."
    except Exception as e:
        return False, f"PDF conversion failed with engine '{selected_engine}': {e}"

    # Apply Shadowrun domain post-processing
    if post_process:
        md_text = clean_shadowrun_markdown(md_text)
    else:
        md_text = clean_markdown_artifacts(md_text)

    # Format if mdformat is available
    if mdformat is not None:
        try:
            md_text = mdformat.text(md_text, extensions={"gfm"})
        except Exception:
            pass

    try:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_text)
        return True, None
    except Exception as e:
        return False, f"Failed writing output markdown: {e}"


def batch_convert_pdfs(
    input_dir: str,
    output_dir: str,
    regenerate: bool = False,
    engine: str = "auto",
    use_cuda: bool = True,
    curated_core_only: bool = False
) -> Tuple[int, int, List[str]]:
    """
    Batch converts all PDFs in input_dir to markdown files in output_dir.
    If curated_core_only is True, skips redundant deprecated core books and focuses
    on City Edition: Hong Kong plus regional sprawl additions.
    """
    if not os.path.exists(input_dir):
        return 0, 0, [f"Input directory not found: {input_dir}"]

    os.makedirs(output_dir, exist_ok=True)
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    
    # Optional curation filter: skip older base core books if Hong Kong is present
    if curated_core_only:
        # Keep Hong Kong (SR6H), Seattle, Berlin, and supplements; skip older raw 2019 base core
        curated_files = []
        for f in pdf_files:
            lower = f.lower()
            if "28000_shadowrun_sixth_edition" in lower or "sixth_world_core_rulebook_2019" in lower:
                continue
            curated_files.append(f)
        pdf_files = curated_files

    success_count = 0
    errors = []

    for filename in pdf_files:
        pdf_path = os.path.join(input_dir, filename)
        md_filename = pathlib.Path(filename).stem + ".md"
        md_path = os.path.join(output_dir, md_filename)

        if os.path.exists(md_path) and not regenerate:
            success_count += 1
            continue

        ok, err = convert_pdf_to_md(
            pdf_path=pdf_path,
            md_path=md_path,
            engine=engine,
            use_cuda=use_cuda,
            post_process=True
        )
        if ok:
            success_count += 1
        else:
            errors.append(f"{filename}: {err}")

    return success_count, len(pdf_files), errors
