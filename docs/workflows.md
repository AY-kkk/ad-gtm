# 工作流与交接

## 品牌广告

| 阶段 | 输入 | Skill | 交付给下一阶段 |
| --- | --- | --- | --- |
| 需求 | 产品资料、目标人群、传播目标 | ad-brief | brief、主张证据、素材权利 |
| 创意 | brief 与可用主张 | ad-creative | 脚本、创意 ID、变体与固定项 |
| 分镜 | 脚本、素材、规格 | ad-storyboard | 时间轴、素材分工、声音与后期 |
| 模型制作 | 分镜与实际账号条件 | ad-seedance-20 或 ad-seedance-25 | 任务、配置、结果与消耗 |
| 验收 | 文本或实际音视频、验收要求 | ad-review | 范围明确的检查结果与返工项 |
| 实验 | 成片、流量条件与真实数据 | ad-experiment | 实验结果、限制与下一轮假设 |

## 模型商业化

| 阶段 | 输入 | Skill | 交付给下一阶段 |
| --- | --- | --- | --- |
| 诊断 | 访谈、现有流程和资料 | ad-discovery | 优先场景、基线、角色与未知项 |
| 试点 | 场景、样本、资源与验收人 | ad-poc | 对照设计、质量周期和完整成本 |
| 落地 | 试点结果、报价与采购条件 | ad-scale | 商业范围、里程碑和扩量计划 |

制作与商业化共用记录，避免客户方案采用与样片不同的事实或成本。实际工作不要求跑完所有阶段。

## 交接约定

每次交接仅传需要的内容：

```text
project_id：项目标识
artifact_id / version：当前产物与版本
source_artifacts：使用的输入及版本
facts：已支持的事实与来源
assumptions：创意或商业假设
constraints：用户已确认的范围、预算和禁改项
open_items：影响后续执行的缺口
stage_status：planned / running / completed / blocked
checks：not_run / pass / fail，附依据和检查范围
next_action：下一步及接收者
```

按需关联 `claim_id / asset_id / concept_id / variant_id / shot_id / job_id / experiment_id / pilot_id`。内部素材 ID 必须先映射为服务支持的引用；不能直接把内部编号提交成可识别的模型资源。

## 三个分支

- **已经有分镜：** 直接做模型制作，不重写受众和脚本。
- **没有生成工具：** 交付提示词、配置与后期计划；视频检查保持 `not_run`。
- **PoC 未通过：** 记录失败与成本，缩小范围或调整；不跳到收益承诺和扩量。

专项模块不依赖共享目录或上游 Skill 安装。安装导航与部分模块时，导航只调用当前环境实际可用的模块。
