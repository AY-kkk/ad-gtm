# 贡献指南

本文件规定 Skill、模型适配、案例与评测用例的提交要求。

## 新增 Skill

只有在存在独立任务、输入输出和验收标准时新增模块。摄影方法、文案结构等辅助资料放入对应 Skill 的 `references/`，不要为增加数量拆成空壳入口。

1. 在 `skills/<name>/` 创建 `SKILL.md`，描述触发、输入、步骤、输出、边界和完成标准。
2. 必要参考与模板保存在模块内部，确保单独复制后可用。其他 Skill 只能作为可选交接，不能成为隐藏文件依赖。
3. 添加 `agents/openai.yaml` 和 `registry/skills.json` 条目，按用途加入安装组合。
4. 更新首页地图，并在 `evals/cases.json` 增加典型与易混淆任务。
5. 运行校验和测试后提交 Pull Request，说明解决的任务与验证范围。

## 模型与案例

模型能力注明官方来源、核验日期、服务、区域及完整模型 ID。制作建议、官方文档、账号可用性和实际结果分开描述。

教学案例标为合成；实测案例附输入范围、尝试与失败、结果和成本口径。不得上传客户私有资料、密钥、未授权素材或无法公开的结果。新增模型适配不复制广告策略和 GTM 逻辑。

## 检查

```bash
python3 scripts/skills.py validate
python3 -m unittest discover -s tests -v
python3 scripts/skills.py build --pack all --output dist
```

结构测试不代替行为验证。用行为用例在目标 Agent 中运行，保存实际输出与判断依据；没有执行时将状态保留为 `not_run`。不要提交本机路径、内部讨论或无依据的效果承诺。
