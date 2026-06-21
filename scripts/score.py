#!/usr/bin/env python3
"""Score predictions for attack-bench-zh.
Predictions: JSONL of {"id":..., "techniques":[...]}. Usage: score.py preds.jsonl"""
import json, os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p):
    d={}
    for line in open(p,encoding="utf-8"):
        line=line.strip()
        if line:
            o=json.loads(line); d[o["id"]]=o
    return d
def top(t): return t.split(".")[0]
def prf(tp,fp,fn):
    P=tp/(tp+fp) if tp+fp else 0.0; R=tp/(tp+fn) if tp+fn else 0.0
    F=2*P*R/(P+R) if P+R else 0.0; return P,R,F
def main():
    if len(sys.argv)<2: print("usage: score.py preds.jsonl"); return 2
    gold=load(os.path.join(ROOT,"data/bench.jsonl")); pred=load(sys.argv[1])
    tmap=json.load(open(os.path.join(ROOT,"ref/tech_tactics.json")))
    miss=[i for i in gold if i not in pred]
    tp=fp=fn=0; ttp=tfp=tfn=0; atp=afp=afn=0  # technique / top-technique / tactic
    for i,g in gold.items():
        G=set(g["techniques"]); P=set(pred.get(i,{}).get("techniques",[]))
        tp+=len(G&P); fp+=len(P-G); fn+=len(G-P)
        GT={top(x) for x in G}; PT={top(x) for x in P}
        ttp+=len(GT&PT); tfp+=len(PT-GT); tfn+=len(GT-PT)
        GA=set(a for x in G for a in tmap.get(x,[])); PA=set(a for x in P for a in tmap.get(x,[]))
        atp+=len(GA&PA); afp+=len(PA-GA); afn+=len(GA-PA)
    out={"n_scored":len(gold),"missing_predictions":len(miss)}
    for name,v in [("technique",(tp,fp,fn)),("top_technique",(ttp,tfp,tfn)),("tactic",(atp,afp,afn))]:
        P,R,F=prf(*v); out[f"{name}_precision"]=round(P,3); out[f"{name}_recall"]=round(R,3); out[f"{name}_f1"]=round(F,3)
    json.dump(out,open(os.path.join(ROOT,"report.json"),"w"),ensure_ascii=False,indent=2)
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return 0
sys.exit(main())
