#!/usr/bin/env python3
"""Naive keyword->technique baseline. Emits predictions_keyword.jsonl."""
import json, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES=[("powershell","T1059.001"),("certutil","T1105"),("mimikatz","T1003.001"),
 ("lsass","T1003.001"),("钓鱼附件","T1566.001"),("钓鱼","T1566.002"),("宏","T1204.002"),
 ("rdp","T1021.001"),("远程桌面","T1021.001"),("ssh","T1021.004"),("smb","T1021.002"),
 ("计划任务","T1053.005"),("schtasks","T1053.005"),("run键","T1547.001"),("注册表","T1112"),
 ("勒索","T1486"),("加密","T1486"),("卷影","T1490"),("挖矿","T1496"),("xmrig","T1496"),
 ("web shell","T1505.003"),("webshell","T1505.003"),("暴力破解","T1110"),("口令喷洒","T1110"),
 ("注入","T1055"),("base64","T1027"),("混淆","T1027"),("禁用","T1562.001"),("defender","T1562.001"),
 ("清除","T1070.001"),("日志","T1070.001"),("删除","T1070.004"),("dns","T1048"),("隧道","T1572"),
 ("frp","T1572"),("anydesk","T1219"),("whoami","T1082"),("ipconfig","T1016"),("tasklist","T1057"),
 ("net group","T1087.002"),("net user","T1087.002"),("net view","T1018"),("云盘","T1567.002"),
 ("打包","T1560.001"),("7-zip","T1560.001"),("python","T1059.006"),("vpn","T1133"),("bash","T1059.004")]
out=[]
for line in open(os.path.join(ROOT,"data/bench.jsonl"),encoding="utf-8"):
    line=line.strip()
    if not line: continue
    o=json.loads(line); txt=o["text"].lower(); hit=[]
    for kw,t in RULES:
        if kw.lower() in txt and t not in hit: hit.append(t)
    out.append({"id":o["id"],"techniques":hit})
with open(os.path.join(ROOT,"baselines/predictions_keyword.jsonl"),"w") as f:
    for r in out: f.write(json.dumps(r,ensure_ascii=False)+"\n")
print("wrote",len(out),"predictions")
