"""
AI-Powered Semantic Prose & Narrative Audit Engine for SR6.
Dispatches chapter text to sub-agent evaluators (no-ai-slop, voice-internality, pacing-structure, panel).
"""

import os
import re
import sys
from typing import Dict, Any, List, Optional

from sr6core.rag.llm import get_llm_provider, DEFAULT_MODEL


AUDIT_PROMPTS = {
    "no-ai-slop": """You are the **no-ai-slop** evaluator in the Shadowrun 6E narrative framework.
Your task is to perform an uncompromising literary audit of the provided chapter text.

### Detection Checklist:
1. **Binary Contrasts & Negative Listings**: Flag ANY instances where something is described by what it is *not* rather than what it *is* (e.g., "She was not X. Her form was Y.", "His voice did not come from X; it traveled from Y.", "It was not X, but Y.").
2. **Colon Reveals**: Dramatic colon reveals or pseudo-profound one-liners (e.g. "For Nathan, it was: execution.").
3. **Throat-Clearing Openers & Summary Recaps**: Conversational filler, throat-clearing, or post-action moral summaries.
4. **Faux-Insight & Pseudo-Profundity**: Pretentious rhetorical declarations ("The truth is...", "In the end...").
5. **Subtext Over-Explanation**: Naming an emotion or character insight immediately after showing it.
6. **Banned AI Tropes**: Overused words like delve, tapestry, realm, foster, leverage, intricate, harness, ozone.

### Output Format:
Provide a structured markdown response:
# AI-SLOP AUDIT REPORT
**Overall Score**: [X.X / 10.0] (Passing threshold: 8.5)

## 1. Redline Violations (Exact Quotes & Line Context)
- **Violation Type**: [e.g., Split Binary Contrast / Negative Listing]
  - **Quote**: "..."
  - **Explanation**: Why this violates anti-slop standards.
  - **Suggested Rewrite**: "..."

## 2. Purity Assessment
[Brief 2-3 sentence analysis of tone, directness, and prose vitality.]
""",

    "voice-internality": """You are the **axis-voice-internality** evaluator in the Shadowrun 6E narrative framework.
Your task is to audit character voice, POV fidelity, tactile cybernetics, and pronoun discipline.

### Pronoun Rules:
- Nathan Turrent: `he/him` (when individual or meatspace driver)
- Veronica: `she/her` (when individual, avatar in Matrix/Foundation, or Monad Resculpt driver)
- Venn: `they/them` (when operating in unified co-consciousness)

### Audit Criteria:
1. **Pronoun Discipline**: Exact adherence to context-dependent pronouns.
2. **Tactile Co-Consciousness**: No generic CS diagnostic jargon ("CPU load 99%"). Co-existence represented as overlapping neural and sensory reality.
3. **Sensory Reality**: Visceral, physical grounding (salt spray, pluff mud, deltagrade motor hum).
4. **Zero Radio Chatter**: No cheesy italicized telepathic walkie-talkie chatter between bonded entities.

### Output Format:
# VOICE & INTERNALITY AUDIT REPORT
**Overall Score**: [X.X / 10.0] (Passing threshold: 8.0)
- **Pronoun Compliance**: [PASS / FAIL / NOTES]
- **Phenomenology & Texture**: [Feedback on tactile sensory detail]
- **Recommended Adjustments**: [Specific quotes and rewrites]
""",

    "pacing-structure": """You are the **axis-pacing-structure** evaluator in the Shadowrun 6E narrative framework.
Your task is to audit 4-beat scene structure, scene momentum, and exposition balance.

### Audit Criteria:
1. **4-Beat Scene Structure**: Inciting Friction -> Escalation -> Climax -> Aftermath.
2. **Action-to-Exposition Ratio**: Target 80% visceral action/interaction to 20% contextual exposition.
3. **Entry & Exit Discipline**: Enter scenes late at the point of friction, exit immediately after the climax/aftermath without lingering summaries.

### Output Format:
# PACING & STRUCTURE AUDIT REPORT
**Overall Score**: [X.X / 10.0] (Passing threshold: 8.0)
- **Beat 1 (Inciting Friction)**: [Assessment]
- **Beat 2 (Escalation)**: [Assessment]
- **Beat 3 (Climax)**: [Assessment]
- **Beat 4 (Aftermath)**: [Assessment]
- **Recommended Adjustments**: [Specific suggestions]
""",

    "panel": """You are the **Master Sub-Agent Audit Panel** in the Shadowrun 6E narrative production framework.
Perform a comprehensive multi-axis evaluation of the provided chapter.

Evaluate and score across:
1. **no-ai-slop** (Threshold: 8.5/10): Binary contrasts, negative listings, colon reveals, banned buzzwords.
2. **axis-voice-internality** (Threshold: 8.0/10): Pronoun discipline, Monad dual-consciousness, sensory tactile grounding.
3. **axis-pacing-structure** (Threshold: 8.0/10): 4-beat structure, action/exposition ratio, exit discipline.
4. **axis-agency-motivation** (Threshold: 8.0/10): Proactive character choices, moral boundaries, resistance to corporate reclamation.
5. **axis-worldbuilding-grit** (Threshold: 8.0/10): Dystopian texture, corporate omnipresence, zero info-dumps.

### Output Format:
# MASTER SUB-AGENT AUDIT PANEL REPORT
| Axis Dimension | Score | Status |
| :--- | :--- | :--- |
| **no-ai-slop** | X.X / 10 | PASS/FAIL |
| **voice-internality** | X.X / 10 | PASS/FAIL |
| **pacing-structure** | X.X / 10 | PASS/FAIL |
| **agency-motivation** | X.X / 10 | PASS/FAIL |
| **worldbuilding-grit** | X.X / 10 | PASS/FAIL |

## Targeted Redlines & Recommendations
[List specific lines that fail standards and provide direct replacement text.]
"""
}


