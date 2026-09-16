# 行为评测

[cases.json](cases.json) 是任务与判据，不是测试结果。覆盖入口选择、独立使用、证据边界、模型版本、质量验收和商业交接。

## 运行

1. 安装待测 Skill。用全新 Agent 会话运行每条 `prompt`，只提供该用例需要的材料；不要把判据交给执行者。
2. 保存 Agent 输出、工具调用和实际可见输入，并记录 Agent / 模型 / Skill 版本。
3. 对照 `must` 和 `must_not` 人工或独立评审。检查行为和交付内容，不只匹配词语。
4. 每项记录 `pass / fail / not_run` 与输出证据。涉及音视频、生成账号或投放数据而未提供时，只评估如何处理缺口。
5. 报告总用例数、已执行数、通过数和失败数；缺失结果保留 `not_run`，不计入通过。

建议记录格式：

```json
{
  "case_id": "route-ready-storyboard",
  "skill_version": "0.2.0",
  "agent": "实际执行环境",
  "status": "not_run",
  "output_path": null,
  "evidence": [],
  "notes": ""
}
```

`python3 scripts/skills.py validate` 只检查用例结构和技能覆盖。`tests/` 测试安装、打包、引用及失败恢复；这些均不证明视频质量、客户收益或投放效果。公开案例目前为合成示例。
