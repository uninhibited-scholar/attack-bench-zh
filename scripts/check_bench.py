#!/usr/bin/env python3
"""CI gate for attack-bench-zh. Exit 0 = clean, 1 = problems."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TACTICS = {"reconnaissance","resource-development","initial-access","execution",
    "persistence","privilege-escalation","defense-evasion","credential-access",
    "discovery","lateral-movement","collection","command-and-control",
    "exfiltration","impact"}
KEYS = {"id","text","techniques","tactics","difficulty","rationale","tags"}
TID = re.compile(r"^T\d{4}(\.\d{3})?$")
DIRTY = [re.compile(p, re.I) for p in
         [r"APT\s*\d+", r"(俄罗斯|朝鲜|伊朗|以色列)\s*(黑客|情报|组织|间谍)",
          r"\bLazarus\s*Group\b", r"地缘政治"]]

def load_ids():
    p = os.path.join(ROOT, "ref", "attack_ids.txt")
    return {l.strip() for l in open(p, encoding="utf-8") if l.strip() and not l.startswith("#")}

def main():
    valid = load_ids()
    f = os.path.join(ROOT, "data", "bench.jsonl")
    problems, ids, texts, n = [], set(), set(), 0
    for ln, line in enumerate(open(f, encoding="utf-8"), 1):
        line = line.strip()
        if not line: continue
        n += 1
        try: o = json.loads(line)
        except Exception as e: problems.append(f"L{ln} bad JSON: {e}"); continue
        if set(o) != KEYS: problems.append(f"L{ln} keys={sorted(o)}")
        if o.get("id") in ids: problems.append(f"L{ln} dup id {o.get('id')}")
        ids.add(o.get("id"))
        t = o.get("text","").strip()
        if t in texts: problems.append(f"L{ln} dup text")
        texts.add(t)
        techs = o.get("techniques") or []
        if not techs: problems.append(f"L{ln} empty techniques")
        for tid in techs:
            if not TID.match(tid): problems.append(f"L{ln} bad id format {tid}")
            elif tid not in valid: problems.append(f"L{ln} unknown ATT&CK id {tid}")
        for tac in o.get("tactics", []):
            if tac not in TACTICS: problems.append(f"L{ln} bad tactic {tac}")
        blob = t + " " + o.get("rationale","")
        for r in DIRTY:
            m = r.search(blob)
            if m: problems.append(f"L{ln} purity: {m.group()!r}")
    print(f"checked {n} records")
    if problems:
        print(f"FAIL — {len(problems)} issue(s):")
        for p in problems[:50]: print("  -", p)
        return 1
    print("PASS — schema/IDs/tactics/dupes/purity all clean.")
    return 0
if __name__ == "__main__": sys.exit(main())
