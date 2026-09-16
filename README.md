# Ad GTM

面向品牌视频广告与视频模型商业化的 Agent Skill，提供从创意、分镜到素材测试与客户 PoC 的工作方法，包含 Seedance 2.0 和 2.5 制作指南。

## 能做什么

| 任务 | 交付物 |
| --- | --- |
| 产品广告创作 | 受众与卖点梳理、广告结构、分镜、提示词、参考素材分工 |
| 广告改版 | 开头、演示或 CTA 变体，以及对应测试计划 |
| Seedance 制作规划 | 分版本镜头方案、服务能力核验、后期与失败处理建议 |
| 视频模型客户试点 | 客户需求诊断、PoC 验收表、成本对照、扩量决策 |

本包是指令与模板库，无运行依赖，不内置视频生成、剪辑或广告投放客户端。实际执行需要所在 Agent 环境提供相应工具和账号。模板不代表已经验证的投放效果。

## 安装

将仓库完整复制到支持 `SKILL.md` 的 Agent 的技能目录，并将文件夹命名为 `ad-gtm`。Codex 默认位置为 `~/.codex/skills/ad-gtm`；若设置了 `CODEX_HOME`，使用其下的 `skills/ad-gtm`。目标目录已有内容时先备份。

Codex 默认目录的安装命令：

```bash
git clone https://github.com/AY-kkk/ad-gtm.git ~/.codex/skills/ad-gtm
```

安装后在新的会话中使用 `$ad-gtm`，也可直接提出匹配的广告或 PoC 任务。

## 使用示例

```text
用 $ad-gtm 为这款桌面收纳盒制作 15 秒竖屏广告方案。
目标受众是居家办公者，产品图片和使用步骤见附件。
使用 Seedance 2.0，先输出分镜和提示词，核心信息是物品分类摆放。
```

```text
用 $ad-gtm 将现有广告改成三个不同开头，正文与 CTA 保持一致。
使用 Seedance 2.5 制作，列出参考素材分工、需保留的内容和验收项。
```

```text
用 $ad-gtm 为电商素材团队设计视频模型 PoC。
比较现有制作方式与 Seedance 2.0、2.5，评估交付质量、制作周期与合格素材成本。
```

尽量提供产品事实、目标人群、素材、渠道、时长、CTA 和预算。客户试点另需现有制作流程、基线数据、验收人和决策节点；缺少的信息会列为待确认项。

## 内容

- [Skill 入口](SKILL.md)：任务路由与执行原则。
- [广告结构](references/ad-patterns.md)与[视觉方法](references/visual-methods.md)：说服顺序与镜头设计。
- [模型配置](references/models.md)：服务入口核验及 Seedance 版本选择。
- [质量与实验](references/quality.md)：成片验收、测试与成本口径。
- [GTM](references/gtm.md)：客户诊断、PoC 与扩量。
- [创作模板](assets/creative-plan.md)与[试点模板](assets/pilot-scorecard.md)：可直接用于项目交付。

## 许可

[MIT](LICENSE)。项目为独立制作的工作方法与模板，不隶属于模型厂商。模型服务及用户提供的素材适用各自的条款与许可。
