import re
from sr6core.log_engine import create_quarto_eval_env, _GLOBAL_LOG_STATE

def test_character_math(char_id):
    print("=" * 60)
    print(f"TESTING {char_id.upper()}")
    print("=" * 60)
    
    # 1. Evaluate build
    env = create_quarto_eval_env()
    _GLOBAL_LOG_STATE.clear()
    with open(f"characters/{char_id}/core/character_build.qmd", encoding="utf-8") as f:
        b_text = f.read()
    pattern = re.compile(r'```\{python\}(.*?)```|`\{python\}\s*(.*?)`', re.DOTALL)
    for m in pattern.finditer(b_text):
        b, i = m.group(1), m.group(2)
        if b:
            lines = [l.strip() for l in b.splitlines() if not l.strip().startswith("#|")]
            try: exec("\n".join(lines), env)
            except Exception as e: print("Build block error:", e)
        elif i:
            try: eval(i.strip(), env)
            except Exception:
                try: exec(i.strip(), env)
                except Exception: pass
    
    b_k = _GLOBAL_LOG_STATE.get("Karma", 0)
    b_ny = _GLOBAL_LOG_STATE.get("Nuyen", 0)
    print(f"Build completion -> Karma: {b_k}, Nuyen: ¥{b_ny:,}")
    
    # 2. Evaluate purchases
    with open(f"characters/{char_id}/core/character_purchases.qmd", encoding="utf-8") as f:
        p_text = f.read()
    p_env = create_quarto_eval_env()
    _GLOBAL_LOG_STATE.clear()
    for m in pattern.finditer(p_text):
        b, i = m.group(1), m.group(2)
        if b:
            lines = [l.strip() for l in b.splitlines() if not l.strip().startswith("#|")]
            try: exec("\n".join(lines), p_env)
            except Exception: pass
        elif i:
            try: eval(i.strip(), p_env)
            except Exception:
                try: exec(i.strip(), p_env)
                except Exception: pass
    p_k = _GLOBAL_LOG_STATE.get("Karma", 0)
    p_ny = _GLOBAL_LOG_STATE.get("Nuyen", 0)
    print(f"Purchases net changes -> Karma: {p_k}, Nuyen: ¥{p_ny:,}")
    
    # 3. Evaluate log starting from Build completion
    with open(f"characters/{char_id}/core/character_log.qmd", encoding="utf-8") as f:
        l_text = f.read()
    
    _GLOBAL_LOG_STATE.clear()
    _GLOBAL_LOG_STATE["Karma"] = b_k
    _GLOBAL_LOG_STATE["Lifetime_Karma"] = b_k
    _GLOBAL_LOG_STATE["Nuyen"] = b_ny
    _GLOBAL_LOG_STATE["Lifetime_Nuyen"] = 50000 if char_id == "velvet" else 90000
    
    l_env = create_quarto_eval_env()
    for m in pattern.finditer(l_text):
        b, i = m.group(1), m.group(2)
        if b:
            lines = [l.strip() for l in b.splitlines() if not l.strip().startswith("#|") and not l.strip().startswith('assign("Karma"') and not l.strip().startswith('assign("Nuyen"') and not l.strip().startswith('assign("Lifetime')]
            try: exec("\n".join(lines), l_env)
            except Exception as e: pass
        elif i:
            code = i.strip()
            if "assign" in code and ("Karma" in code or "Nuyen" in code or "Lifetime" in code):
                continue
            try: eval(code, l_env)
            except Exception:
                try: exec(code, l_env)
                except Exception: pass
    
    final_k = _GLOBAL_LOG_STATE.get("Karma", 0)
    final_lk = _GLOBAL_LOG_STATE.get("Lifetime_Karma", 0)
    final_ny = _GLOBAL_LOG_STATE.get("Nuyen", 0)
    final_lny = _GLOBAL_LOG_STATE.get("Lifetime_Nuyen", 0)
    print(f"Log evaluated from chargen balance -> Karma: {final_k}, Lifetime_Karma: {final_lk}, Nuyen: ¥{final_ny:,}, Lifetime_Nuyen: ¥{final_lny:,}")

if __name__ == "__main__":
    test_character_math("velvet")
    test_character_math("reiko")
