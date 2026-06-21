# 计划书：attack-bench-zh
## 中文 · 威胁情报文本 → ATT&CK 技术编号 标注映射集（可机器评分）

> 交付给执行 agent 的自包含规格书，冷启动可执行。出品人 GitHub: uninhibited-scholar。
> 语言：中文为主，schema/代码用英文。立场：纯防御 / 检测工程 / 威胁情报研究。

## 0. 目标
给一段中文威胁情报 / 安全事件描述，标注它对应的 ATT&CK 技术编号（如 `T1059.001`、`T1566.002`）。
产出：标注数据 + 自动评分器 + 规则基线 + 排行榜，发布到 GitHub / HF / 魔搭。
**核心卖点**：ATT&CK 编号是封闭词表 → 评分是 exact/partial match，**零主观、CI 可担保**。

## 第 0 步（必做）：prior-art 核实
检索 CTI-REALM、TRAM(MITRE)、ATT&CK 官方、CyberPal.AI、CTI→ATT&CK 相关 2026 论文。
产出 `docs/prior-art.md`：列同类的语言/任务/是否开源标注/差异。明确本项目差异化 = **中文 + 开源标注 + 上游 technique 映射（非下游规则生成）**。撞车则停、报告出品人。

## 1. v0 范围（目标 2 周）
- 规模：300–500 条（v0），可扩 1000+。
- 任务：输入中文威胁描述 → 输出 `techniques: [T-id...]`（多标签）。
- 难度：easy（单技术、措辞直白）/ medium / hard（多技术、需推断）。
- 覆盖：尽量覆盖 ATT&CK 14 个 tactic，避免只堆 execution/persistence。

## 2. 数据 schema（严格）
```json
{
  "id": "cti-0007",
  "text": "攻击者通过钓鱼邮件投递带宏的 Office 文档，用户启用宏后执行 PowerShell 下载后续载荷。",
  "techniques": ["T1566.001", "T1204.002", "T1059.001"],
  "tactics": ["initial-access", "execution"],
  "difficulty": "medium",
  "rationale": "钓鱼附件=T1566.001；用户执行=T1204.002；PowerShell=T1059.001。",
  "tags": ["phishing", "macro", "powershell"]
}
```
- 顶层键严格为：`id, text, techniques, tactics, difficulty, rationale, tags`。
- `techniques` 至少 1 个，元素必须是合法 ATT&CK 技术/子技术 ID。
- `tactics` 由 techniques 推出（用官方 technique→tactic 映射校验一致）。

## 3. 评分器 `score.py`（灵魂）
让被测模型对每条输出 `{id, techniques:[...]}`，评分：
- **technique 级**：micro / macro Precision / Recall / F1（多标签集合比对）。
- **tactic 级宽松分**：technique 错但 tactic 对算半分（容忍子技术粒度误差）。
- **顶层技术命中率**：只看主技术 `Txxxx`（忽略子技术后缀）的 F1。
纯标准库、零依赖、确定性、CI 可跑。输出 `report.json`。

## 4. 校验 `check_bench.py` + CI（反 Goodhart）
- 每条合法 JSON、schema 严格、键完整；
- **每个 technique ID 必须存在于官方 ATT&CK 编号表**（仓库内置一份 `attack_ids.txt` 快照；非法 ID → 红灯）；
- techniques 与 tactics 一致性校验；
- 无重复 id、无重复 text；难度/ tactic 分布非空；
- 纯净度：复用网安数据集规则，禁国家归因 / 命名 APT / 地缘（**只标技术，不标"谁干的"**）。

## 5. 基线（自带论点）
关键词/正则映射当 baseline（如"PowerShell"→T1059.001），跑全集，报告 F1。
预期：直白样本还行，hard 样本召回低 → 证明"光靠关键词映射 ATT&CK 不靠谱"，即本基准存在的理由。

## 6. 仓库结构
```
attack-bench-zh/
  README.md  PLAN.md  LICENSE(CC BY 4.0)
  data/bench.jsonl
  ref/attack_ids.txt           # 官方技术编号快照（来源、版本号写明）
  scripts/score.py  scripts/check_bench.py
  baselines/keyword_map.py  baselines/predictions_keyword.jsonl
  docs/prior-art.md  docs/taxonomy.md
  .github/workflows/validate.yml
```

## 7. 验收标准（机器可判定的"完成"）
1. `data/bench.jsonl` ≥ 300 条，`check_bench.py` 全绿（含 ID 合法性）；
2. `score.py` 能对示例预测产出完整 `report.json`；
3. 关键词基线结果写入 README（≥3 个指标）；
4. `docs/prior-art.md` 完成、差异化明确；
5. CI 绿；README 含一键 `load_dataset` + 诚实来源说明（哪些 LLM 生成、哪些人工校验，不夸大；尤其"techniques 由谁标、是否人工复核"要写清）。

## 8. 给执行 agent 的红线
- 只标"用了什么技术"，**绝不**标国家/组织归因。
- text 改写自公开来源，不得含针对真实目标的可直接实施载荷。
- 不确定某条该标哪个 technique → 记入 `docs/open-questions.md`，交出品人裁决，别硬塞。
- 每个里程碑跑 CI，红灯先修。

## 9. 里程碑
M1 prior-art + taxonomy + 官方 ID 快照导入。
M2 schema + check_bench + score + 30 条种子（端到端跑通）。
M3 扩到 300+、关键词基线、CI 绿。
M4 README/排行榜/诚实声明，发布 HF + 魔搭。
