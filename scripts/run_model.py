#!/usr/bin/env python3
"""Run an OpenAI-compatible chat model over attack-bench-zh -> predictions.jsonl.
Zero deps (urllib). Then score with scripts/score.py.

Usage:
  export OPENAI_API_KEY=sk-...
  python3 scripts/run_model.py --model gpt-4o [--base-url https://api.openai.com/v1] [--limit N]
Output: predictions_<model>.jsonl  ({"id":..., "techniques":[...]})
Works with any OpenAI-compatible endpoint (OpenAI / DeepSeek / Qwen / 本地 vLLM …).
"""
import argparse, json, os, re, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SYS = ("你是网络安全威胁情报分析助手。给定一段中文威胁/事件描述，"
       "判断它对应的 MITRE ATT&CK 技术编号（如 T1059.001）。"
       "只输出一个 JSON 数组，元素为技术编号字符串，不要解释。示例：[\"T1566.001\",\"T1059.001\"]")

def extract_json(text):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m: text = m.group(1).strip()
    i = text.find("[")
    if i >= 0:
        try: return json.loads(text[i:text.rfind("]")+1])
        except Exception: pass
    return []

def call(base, key, model, text):
    body = json.dumps({"model": model, "temperature": 0,
        "messages":[{"role":"system","content":SYS},{"role":"user","content":text}]}).encode()
    req = urllib.request.Request(base.rstrip("/")+"/chat/completions", data=body,
        headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL","https://api.openai.com/v1"))
    ap.add_argument("--key", default=os.environ.get("OPENAI_API_KEY",""))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    if not a.key: print("ERROR: set OPENAI_API_KEY or --key"); return 2
    out = a.out or os.path.join(ROOT, f"predictions_{re.sub(r'[^a-zA-Z0-9._-]','_',a.model)}.jsonl")
    rows = [json.loads(l) for l in open(os.path.join(ROOT,"data","bench.jsonl"),encoding="utf-8") if l.strip()]
    if a.limit: rows = rows[:a.limit]
    with open(out, "w", encoding="utf-8") as w:
        for i, o in enumerate(rows, 1):
            try:
                techs = extract_json(call(a.base_url, a.key, a.model, o["text"]))
                techs = [t for t in techs if isinstance(t, str)]
            except Exception as e:
                print(f"  [{i}] {o['id']} error: {e}"); techs = []
            w.write(json.dumps({"id":o["id"],"techniques":techs},ensure_ascii=False)+"\n")
            print(f"  [{i}/{len(rows)}] {o['id']} -> {techs}")
    print(f"\nwrote {out}\n下一步: python3 scripts/score.py {out}")
    return 0
if __name__ == "__main__": sys.exit(main())
