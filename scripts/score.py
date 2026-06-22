#!/usr/bin/env python3
"""Score predictions for attack-bench-zh (multi-label technique mapping).
Usage: python3 scripts/score.py predictions.jsonl
predictions: one JSON/line {"id":..., "techniques":[...]}"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(path, key):
    d = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            o = json.loads(line); d[o["id"]] = set(o.get(key, []))
    return d

def top(s): return {t.split(".")[0] for t in s}

def prf(tp, fp, fn):
    p = tp/(tp+fp) if tp+fp else 0.0
    r = tp/(tp+fn) if tp+fn else 0.0
    f = 2*p*r/(p+r) if p+r else 0.0
    return round(p,3), round(r,3), round(f,3)

def main():
    if len(sys.argv) < 2: print("usage: score.py predictions.jsonl"); return 2
    gold = load(os.path.join(ROOT,"data","bench.jsonl"), "techniques")
    pred = load(sys.argv[1], "techniques")
    tp=fp=fn=0; ttp=tfp=tfn=0; missing=0
    for gid, g in gold.items():
        p = pred.get(gid)
        if p is None: missing += 1; p = set()
        tp += len(g & p); fp += len(p - g); fn += len(g - p)
        gt, pt = top(g), top(p)
        ttp += len(gt & pt); tfp += len(pt - gt); tfn += len(gt - pt)
    P,R,F = prf(tp,fp,fn); tP,tR,tF = prf(ttp,tfp,tfn)
    rep = {"n_gold": len(gold), "missing_predictions": missing,
           "technique_micro": {"precision":P,"recall":R,"f1":F},
           "top_technique_micro": {"precision":tP,"recall":tR,"f1":tF}}
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    open(os.path.join(ROOT,"report.json"),"w",encoding="utf-8").write(json.dumps(rep,ensure_ascii=False,indent=2))
    return 0
if __name__ == "__main__": sys.exit(main())
