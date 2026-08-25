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
      - 'auto': Prefers 'docling' if GPU/Docling available, falls back to 'pymupdf'
      - 'docling': GPU-accelerated DocLayNet + TableFormer layout parser
      - 'pymupdf': Fast local PyMuPDF4LLM extractor
    """
    if not os.path.exists(pdf_path):
        return False, f"Source PDF not found: {pdf_path}"

    os.makedirs(os.path.dirname(os.path.abspath(md_path)), exist_ok=True)

    # Engine selection
    selected_engine = engine.lower()
    if selected_engine == "auto":
        if DOCLING_AVAILABLE and (is_cuda_available() or not pymupdf4llm):
            selected_engine = "docling"
        elif pymupdf4llm is not None:
            selected_engine = "pymupdf"
        elif DOCLING_AVAILABLE:
            selected_engine = "docling"
        else:
            return False, "Neither 'docling' nor 'pymupdf4llm' are installed."

    try:
        if selected_engine == "docling":
            md_text = convert_pdf_with_docling(pdf_path, use_cuda=use_cuda)
        elif selected_engine == "pymupdf":
            md_text = convert_pdf_with_pymupdf(pdf_path)
        else:
            return False, f"Unknown PDF conversion engine: '{engine}'. Use 'docling', 'pymupdf', or 'auto'."
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
