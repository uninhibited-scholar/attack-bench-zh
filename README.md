# attack-bench-zh

中文 · 威胁情报文本 → ATT&CK 技术编号 标注映射集（可机器评分，防御导向）。

[![CI](https://github.com/uninhibited-scholar/attack-bench-zh/actions/workflows/validate.yml/badge.svg)](https://github.com/uninhibited-scholar/attack-bench-zh/actions/workflows/validate.yml)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-green.svg)](https://creativecommons.org/licenses/by/4.0/)

给一段中文威胁/事件描述，标注其对应的 ATT&CK 技术编号（如 `T1059.001`）。**ATT&CK 编号是封闭词表 → 评分为 exact / partial match，零主观、CI 可担保。** 是检测工程的**上游**（先定 technique，才谈检测规则），与下游规则生成基准（如 CTI-REALM）互补。

> 现状诚实定位：**v0 种子集 36 条、单人标注、关键词基线**——一个**能跑通、有论点、可复现**的早期基准（占位 + 方法验证），尚非大规模权威基准；规模化与多模型基线见 [PLAN.md](PLAN.md)。

## 数据
- `data/bench.jsonl`，v0 共 **36 条**（目标扩至 300+）。覆盖 50 个 ATT&CK 技术、14 个 tactic 大部分阶段；难度 easy/medium/hard。
- 字段：`id, text, techniques, tactics, difficulty, rationale, tags`。详见 [docs/taxonomy.md](docs/taxonomy.md)。
- 技术编号合法性以 `ref/attack_ids.txt`（attack.mitre.org Enterprise 快照）校验。

## 评测方法
让被测模型对每条 `text` 输出 `{id, techniques:[...]}`，然后：
```bash
python3 scripts/score.py your_predictions.jsonl
```
指标：technique 级 / 顶层技术级 / tactic 级 的 Precision / Recall / F1。

## 关键词基线（自带论点）
朴素「关键词→技术」映射（`baselines/keyword_map.py`）跑全集：

```json
{
  "technique_precision": 0.780, "technique_recall": 0.582, "technique_f1": 0.667,
  "top_technique_f1": 0.690, "tactic_f1": 0.711
}
```

**看点**：关键词映射 precision 尚可（0.78）但 **recall 仅 0.58**——大量"需跨阶段推断、或一句话含多个技术"的样本被漏标。**光靠关键词对不齐 ATT&CK**，这正是需要专门评测、并上更强模型的理由。

## 质量保证
`scripts/check_bench.py` + CI 每次提交校验：schema 严格、**每个技术编号必须在官方快照内**、techniques↔tactics 一致、去重、纯净度（**只标技术，不标国家/APT 归因**）。**禁止靠删难例或放宽 gold 骗过校验。**

## 许可
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。立场：纯防御 / 检测工程 / 威胁情报研究。

相关作品：[cybersec-qa-dataset-zh](https://github.com/uninhibited-scholar/cybersec-qa-dataset-zh) · [agent-safety-bench-zh](https://github.com/uninhibited-scholar/agent-safety-bench-zh) · [defensive-refusal-bench-zh](https://github.com/uninhibited-scholar/defensive-refusal-bench-zh) · [zh-function-calling-bench](https://github.com/uninhibited-scholar/zh-function-calling-bench)