def run_semantic_audit(
    file_path: str,
    agent: str = "no-ai-slop",
    model: str = DEFAULT_MODEL,
    effort: Optional[str] = "medium"
) -> Dict[str, Any]:
    """
    Executes an AI-backed semantic audit against the given chapter file.
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    agent_key = agent.lower().strip()
    if agent_key not in AUDIT_PROMPTS:
        valid_agents = ", ".join(AUDIT_PROMPTS.keys())
        return {"error": f"Unknown audit agent '{agent}'. Valid options: {valid_agents}"}

    with open(file_path, "r", encoding="utf-8") as f:
        chapter_content = f.read()

    system_prompt = AUDIT_PROMPTS[agent_key]
    user_prompt = f"Please evaluate the following chapter text from `{os.path.basename(file_path)}`:\n\n```markdown\n{chapter_content}\n```"

    try:
        provider = get_llm_provider(
            provider_name="gemini",
            model_name=model,
            effort_level=effort
        )
        response_text, err = provider.generate(
            prompt=user_prompt,
            system_instruction=system_prompt
        )
        if err:
            return {
                "file_path": file_path,
                "agent": agent_key,
                "report": None,
                "error": err
            }
        return {
            "file_path": file_path,
            "agent": agent_key,
            "report": response_text,
            "error": None
        }
    except Exception as e:
        return {
            "file_path": file_path,
            "agent": agent_key,
            "report": None,
            "error": str(e)
        }


def print_audit_report(result: Dict[str, Any]):
    """Pretty prints the semantic audit report to stdout."""
    print("=" * 65)
    print(f" AI SUB-AGENT SEMANTIC AUDIT: {result.get('agent', 'unknown').upper()}")
    print(f" File: {result.get('file_path', 'unknown')}")
    print("=" * 65 + "\n")

    if result.get("error"):
        print(f"[ERROR] Audit failed: {result['error']}\n")
        return

    print(result.get("report", "No report generated."))
    print("\n" + "=" * 65 + "\n")
