# 标注规范 · taxonomy

- **techniques**：ATT&CK Enterprise 技术/子技术编号（如 `T1059.001`）。多标签，按文本中明确体现的行为标注，不臆测未提及的技术。
- **tactics**：由 techniques 推出（见 `ref/tech_tactics.json`），表示该样本涉及的战术阶段。
- **difficulty**：easy=单/双技术且措辞直白；medium=多技术或需少量推断；hard=多技术、跨阶段或需较强领域推断。
- **只标技术，不标归属**：严禁标注国家/APT 组织归因。
- 编号合法性以 `ref/attack_ids.txt` 快照为准（来源 attack.mitre.org Enterprise）。
