# 模型配置

## 选择版本

广告受众、主张、CTA 和验收口径共用；镜头长度、素材编排和修改方式按版本适配。

- [Seedance 2.0](seedance-2.0.md)：以短段和模块化镜头组织制作。
- [Seedance 2.5](seedance-2.5.md)：可考虑较长连续演示和更多参考素材，仍按复杂度拆镜。

这些是制作建议，不是两个版本的效果排名。版本选择依据当前服务能力和同任务试点，不能仅按版本号推断成本或质量。

## 运行配置

生成前记录以下信息，制作计划可将未知值标为 `unknown`：

| 字段 | 内容 |
| --- | --- |
| provider / service / region | 厂商、产品入口、区域 |
| model_id | 实际完整模型 ID |
| mode | 生成、参考、编辑或延长 |
| capabilities | 当前模式允许的时长、画幅、分辨率、输入数量与格式 |
| asset_mapping | 内部素材 ID、上传顺序及服务引用标记 |
| capability_source / checked_at | 官方文档链接、核验日期 |
| account_status | `unknown`、`available` 或 `unavailable`，附控制台或请求依据 |
| budget / retry_limit | 费用上限、尝试次数和停止条件 |

能力限制必须落在具体入口、版本与模式上。官方页面有矛盾时，不猜参数；继续做无依赖的创意规划，在提交前核对实际服务文档或账号返回。

## 文档快照

核验日期：2026-09-16。以下仅适用于 [BytePlus LAS Enhanced Video Generation](https://docs.byteplus.com/en/docs/Byteplus_LAS/video_gen_enhanced)，区域 `ap-southeast-1`。

| 项目 | Seedance 2.0 | Seedance 2.5 |
| --- | --- | --- |
| 模型 ID | `dreamina-seedance-2-0-260128` | `dreamina-seedance-2-5-260628` |
| 单次输出时长 | 4–15 秒 | 4–30 秒 |
| 输出分辨率 | 480p、720p、1080p、4k | 480p、720p |

该入口的 2.0 参考图片场景不支持 1080p。服务包含前后处理，上表不能解释为模型原生能力；也不能直接用于其他区域、即梦或火山方舟。账号权限、当前限制与费用需在执行时确认。

## 对比与版本更新

同一 brief、产品事实、交付规格和成本范围下比较版本。允许使用各版本适合的提示词与拆段方式，保存差异。若要隔离模型差异，再安排相同输入的受控测试。

比较商品一致性、动作准确性、合格率、完整制作周期、合格成片成本与人工修改量。更新模型 ID 或服务入口后，用原验收任务复查这些指标；未运行的数据保持 `not_run`。
