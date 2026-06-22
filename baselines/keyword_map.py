#!/usr/bin/env python3
"""Naive keyword->technique baseline. Writes predictions_keyword.jsonl."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = [("PowerShell","T1059.001"),("powershell","T1059.001"),("钓鱼","T1566.001"),
         ("宏","T1204.002"),("加密","T1486"),("卷影","T1490"),("横向","T1021"),
         ("webshell","T1505.003"),("上传","T1190")]
def main():
    out=open(os.path.join(ROOT,"baselines","predictions_keyword.jsonl"),"w",encoding="utf-8")
    for line in open(os.path.join(ROOT,"data","bench.jsonl"),encoding="utf-8"):
        line=line.strip()
        if not line: continue
        o=json.loads(line); text=o["text"]
        hits=sorted({tid for kw,tid in RULES if kw in text})
        out.write(json.dumps({"id":o["id"],"techniques":hits},ensure_ascii=False)+"\n")
    print("wrote baselines/predictions_keyword.jsonl")
if __name__=="__main__": main()
