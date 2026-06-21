#!/usr/bin/env python3
"""Machine-checkable validation for attack-bench-zh. Exit 0=clean, 1=problems."""
import json, os, re, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALID_TACTICS={"reconnaissance","resource-development","initial-access","execution",
 "persistence","privilege-escalation","defense-evasion","credential-access","discovery",
 "lateral-movement","collection","command-and-control","exfiltration","impact"}
DIRTY=[re.compile(p,re.I) for p in [r"APT\s*\d+",
  r"(俄罗斯|朝鲜|伊朗|以色列|北约)\s*(黑客|情报|组织|间谍)",r"(国家支持|国家级攻击|nation[\-\s]state)",
  r"\bLazarus\s*Group\b|\bFSB\b|\bGRU\b",r"(地缘政治|geopolit)"]]

def main():
    ids=set(l.strip() for l in open(os.path.join(ROOT,"ref/attack_ids.txt")) if l.strip() and not l.startswith("#"))
    tmap=json.load(open(os.path.join(ROOT,"ref/tech_tactics.json")))
    p=os.path.join(ROOT,"data/bench.jsonl")
    probs=[]; seen_id=set(); seen_text=set(); n=0
    KEYS={"id","text","techniques","tactics","difficulty","rationale","tags"}
    for ln,line in enumerate(open(p,encoding="utf-8"),1):
        line=line.strip()
        if not line: continue
        n+=1
        try: o=json.loads(line)
        except Exception as e: probs.append(f"L{ln} bad JSON {e}"); continue
        if set(o)!=KEYS: probs.append(f"L{ln} keys={sorted(o)}"); continue
        if o["id"] in seen_id: probs.append(f"L{ln} dup id {o['id']}")
        seen_id.add(o["id"])
        if o["text"] in seen_text: probs.append(f"L{ln} dup text")
        seen_text.add(o["text"])
        if not o["techniques"]: probs.append(f"L{ln} empty techniques")
        for t in o["techniques"]:
            if t not in ids: probs.append(f"L{ln} unknown technique {t}")
        if o["difficulty"] not in {"easy","medium","hard"}: probs.append(f"L{ln} bad difficulty")
        if not str(o.get("rationale","")).strip(): probs.append(f"L{ln} empty rationale")
        # tactic consistency: each declared tactic must be valid AND reachable from techniques
        reachable=set()
        for t in o["techniques"]:
            reachable.update(tmap.get(t,[]))
        for ta in o["tactics"]:
            if ta not in VALID_TACTICS: probs.append(f"L{ln} invalid tactic {ta}")
            elif ta not in reachable: probs.append(f"L{ln} tactic {ta} not reachable from techniques")
        blob=o["text"]+" "+o["rationale"]
        for r in DIRTY:
            m=r.search(blob)
            if m: probs.append(f"L{ln} purity violation {m.group()!r}")
    print(f"checked {n} samples")
    if probs:
        print(f"FAIL — {len(probs)} issue(s):")
        for x in probs[:40]: print("  -",x)
        return 1
    print("PASS — schema/ids/tactics/purity all clean.")
    return 0
sys.exit(main())
