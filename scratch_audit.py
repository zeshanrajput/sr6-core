import re
from sr6core.log_engine import create_quarto_eval_env, _GLOBAL_LOG_STATE

def audit_character(char_id):
    print("=" * 60)
    print(f"AUDITING {char_id.upper()}")
    print("=" * 60)
    
    # 1. Evaluate build
    env = create_quarto_eval_env()
    _GLOBAL_LOG_STATE.clear()
    build_path = f"characters/{char_id}/core/character_build.qmd"
    content = open(build_path, "r", encoding="utf-8").read()
    pattern = re.compile(r'```\{python\}(.*?)```|`\{python\}\s*(.*?)`', re.DOTALL)
    for match in pattern.finditer(content):
        block, inline = match.group(1), match.group(2)
        if block:
            lines = [l.strip() for l in block.splitlines() if not l.strip().startswith('#|')]
            try: exec('\n'.join(lines), env)
            except Exception as e: pass
        elif inline:
            try: eval(inline.strip(), env)
            except:
                try: exec(inline.strip(), env)
                except: pass
    
    chargen_karma = _GLOBAL_LOG_STATE.get("Karma", 0)
    chargen_nuyen = _GLOBAL_LOG_STATE.get("Nuyen", 0)
    print(f"Chargen Leftovers -> Karma: {chargen_karma}, Nuyen: ¥{chargen_nuyen:,}")
    
    # 2. Check what character_log.qmd starts with
    log_path = f"characters/{char_id}/core/character_log.qmd"
    log_content = open(log_path, "r", encoding="utf-8").read()
    
    # Extract assign statements in log
    assigns = re.findall(r'assign\s*\(\s*["\']([^"\']+)["\']\s*,\s*([^)]+)\)', log_content)
    print(f"Log Baseline assigns: {assigns}")
    
    # 3. Check what happens if log starts from chargen leftovers vs if log re-assigns full budget
    print("-" * 40)

if __name__ == "__main__":
    audit_character("velvet")
    audit_character("reiko")
