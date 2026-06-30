# attack-bench-zh

中文 · 威胁情报文本 → ATT&CK 技术编号 标注映射集（可机器评分，防御导向）。

[![CI](https://github.com/uninhibited-scholar/attack-bench-zh/actions/workflows/validate.yml/badge.svg)](https://github.com/uninhibited-scholar/attack-bench-zh/actions/workflows/validate.yml)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-green.svg)](https://creativecommons.org/licenses/by/4.0/)

给一段中文威胁/事件描述，标注其对应的 ATT&CK 技术编号（如 `T1059.001`）。**ATT&CK 编号是封闭词表 → 评分为 exact / partial match，零主观、CI 可担保。** 是检测工程的**上游**（先定 technique，才谈检测规则），与下游规则生成基准（如 CTI-REALM）互补。

> 现状诚实定位：**v1.0 共 300 条、单人标注、关键词基线**——一个**能跑通、有论点、可复现**的基准（v0 验收目标已达成）；多模型基线与人工交叉校验见 [PLAN.md](PLAN.md)。

## 数据
- `data/bench.jsonl`，共 **300 条**。**覆盖全部 14 个 ATT&CK tactic**：最薄 reconnaissance 20 / resource-development 20，其余在 23–33（defense-evasion、privilege-escalation 因多 technique 共享该 tactic 而自然偏高）；难度 easy 63 / medium 151 / hard 86，hard 占比 ~29%。
- 字段：`id, text, techniques, tactics, difficulty, rationale, tags`。每条 `rationale` 逐个说明各 technique 的映射理由。详见 [docs/taxonomy.md](docs/taxonomy.md)。
- 技术编号合法性以 `ref/attack_ids.txt`（attack.mitre.org Enterprise 快照）校验；`ref/tech_tactics.json` 提供 technique→tactic 映射。

## 评测方法
让被测模型对每条 `text` 输出 `{id, techniques:[...]}`，然后：
```bash
python3 scripts/score.py your_predictions.jsonl
```
指标：technique 级 / 顶层技术级 的 micro Precision / Recall / F1。

## 关键词基线（自带论点）
朴素「关键词→技术」映射（`baselines/keyword_map.py`）跑全集 300 条：

```json
{ "technique_micro":     {"precision": 0.31,  "recall": 0.042, "f1": 0.074},
  "top_technique_micro": {"precision": 0.448, "recall": 0.061, "f1": 0.107} }
```

**看点**：朴素关键词映射 **technique 召回仅 ~0.04**——直白措辞还能蹭对几个，稍一改写、或一句话含多技术就全漏。**光靠关键词对不齐 ATT&CK**，这正是需要专门评测、并上更强模型的理由。

## 跑真实模型（排行榜）
```bash
export OPENAI_API_KEY=sk-...     # 任意 OpenAI 兼容端点：OpenAI / DeepSeek / Qwen / 本地 vLLM
python3 scripts/run_model.py --model <模型名> [--base-url <端点>]
python3 scripts/score.py predictions_<模型名>.jsonl
```

| 模型 | technique F1 | top-technique F1 | 备注 |
|---|---:|---:|---|
| keyword baseline | 0.074 | 0.107 | 规则映射，作下限 |
| doubao-1-5-pro-32k | 0.408 | 0.577 | 火山引擎，2025-01 |
| glm-4-plus | 0.300 | 0.431 | 智谱，2024 |

## 质量保证
`scripts/check_bench.py` + CI 每次提交校验：schema 严格、**每个技术编号必须在官方快照内**、techniques↔tactics 一致、去重、纯净度（**只标技术，不标国家/APT 归因**）。**禁止靠删难例或放宽 gold 骗过校验。**

## 许可
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。立场：纯防御 / 检测工程 / 威胁情报研究。

相关作品：[cybersec-qa-dataset-zh](https://github.com/uninhibited-scholar/cybersec-qa-dataset-zh) · [agent-safety-bench-zh](https://github.com/uninhibited-scholar/agent-safety-bench-zh) · [defensive-refusal-bench-zh](https://github.com/uninhibited-scholar/defensive-refusal-bench-zh) · [zh-function-calling-bench](https://github.com/uninhibited-scholar/zh-function-calling-bench)
