# TelyClaw Growth Engine

将选定 X 账号的讨论转化为有来源依据的内容机会，完成 **发现 → 理解 → 排序 → 创作 → 审批 → 手动发布 → 衡量 → 学习**。这是可本地运行的单用户 MVP，不依赖付费 API；中文界面默认开启，可切换 English。

**提交版本：`feat/evidence-led-content`。** 此分支包含最近验证的修复；准备交付时 PR #7–#9 尚未合入 `main`，请使用此分支或配套源码 ZIP。实际版本以 ZIP 内的 `SOURCE_VERSION.txt` 为准。不要用交付包覆盖已有项目或 `data/growth.db`。

## 快速运行（macOS / Linux）

需要 Python 3.11+，推荐 3.12。解压源码 ZIP，终端进入包含本 README 的项目文件夹，逐行执行：

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

浏览器打开 **http://localhost:8000**，保持终端运行；Control+C 停止。首次安装依赖需要网络，Demo 分析和本地内容生成不需要 API 密钥或外部请求。SQLite 自动创建于 `data/growth.db`，重启后记录保留；更新时务必保留该文件。

## Product Logic｜产品逻辑与演示

1. **数据源与监控设置**：配置至少 5 个账号；可逐条粘贴 X 原帖链接、作者、全文、时间和可选互动指标。输入校验、重复检查及持久保存已实现，不会抓取 X。
2. **趋势机会**：选择数据模式和最近 1H / 4H / 24H / 7D，分析后查看话题、来源、评分和最多 3 个值得跟进的机会。
3. **内容工作室**：生成三个内容角度及英文 X 初稿，人工编辑、保存并批准；修改批准稿会撤销审批。
4. **发布与衡量**：批准后可导出 TXT，或“在 X 中打开”预填编辑器。由用户在 X 确认发布，再登记真实链接/时间；在内容表现页录入和更新实际观察到的累计指标。

干净安装会提供 **6 个虚构账号、48 条合成帖子**，适合直接演示。先用 Demo 的 1H、4H 展示筛选，再演示生成、编辑、审批、TXT 导出。真实手动导入、JSON 导入、Demo 与 Live 数据模式分开；源码不附带候选人本地数据库、真实导入数据或任何发布效果。只有实际发布后才登记发布记录，未获得的指标留空。

## System Architecture｜系统架构

`HTML / CSS / JavaScript → FastAPI JSON API → SQLite + scikit-learn → 本地模板 / 可选 OpenAI`

一个 Python 服务同时提供网页和 API，无需前端构建、Docker 或独立数据库。`trends.py` 负责检测/评分，`semantics.py` / `topic_quality.py` 负责领域概念和证据洞察，`content.py` 负责内容生成，`publishing.py` 负责发布登记及指标计算；`manual.py` / `x_api.py` 负责不同来源接入。API 文档：http://localhost:8000/docs。

## Trend Detection Logic｜趋势检测逻辑

对启用账号及所选时间窗口内的帖子去重、规范化，用领域同义词规则、TF-IDF 词组/字符相似度及平均链接聚类识别共同讨论，不预设话题数量。具体概念支持跨措辞匹配；泛化的 AI / agent / workflow 词本身不足以合并。系统生成主题名称、摘要和来源支持的共同洞察，保留原文、账号、时间、可用指标和链接供复核。

**话题聚合不等于上升趋势。** 只有当前和前一个等长窗口均具备足够帖子、独立账号和时间跨度时才计算样本内讨论量变化；否则显示“历史数据不足”。手选样本不代表全平台共识。

## Opportunity Ranking Logic｜机会排序逻辑

按话题簇评分，基础权重为：**相关性 30%、趋势增速 25%、互动质量 15%、独立账号广度 15%、内容机会 10%、新鲜度 5%**。缺失维度不当作零或编造正分，而是排除并重新归一化其余权重；互动指标不完整时不计该维度。单账号互动分折减，多帖来自同一账号不算独立确认。

展示分项分数、为什么值得关注、与 TelyClaw 的关联及建议内容动作。评分是可解释的编辑启发式，不是增长预测；品牌受众、定位和关键词可配置，默认定位仍是待核实假设。

## Content Generation Logic｜内容生成逻辑

默认明确标为 **本地编辑模板，未使用大语言模型**。根据支持帖中的具体问题分别生成 **Hot Take / Opinion、Educational / Insight、TelyClaw Product Angle**：提出取舍、设计具体检查和衡量方法、连接受众与品牌编辑定位。初稿给出原创编辑观点及可执行建议，不机械比较关键词，不把来源主张当成已验证结果或 TelyClaw 产品能力。

可选 OpenAI 适配器仅在服务器配置 `OPENAI_API_KEY` 时启用，明确标注 LLM，并接受来源和编辑提纲；真实 API 尚未验证。免费演示请保持该变量未配置、`X_LIVE_ENABLED=false`。所有草稿必须人工审核，沿用 **1–280 ASCII 字符、无链接** 的保守规则；中文界面不会自动翻译英文草稿。不会自动发布。

## Growth Measurement｜增长衡量

北极星指标是 **Qualified Engagement Generated from Trends**，MVP 代理指标为每篇趋势内容的合格互动。需与 TelyClaw 明确受众资格和事件规则；普通浏览、点赞或批准稿不自动等于合格互动。

内容表现页支持真实累计指标和历史快照：可用点赞＋转帖＋回复＋收藏为已衡量互动量；有展示量时，互动率＝已衡量互动量 ÷ 展示量 × 100%。缺项标为未衡量/部分数据；汇总仅取每篇最新快照。点击、主页访问和有可靠依据的本帖归因关注者单列，账号整体涨粉不能当成本帖归因。

## AI / Vibe Coding Tools｜使用工具

开发使用 **OpenAI Codex**；本地 NLP 使用 **scikit-learn**；可选内容模型为 **OpenAI API**。默认内容生成不使用 LLM，没有声称完成真实 API 验证或产生已证实的增长效果。

## Validation & Limitations｜验证与限制

- 最近运行结果：**147 项 pytest 测试、6 组 Chromium 浏览器流程通过**，包含编辑/审批/导出、发布登记、指标更新与重启保留；有一条现存 TestClient 依赖弃用警告。测试使用隔离的测试数据，X / LLM 请求均为 mock，没有消耗付费额度。详见 [验证报告](docs/VALIDATION.md)。
- 聚类是英语领域规则辅助的本地方法，仍可能误分或漏分；模板可能重复，不能代替事实核查或人工判断。TelyClaw 实际定位需确认。
- Live X 已实现官方 API 按需拉取、缓存与请求保护，**默认禁用、未验证真实权限/额度**；不是流式监控。生产监控还需正式授权/额度、分页、覆盖率及保留策略、任务调度和运维。自动发布、自动采集表现数据尚未实现。
- 发布和指标为用户手动确认，未由 X API 核验；没有证明因果增长或 10× 结果。当前无登录、多租户或公网部署加固，适用于 localhost 演示。
- **最终交付仍待：3–5 分钟演示视频，以及第 7 页被遮挡文字的招聘方确认。** 不推测缺失要求内容。

完整配置、macOS 证书故障排查、算法公式与生产接入说明见 [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)。[源码分支](https://github.com/cloriszhu1234-create/telyclaw-growth-engine/tree/feat/evidence-led-content) 为私有仓库；向评审提交仓库链接前需授予其访问权限，或直接提交源码 ZIP。开发测试：安装 `requirements-dev.txt` 后运行 `python -m pytest -q`；浏览器测试命令见验证报告。
