"use strict";
/* Presentation-only localization. Keys are the English interface copy. Raw
   evidence, handles, drafts and editable/database values are explicitly excluded.
   Text-node originals are retained so a switch never rebuilds forms or loses edits. */
const ZH = {
  "GROWTH WORKSPACE":"增长工作台", "Opportunities":"趋势机会", "Content studio":"内容工作室", "Performance":"内容表现", "Sources & settings":"数据源与监控设置",
  "Growth Lead":"增长负责人", "Candidate workspace":"候选人工作台", "Workspace":"工作台", "Local workspace":"本地工作台", "API docs ↗":"API 文档 ↗",
  "DEMO WORKSPACE":"演示工作台", "LIVE X · CACHED DATA":"实时 X · 缓存数据", "JSON IMPORTS":"JSON 导入", "MANUAL IMPORTS":"手动导入",
  "Fictional accounts, synthetic posts and engagement. No live X connection.":"虚构账号、合成帖子与互动数据。未连接实时 X。",
  "User-imported posts. Accuracy is not independently verified. No live X connection.":"用户导入的帖子，准确性未经独立核实。未连接实时 X。",
  "Manually entered X posts. Text, timestamps and metrics are unverified. No scraping or API requests.":"手动录入的 X 帖子。原文、时间与指标未经核实；不会抓取网页或调用 API。",
  "Official X API cache only. No automatic fetch, no synthetic fallback, no platform-wide trend claim.":"仅使用官方 X API 缓存；不自动获取、不以合成数据兜底，也不代表全平台趋势。",
  "DISCOVER → UNDERSTAND → PRIORITIZE → CREATE":"发现 → 理解 → 排序 → 创作", "Turn signals into your next move.":"从社交信号，找到下一步增长机会。",
  "Discover the conversations worth joining — and give them a TelyClaw perspective.":"发现值得参与的讨论，提出 TelyClaw 的独到视角。",
  "Data source":"数据来源", "Demo Data (synthetic)":"演示数据（合成）", "Live X (manual / cached)":"实时 X（按需获取／缓存）", "Manual Imports":"手动导入", "JSON Imports":"JSON 导入",
  "Monitoring window":"监控时间窗口", "Last 1 hour":"最近 1 小时", "Last 4 hours":"最近 4 小时", "Last 24 hours":"最近 24 小时", "Last 7 days":"最近 7 天", "✳ Analyze signals":"✳ 分析信号",
  "OFFICIAL X API · ON-DEMAND":"官方 X API · 按需获取", "Live account monitoring":"实时账号监控", "NO AUTOMATIC FETCHING":"不自动获取",
  "One account is a source of content signals, not evidence of a platform-wide trend. Fetching may incur X API costs; analyzing the cache does not.":"单个账号只能提供内容信号，不能证明全平台趋势。获取帖子可能产生 X API 费用；分析缓存不会调用 API。",
  "Monitored X username":"监控的 X 用户名", "Posts per request":"每次获取数量", "5 posts (default)":"5 条（默认）", "10 posts":"10 条", "Fetch latest posts":"获取最新帖子", "Inspecting local configuration and cache…":"正在检查本地配置与缓存…",
  "15-minute cache · 10-minute global cooldown · 10 outbound requests per UTC day · First fetch usually uses 2 requests (user ID + posts). No pagination or automatic retries.":"缓存有效期 15 分钟 · 全局冷却 10 分钟 · 每 UTC 日最多 10 次外部请求 · 首次获取通常需要 2 次请求（用户 ID 与帖子）。无翻页或自动重试。",
  "Posts in window":"窗口内帖子", "Filtered to enabled accounts":"仅统计已启用账号", "Active sources":"活跃来源", "Distinct accounts in this run":"本轮独立账号数", "Detected opportunities":"发现的机会", "Evidence-backed topic clusters":"有来源支持的话题聚类",
  "Qualified engagement / post":"每篇帖子的合格互动", "Not measured":"未衡量", "Requires published-post analytics":"需要已发布帖子的效果数据", "Trend radar":"AI 趋势雷达", "TOP OPPORTUNITIES":"最值得跟进的机会", "Ranked by relevance, signal strength and timing.":"综合相关性、信号强度与时效性排序。", "Ready to analyze":"等待分析",
  "Analyze signals to discover opportunities.":"点击分析信号，发现内容机会。", "Select a trend to inspect its evidence and score.":"选择话题，查看来源证据与评分。",
  "Local topic synthesis · Transparent scoring · Human judgment at every publishing decision":"本地话题综合分析 · 透明评分 · 每次发布均由人工决策",
  "FROM OPPORTUNITY TO ORIGINAL CONTENT":"从趋势机会到原创内容", "Shape the idea. Check the claims. Approve when it’s ready.":"打磨观点、核实论据，准备好后再批准。", "Generate a draft from a trend to begin.":"从趋势话题生成草稿，开始创作。",
  "PUBLISH → MEASURE → LEARN":"发布 → 衡量 → 学习", "Content performance":"内容表现", "Record real outcomes from manually published posts. Unknown metrics stay unmeasured.":"记录手动发布帖子的真实效果。缺失指标保留为未衡量。", "All aggregate outcomes and coverage":"汇总效果与数据覆盖范围", "Performance by topic":"按话题查看表现",
  "No published posts yet. Approve a draft, publish it yourself in X, then record its actual URL in Content Studio.":"暂无已发布帖子。先批准草稿，再前往 X 手动发布，并在内容工作室登记真实链接。",
  "BETTER INPUTS, BETTER OPPORTUNITIES":"更好的信号，带来更好的机会", "Curate your listening list and make relevance explicit.":"配置监控清单，明确品牌相关性。", "Monitored accounts":"监控账号", "Demo handles are fictional. Imported accounts are added automatically.":"演示账号为虚构账号；导入帖子时会自动添加作者账号。", "X handle without @":"X 用户名（不含 @）", "Add account":"添加账号", "Remove":"移除", "No accounts. Add an account to begin.":"暂无账号，请先添加。",
  "Brand brief":"品牌简报", "Provisional until TelyClaw confirms its positioning. Changes apply to new analyses.":"品牌定位有待 TelyClaw 确认。修改仅用于后续分析。", "Positioning & editorial guardrails":"品牌定位与内容边界", "Audience":"目标受众", "Relevance keywords (comma separated)":"相关性关键词（英文逗号分隔）", "Save brand brief":"保存品牌简报",
  "NO API ACCESS NEEDED":"无需 API 权限", "Import X Post":"导入 X 帖子", "Copy a post yourself and save it locally. This form never opens, scrapes or fetches the URL. Source details are user-supplied and unverified.":"自行复制帖子并保存到本地。本表单不会打开、抓取或请求链接；来源信息由用户提供，未经独立核实。",
  "Original X post URL":"原始 X 帖子链接", "Author’s X handle":"作者的 X 用户名", "Full post text":"完整帖子原文", "Paste the full text, without adding your own commentary":"粘贴完整原文，请勿加入个人评论", "Publication date and time (Asia/Shanghai, UTC+08:00)":"发布时间（上海，UTC+08:00）", "Likes (optional)":"点赞数（选填）", "Reposts (optional)":"转帖数（选填）", "Replies (optional)":"回复数（选填）", "Unknown":"未知",
  "Leave unavailable counts blank; enter 0 only when the post actually shows zero. Convert the publication time to UTC+08:00 before entering it.":"无法获取的指标请留空；仅在真实数值为零时填写 0。请先将发布时间换算为 UTC+08:00。", "Save Post":"保存帖子", "Recent manual imports":"最近手动导入的帖子",
  "Import posts (JSON)":"导入帖子（JSON）", "Upload JSON with a":"上传 JSON 文件，包含", "array. Up to 1,000 posts; timezone-aware dates required. Imported data stays separate from synthetic data.":"数组。最多 1,000 条，日期必须包含时区。导入数据与合成数据相互独立。", "Choose JSON file":"选择 JSON 文件", "Import dataset":"导入数据集", "View import format":"查看导入格式",
  "THE GROWTH LOOP":"增长闭环", "Optimize for useful attention.":"让关注转化为有价值的互动。", "Trends → Content → Attention → Engagement → Growth":"趋势 → 内容 → 关注 → 互动 → 增长", "The North Star is":"北极星指标：", "Qualified Engagement Generated from Trends":"由趋势内容带来的合格互动", ": meaningful replies, reposts, bookmarks, profile visits, qualified followers and product clicks.":"：有价值的回复、转帖、收藏、主页访问、目标受众关注与产品点击。",
  "Use tagged links and a consistent measurement window after manual publishing. Source-post likes are signals, not results from your content.":"手动发布后，使用带追踪参数的链接和统一的衡量窗口。来源帖子的点赞只是信号，并非你的内容效果。", "PAGE 7: PENDING RECRUITER CLARIFICATION":"第 7 页遮挡文字：等待招聘方澄清",
  "Cached posts for selected username":"所选用户的缓存帖子", "Scenario clock:":"演示场景时间：", "Current time · imported posts":"当前时间 · 导入帖子", "Current time · cached X posts":"当前时间 · X 缓存帖子",
  "Manually selected posts form a limited, unverified sample. Analyze to check coverage for the selected time window.":"手选帖子只是有限且未经核实的样本。运行分析可查看当前时间窗口的数据覆盖情况。",
  "Fetching manually from X… No automatic retry will run.":"正在按需获取 X 帖子… 不会自动重试。", "Any existing X cache is preserved; no demo data was substituted.":"现有 X 缓存已保留，未替换成演示数据。", "Click Analyze signals to use the cache.":"点击分析信号，使用缓存数据。",
  "Selection changed. Analyze signals to refresh results.":"选择已更改，请重新分析信号。", "Select a trend after analyzing.":"分析后请选择一个话题。", "New analysis required":"需要重新分析", "Analyzing…":"正在分析…", "Run completed ·":"分析完成 ·",
  "No eligible posts in this window. For Live X, fetch manually when access is enabled, then analyze the cache. Otherwise enable accounts, choose a wider window, or import recent data.":"当前窗口内没有符合条件的帖子。实时 X 模式需先获得权限并手动获取，再分析缓存。其他模式可启用账号、扩大窗口或导入近期帖子。", "No topics yet. Adjust your sources or time window.":"暂无话题，请调整数据来源或时间窗口。",
  "Insufficient historical data":"历史数据不足", "Rising in observed sample":"所选样本内讨论量上升", "Flat / falling in observed sample":"所选样本内讨论量持平／下降", "Multi-source confirmation":"多个独立账号支持", "Single-source signal":"单一来源信号", "Manual · unverified":"手动录入 · 未核实", "Original X post ↗":"查看 X 原帖 ↗",
  "Why It’s Trending":"为何值得关注", "Why TelyClaw Should Care":"为何与 TelyClaw 相关", "Recommended Content Move":"建议的内容行动", "Opportunity score":"机会评分", "relevance":"品牌相关性", "momentum":"趋势增长速度（Velocity）", "engagement":"互动表现（Engagement）", "breadth":"独立来源广度", "depth":"原创内容机会", "freshness":"新鲜度", "N/A":"未知／不适用",
  "Weighted heuristic, not a prediction. Relevance uses specific brand keywords and supported domain concepts; generic AI/agent mentions alone earn only limited credit. Available source engagement = observed likes + reposts + replies. Quality scoring is damped for single-account signals. Unknown factors have zero weight; remaining weights rescale.":"此为加权启发式评分，并非预测。相关性参考品牌关键词与具体领域概念；来源互动量为可获得的点赞＋转帖＋回复。单一账号的互动评分会折减。未知维度不参与计分，其余权重重新归一化。",
  "Create angles & draft →":"生成内容角度与草稿 →", "Local editorial templates by default; optional OpenAI configuration. Human approval required.":"默认使用本地编辑模板；可选配置 OpenAI。发布前必须人工审核（Human-in-the-loop）。", "Preparing draft…":"正在准备草稿…", "Three angles and a draft are ready for your review.":"三个内容角度与一篇草稿已就绪，请人工审核。",
  "No drafts yet. Start with the trend radar.":"暂无草稿，请从 AI 趋势雷达开始。", "Discard unsaved draft edits?":"是否放弃尚未保存的草稿修改？", "Synthetic signal":"合成演示信号", "Live X signal":"实时 X 信号", "Manual X signal":"手动导入 X 信号", "Imported signal":"导入信号", "draft":"草稿", "approved":"已批准", "published":"已发布", "Edited":"已编辑",
  "Local editorial templates (evidence-conditioned, no LLM)":"本地编辑模板（结合来源证据，未使用大语言模型）", "OpenAI LLM (human review required)":"OpenAI 大语言模型（需人工审核）", "Three ways into the conversation":"三个切入讨论的内容角度", "Hot Take / Opinion":"鲜明观点／评论", "Educational / Insight":"知识解读／洞察", "TelyClaw Product Angle":"TelyClaw 产品视角", "Your X post":"你的 X 帖子（内容语言独立于界面语言）", "Review claims and positioning before approval":"批准前请核实论据与品牌定位",
  "Draft suggestions are labeled by provider and are not verified TelyClaw product claims. Check the source, add your expertise, and confirm the angle fits your audience. MVP export supports ASCII text without URLs.":"草稿已标明生成方式，不代表已核实的 TelyClaw 产品能力。请检查来源、加入专业判断，并确认符合受众需求。MVP 仅支持不含链接的 ASCII 文本。",
  "Save changes":"保存修改", "Approve post":"批准帖子", "Export approved text ↗":"导出已批准文本 ↗", "Export downloads text for manual publishing. Nothing is posted to X by this application. Editing approved text requires approval again.":"导出文本供手动发布。本应用不会在 X 上发布任何内容。修改已批准文本后需要重新审核。",
  "Publish manually":"手动发布", "Open in X only prepares the composer. Review and confirm publication there, then record the actual post below.":"“在 X 中打开”仅预填编辑器。请在 X 上审核并确认发布，再在下方登记真实帖子。", "Open in X ↗":"在 X 中打开 ↗", "Actual published X post URL":"已发布帖子的真实 X 链接", "Publication time (Asia/Shanghai, UTC+08:00)":"发布时间（上海，UTC+08:00）", "Mark as Published":"登记为已发布", "Publication recorded manually. Add real metrics in Performance.":"已记录手动发布信息。请到内容表现页填写真实指标。",
  "Published · user confirmed":"已发布 · 用户确认", "Published text is preserved. Create a revision to start another human-reviewed draft.":"已发布文本保持不变。创建修订版可开始新一轮人工审核。", "Create revision":"创建修订版", "Unsaved changes · Approval required":"修改尚未保存 · 需要重新审核", "Approved. Export is ready for manual publishing.":"已批准，可导出并手动发布。", "Saved. Any changed text needs fresh approval.":"已保存。修改后的文本需要重新批准。",
  "No manual posts yet. Add posts from different accounts to compare topics.":"暂无手动导入帖子。请添加不同账号的帖子以比较话题。", "Saving locally…":"正在保存到本地…", "Saved locally. Choose Manual Imports and Analyze signals; no X request was made.":"已保存到本地。请选择手动导入并分析信号；未调用 X。", "Account added. Import posts for new handles to analyze them.":"已添加账号。导入该账号帖子后即可分析。", "Account removed. Existing evidence snapshots are preserved.":"已移除账号，已有证据快照保留。", "Brand brief saved. Run a new analysis to apply.":"品牌简报已保存，请重新运行分析。", "Choose a JSON file first.":"请先选择 JSON 文件。", "File must be under 6 MB.":"文件必须小于 6 MB。",
  "Views / impressions":"浏览量／展示量", "Likes":"点赞", "Reposts":"转帖", "Replies":"回复", "Bookmarks":"收藏", "Link clicks":"链接点击", "Profile visits":"主页访问", "Post-attributed followers":"可归因于本帖的新关注者", "Published records":"发布记录", "Total measured engagement":"已衡量的总互动量", "All four counts available":"四项互动数据均可获得", "Partial / unmeasured counts; not qualified by default":"部分指标缺失；不默认视为合格互动", "Engagement rate":"互动率", "Measured impressions":"已衡量的展示量", "Published · manual":"已发布 · 手动登记", "Published X post ↗":"查看已发布 X 帖子 ↗", "Approved published text":"已批准并发布的文本", "Record cumulative metrics":"记录累计指标",
  "Enter actual observed totals, not increments. Blank means Not measured. A new snapshot replaces the previous snapshot for totals; history is kept.":"填写真实观察到的累计值，而非增量。留空表示未衡量。汇总只使用每篇帖子的最新快照，历史记录仍保留。", "Measurement time (Asia/Shanghai, UTC+08:00)":"衡量时间（上海，UTC+08:00）", "Optional outcomes and attribution":"可选效果与归因", "Account-level follower growth is not attributable to this post. Leave post-attributed followers blank unless you have reliable post-level evidence, including for a zero value.":"账号整体粉丝增长不能直接归因于本帖。除非有可靠的帖子级归因证据，否则请留空；填写零也需要证据。", "Attribution evidence (required for post-attributed followers)":"归因证据（填写本帖新增关注者时必填）", "Save measurement":"保存衡量记录", "Latest outcome":"最新效果", "No measurements yet.":"暂无衡量记录。", "Real metric snapshot saved. Aggregates use only the latest snapshot per post.":"真实指标快照已保存。汇总仅使用每篇帖子的最新快照。",
  "Compare topics using consistent measurement windows and audience quality. These observational totals do not prove that a topic caused growth.":"请用一致的衡量窗口和受众质量标准比较话题。观察到的汇总数据不能证明某话题导致了增长。", "No topic outcomes yet. Publication and measurement records will appear here.":"暂无话题效果。登记发布与衡量记录后会显示在此处。",
  "Measured engagement = available likes + reposts + replies + bookmarks. Partial counts are labeled; unknown is not zero. Rate = measured engagement / impressions × 100. Clicks, profile visits and attributed followers are separate outcomes, not added again.":"已衡量互动量＝可获得的点赞＋转帖＋回复＋收藏。缺失指标明确标记，未知不等于零。互动率＝已衡量互动量／展示量×100。点击、主页访问与归因关注者单独统计，不重复计入互动量。",
  "Manual metrics are unverified and are not automatically qualified engagement. Snapshots are cumulative; only the latest per post is aggregated. Account-level follower growth must not be entered as post-attributed followers.":"手动指标未经独立核实，不自动视为合格互动。快照为累计值，汇总仅采用每帖最新快照。不能把账号整体粉丝增长填入本帖归因关注者。",
  "Local multi-document extractive synthesis; attributed source excerpts are not independently verified.":"本地多文档提取式综合摘要；引用原文未经独立核实。",
  "Review the configured brand brief.":"请检查已配置的品牌简报。", "Review source evidence before drafting.":"起草前请检查来源证据。",
  "SYNTHETIC EVIDENCE":"合成演示证据", "LIVE X CACHE":"实时 X 缓存", "MANUAL · UNVERIFIED":"手动导入 · 未核实", "OPPORTUNITY BRIEF":"机会分析", "LOW RELEVANCE":"相关性较低", "SIGNAL":"信号", "TOP":"优先机会",
  "demo":"演示", "manual":"手动导入", "live":"实时 X", "imported":"JSON 导入", "synthetic":"合成数据", "manual_x":"手动 X · 未核实", "live_x":"官方 X 缓存", "user_confirmed_manual_publication":"用户确认的手动发布", "original":"原创帖", "reply":"回复帖", "quote":"引用帖", "repost":"转帖", "also reply":"同时为回复", "also quote":"同时为引用", "Never":"从未获取", "fresh":"有效缓存", "stale or empty":"已过期或为空"
};
Object.assign(ZH,{
  "Multi-Agent Orchestration": "多智能体协作与编排",
  "Agent Frameworks & Interoperability": "智能体框架与互操作性",
  "Agent-Assisted Coding Workflows": "智能体辅助编程工作流",
  "Human Oversight of Agents": "智能体的人工监督与审核",
  "Context & Memory Efficiency": "上下文与记忆效率",
  "Content Measurement & Attribution": "内容效果衡量与归因",
  "Social Listening & Customer Signals": "社交聆听与客户信号",
  "Software Security & Evaluation": "软件安全与评估",
  "Unclassified Discussion": "待分类讨论",
  "Manually entered X posts: source text, dates, authors and metrics are user-supplied and unverified. A hand-selected sample does not establish platform-wide trends.": "手动录入的 X 帖子：原文、日期、作者与指标由用户提供，未经独立核实。手选样本不能证明全平台趋势。",
  "Saved": "已保存",
  "Approved": "已批准",
  "Updated": "更新于",
  "Engagement:": "互动量：",
  "Rate:": "互动率：",
  "(partial / incomplete)": "（部分指标缺失）",
  "(partial / unmeasured)": "（部分指标缺失／未衡量）",
  "Source mode:": "来源模式：",
  "Source:": "来源：",
  "likes": "点赞",
  "reposts": "转帖",
  "replies": "回复",
  "timeline": "时间线",
  "Independent confirmation is limited to the selected accounts, not the X platform.": "独立来源支持仅限所选账号，不代表 X 全平台共识。",
  "Concept evidence & clustering method": "概念证据与聚类方法",
  "No specific domain concept detected; conservative lexical grouping.": "未识别到具体领域概念；采用保守的词语相似度分组。",
  "Local domain-concept vocabulary v1 + word/phrase TF-IDF (80%) + character similarity (20%); specific-concept similarity floor 0.64; average-link threshold 0.31. Generic agent/AI/workflow overlap alone is excluded. No remote model.": "本地领域概念词表 v1＋词语／短语 TF-IDF（80%）＋字符相似度（20%）。共享具体概念时，相似度至少为 0.64；平均链接相似度阈值 0.31。AI、agent、workflow 等泛词重合不构成合并依据。未调用远程模型。",
  "Only English source analysis is supported by the local vocabulary. Interface language does not change draft language.": "本地概念词表主要支持英文来源分析。界面语言不会改变草稿语言。",
  "Enter a valid X handle, with or without @": "请输入有效的 X 用户名，可包含或不包含 @",
  "Full post text cannot be blank": "完整帖子原文不能为空",
  "Publication time must include a timezone": "发布时间必须包含时区",
  "Publication time cannot be in the future": "发布时间不能晚于当前时间",
  "Enter a valid HTTPS X post URL": "请输入有效的 HTTPS X 帖子链接",
  "Use https://x.com/author/status/numeric-post-id (twitter.com links also accepted)": "请使用 https://x.com/author/status/数字ID（也接受 twitter.com 链接）",
  "Author handle must match the handle in the post URL": "作者用户名必须与帖子链接中的用户名一致",
  "Post ID must be a positive integer": "帖子 ID 必须是正整数",
  "This X post has already been manually imported. Its existing text and metrics were kept.": "该 X 帖子已手动导入，原有文本和指标已保留。",
  "Use an HTTPS X post URL": "请使用 HTTPS X 帖子链接",
  "Use https://x.com/author/status/numeric-post-id": "请使用 https://x.com/author/status/数字ID",
  "Timestamp must include timezone": "时间必须包含时区",
  "Timestamp cannot be in the future": "时间不能晚于当前时间",
  "Future post timestamps are not accepted": "不接受未来时间的帖子",
  "Post-attributed followers require a description of reliable attribution evidence; account-level growth is not post attribution": "填写本帖归因关注者需提供可靠的归因证据；账号整体增长不能视为本帖归因",
  "Cross-origin live fetching is not allowed": "不允许跨站点获取实时数据",
  "Record not found": "未找到记录",
  "Choose a supported window and dataset": "请选择支持的时间窗口与数据来源",
  "Topic not found": "未找到话题",
  "AI provider failed. Check server configuration or remove the key to use labeled local templates.": "内容服务调用失败。请检查服务器配置，或移除密钥后使用已标注的本地模板。",
  "Published text is preserved. Create a revision to edit a new draft.": "已发布文本保持不变。请创建修订版编辑新草稿。",
  "Draft must be 1–280 ASCII characters without URLs": "草稿须为 1–280 个 ASCII 字符，且不能含链接",
  "Draft cannot be blank": "草稿不能为空",
  "This MVP validates plain ASCII posts without URLs; simplify the text before approval.": "此 MVP 仅验证不含链接的 ASCII 文本；批准前请简化文本。",
  "Human approval required before export": "导出前必须完成人工批准",
  "Draft not found": "未找到草稿",
  "Save and approve the current draft before opening X": "请先保存并批准当前草稿，再打开 X",
  "Only an approved, unpublished draft can be marked published": "仅可将已批准且尚未发布的草稿登记为已发布",
  "That X post or draft already has a publication record": "该 X 帖子或草稿已有发布记录",
  "Publication not found": "未找到发布记录",
  "Measurement must be at or after publication": "衡量时间不能早于发布时间",
  "Enter a measurement timestamp at or after the latest snapshot": "衡量时间不能早于最新快照",
  "Keywords must contain 1–60 characters": "每个关键词须为 1–60 个字符",
  "Please fill out this field.": "请填写此字段。",
  "Please enter a URL.": "请输入有效链接。",
  "Please match the requested format.": "请按要求的格式填写。",
  "Please enter a number.": "请输入数字。",
  "Value error, ": "数值错误：",
  "Add X_BEARER_TOKEN to your private server .env, then restart. No X request was made.": "请在服务器私有 .env 中设置 X_BEARER_TOKEN 并重启。未发送 X 请求。",
  "Live fetching is off. With $0 credits, keep X_LIVE_ENABLED=false. Enable locally only after confirming X access and credits.": "实时获取已关闭。余额为 $0 时请保持 X_LIVE_ENABLED=false。仅在确认权限和额度后在本地启用。",
  "Ready for a manual fetch. X may charge for API reads; no request has been made by switching modes.": "可手动获取帖子。X 可能收取 API 读取费用；切换模式并未发送请求。",
  "Using cached X posts. No new X request was made.": "正在使用 X 缓存帖子，未发送新请求。",
  "Latest X response cached. Analyze these posts without another API request.": "最新 X 响应已缓存，可直接分析，无需再次调用 API。",
  "X returned no public posts. This is not demo data; no synthetic posts were substituted.": "X 未返回公开帖子。这不是演示数据，未替换成合成帖子。",
  "X rejected authentication (401). Check or rotate your Bearer Token privately; do not paste it here.": "X 身份验证失败（401）。请私下检查或更换 Bearer Token，不要在此粘贴。",
  "X denied access (403). Verify your app permissions, API plan and endpoint access.": "X 拒绝访问（403）。请检查应用权限、API 套餐与接口权限。",
  "X reported a payment or credit restriction. Check your X Developer billing and access; this app does not purchase credits.": "X 返回支付或额度限制。请检查开发者账单和权限；本应用不会购买额度。",
  "X rate limit reached (429). Wait until the retry time shown; automatic retry is off.": "已触发 X 速率限制（429）。请等待显示的可重试时间，不会自动重试。",
  "Refresh cooldown active. Use the cached posts or wait until the next allowed fetch.": "获取处于冷却期，请使用缓存或等到下次允许时间。",
  "Daily request cap reached or insufficient request slots remain. Use the cache; budget resets at midnight UTC.": "已达到每日请求上限或剩余请求次数不足。请使用缓存；预算于 UTC 零点重置。",
  "Unable to reach X. Check your connection. No automatic retries or demo substitution occurred.": "无法连接 X。请检查网络；未自动重试，也未替换成演示数据。",
  "X is temporarily unavailable. Cached posts are preserved; retry manually after the cooldown.": "X 暂时不可用。缓存已保留，请在冷却期后手动重试。",
  "X account not found (404). Check the username and whether the account is public.": "未找到 X 账号（404）。请检查用户名与账号公开状态。",
  "X returned incomplete or unexpected data. Existing cache is preserved; no fabricated values were added.": "X 返回的数据不完整或格式异常。已有缓存保留，未补造数据。",
  "X rejected the request. Confirm the account and current API endpoint access in the developer portal.": "X 拒绝请求。请在开发者平台确认账号和当前 API 接口权限。"
});
Object.assign(ZH,{"Run completed":"分析完成","Observed source evidence":"可观察的来源证据","source data":"来源数据","Failed to fetch":"无法连接本地服务器，请检查应用是否仍在运行。","Load failed":"加载失败，请检查本地服务器。","Hot Take / Opinion":"鲜明观点／评论","manual_user_reported":"用户手动记录","manual_user_confirmed":"用户确认的手动发布"});
Object.assign(ZH,{
  "Content opportunity is a heuristic based on independent account breadth and specific concept diversity, not a prediction of originality.": "内容机会评分是基于独立账号广度与具体概念多样性的启发式判断，并不保证原创性。",
  "Publish a handoff-ownership checklist; test recovery from a failed specialist before adding more agents.": "制作任务交接责任清单；先测试某个专业智能体失败后的恢复流程，再讨论是否增加智能体数量。",
  "Compare one task across two runtimes; document protocol compatibility, permissions and migration effort.": "用两个运行环境完成同一任务，比较协议兼容性、权限边界与迁移成本。",
  "Show a coding-assistant review checklist; compare time saved against defects caught before approving a change.": "展示编程助手的审核清单；批准修改前，比较节省的时间与拦截的缺陷。",
  "Map reversible versus consequential actions; propose approval checkpoints and measure intervention burden.": "区分可逆操作与高影响决策，设计人工批准节点，并衡量人工介入成本。",
  "Run one task with two context budgets; compare answer quality, retained evidence and token usage.": "用两种上下文预算执行同一任务，比较回答质量、证据保留与 Token 消耗。",
  "Trace one editorial hypothesis to tagged clicks and qualified replies; separate reach from buyer intent.": "用追踪链接与合格回复验证一个内容假设，明确区分曝光触达和购买意向。",
  "Turn recurring customer questions into a content brief; validate relevance with independent sources and qualified replies.": "把反复出现的客户问题转为内容简报，用独立来源与合格回复验证相关性。",
  "Create a reproducible security-review checklist; test failure cases before recommending deployment.": "制作可复现的安全审核清单，在建议上线前测试失败场景。",
  "Validate the source claim with a second independent account before committing to a content experiment.": "先通过第二个独立账号核验来源观点，再决定是否开展内容实验。",
  "User-confirmed manual publication; not verified with X": "用户确认的手动发布记录；未通过 X 验证",
  "url": "帖子链接",
  "handle": "作者用户名",
  "text": "帖子原文",
  "created_at": "发布时间",
  "published_at": "发布时间",
  "measured_at": "衡量时间",
  "impressions": "展示量",
  "likes": "点赞",
  "reposts": "转帖",
  "replies": "回复",
  "bookmarks": "收藏",
  "link_clicks": "链接点击",
  "profile_visits": "主页访问",
  "attributed_followers": "本帖归因关注者",
  "attribution_evidence": "归因证据",
  "positioning": "品牌定位",
  "audience": "目标受众",
  "keywords": "关键词",
  "an integer": "整数",
  "a valid integer": "有效的整数",
  "a valid number": "有效数字",
  "a valid datetime or date, invalid character in year": "包含时区的有效日期时间",
  "a valid string": "有效文本",
  "Field required": "必填字段"
});
Object.assign(ZH,{
"No specific brand keyword matched":"未匹配具体品牌关键词",
"Specific domain fit is an editorial assumption; validate against your brand brief.":"领域相关性属于编辑假设，请结合品牌简报核实。",
"No domain-fit credit applied.":"未计入领域相关性分数。",
"configured AI editorial scope (domain heuristic; validate audience fit)":"已配置的 AI 内容方向（领域启发式判断；请核实受众契合度）",
"Relevance inputs":"相关性依据"
});
Object.assign(ZH,{
  "Engineering & Reliability of AI Coding Agents": "AI 编程智能体的工程化与可靠性",
  "Feedback & Error Recovery for AI Coding Agents": "AI 编程智能体的反馈与错误恢复",
  "Testing & Verification for AI Coding Agents": "AI 编程智能体的测试与验证",
  "Context Efficiency for AI Coding Agents": "AI 编程智能体的上下文效率",
  "Execution Harnesses for AI Coding Agents": "AI 编程智能体的执行框架",
  "AI Agent Interoperability & Communication Protocols": "AI Agent 互操作性与通信协议",
  "Unconfirmed Single-Post Signal": "待确认的单帖信号",
  "Provisional Discussion Cluster": "待确认的讨论主题",
  "Shared Discussion Insight": "共同讨论洞察",
  "Topic grouping does not establish rising momentum.": "多帖聚合不等于上升趋势；历史数据不足时，无法判断趋势增速。",
  "Evidence behind this insight": "查看洞察对应的来源线索",
  "Inspect the original source posts below.": "请查看下方完整来源原文。"
});
const RULES = [
 [/^Provisional Discussion: (.+)$/i,a=>`待确认的讨论主题：${a}`],
 [/^Unexpected (?:token|end).*$/,()=> 'JSON 格式无效，请按照导入示例检查文件。'],
 [/^([a-z_]+):? Input should be greater than or equal to (\d+)$/, (a,b)=>`${tr(a)}不能小于 ${b}`],
 [/^greater than or equal to (\d+)$/,a=>`不小于 ${a} 的数值`],
 [/^less than or equal to (\d+)$/,a=>`不大于 ${a} 的数值`],
 [/^a valid integer, unable to parse string as an integer$/,()=> '有效的整数'],
 [/^a valid datetime or date[\s\S]*$/,()=> '包含时区的有效日期时间'],
 [/^String should match pattern [\s\S]*$/,()=> '请输入符合要求的格式（X 用户名仅支持字母、数字和下划线）'],
 [/^List should have (?:at least|at most) (\d+) items?[\s\S]*$/,a=>`列表条目数量不符合要求（限制：${a}）`],
 [/^(↗ TOP|SIGNAL) (\d+)$/, (a,b)=>`${a==='SIGNAL'?'信号':'↗ 优先机会'} ${b}`],
 [/^This is a cached sample from @(.+?), not a platform-wide trend\. ([\s\S]*)$/,a=>`这是 @${a} 的缓存样本，不能证明全平台趋势。回复、引用与转帖均已标注；时间窗口可能覆盖不完整。`],
 [/^(N\/A|Not measured) (likes|reposts|replies)$/, (a,b)=>`${tr(b)}：未知`],
 [/^(\d+) distinct posts from (\d+) accounts discuss (.+?)\. ([\s\S]*)$/, (a,b,c,d)=>`${a} 条去重帖子来自 ${b} 个账号，共同讨论「${tr(c.replace(/\b\w/g,x=>x.toUpperCase()))}」。${d.replace(/ Plus (\d+) more supporting discussions below\./,' 其余 $1 条来源讨论见下方。')}`],
 [/^Observed: (\d+) unique posts, (\d+) distinct accounts; ([\s\S]*)$/, (a,b,c)=>`观察证据：${a} 条去重帖子、${b} 个独立账号；${c.replace(/(\d+) available likes \+ reposts \+ replies/,'可获得的点赞＋转帖＋回复为 $1 次').replace('engagement not measured','互动未衡量').replace(' (incomplete metrics; engagement scoring excluded)','（指标不完整，互动维度不参与评分）').replace('Insufficient historical data.','历史数据不足。').replace('Rising in observed sample.','所选样本内讨论量上升。').replace('Flat / falling in observed sample.','所选样本内讨论量持平／下降。').replace(/ ([+-]?[\d.]+)% observed post-count change versus the previous equal window \((\d+) posts\)\./,' 相比上一等长窗口（$2 条），样本帖子量变化 $1%。').replace(' Single-account signal, not independent confirmation.',' 单一账号信号，不构成独立来源支持。').replace(/ Missing factors excluded and remaining weights rescaled: (.+?)\./,(_,v)=>' 缺失维度已排除，其余权重重新归一化：'+v.split(', ').map(tr).join('、')+'。')}`],
 [/^Editorial hypothesis for (.+?): (.+?) connects through (.+?)\. Positioning supplied by you: ([\s\S]*) No additional product capabilities are assumed\.$/, (a,b,c,d)=>`面向「${a}」的编辑假设：此话题与品牌的关联来自${c==='no configured relevance keyword; review before prioritizing'?'尚未匹配到配置关键词，请人工确认优先级':'关键词 '+tr(c)}。用户提供的定位：${d} 未假定其他产品能力。`],
 [/^Create a practical comparison about (.+?): contrast “([\s\S]+)” with “([\s\S]+)”\. Give (.+?) one decision checklist and one measurable experiment; do not repeat the source claims as established facts\.$/, (a,b,c,d)=>`建议围绕此话题开展实用比较：对照来源观点“${b}”与“${c}”，为「${d}」提供决策清单及一个可衡量的实验。来源观点不应直接当作已证实的事实。`],
 [/^Create a practical comparison about (.+?): contrast “([\s\S]+)” with a clearly labeled counter-hypothesis\. Give (.+?) one decision checklist and one measurable experiment; do not repeat the source claims as established facts\.$/, (a,b,c)=>`建议以来源观点“${b}”为起点，明确提出待验证的反向假设，为「${c}」设计决策清单及一个可衡量的实验。单一来源不足以证实该观点。`],
 [/^(.+?) Discussion$/,a=>`其他话题（关键词：${a}）`],
 [/^([\d.,]+|Not measured) engagement$/,a=>`${tr(a)} 次互动`],
 [/^(.*?)([\d.,]+) likes/, (a,b)=>`${a}${b} 次点赞`],
 [/^(.*?)([\d.,]+) reposts/, (a,b)=>`${a}${b} 次转帖`],
 [/^(.*?)([\d.,]+) replies/, (a,b)=>`${a}${b} 条回复`],
 [/^([\d.,]+|Not measured) \((\d+) paired posts\)$/, (a,b)=>`${tr(a)}（${b} 篇配对帖子）`],
 [/^([\d.,]+)% \((\d+) paired posts\)$/, (a,b)=>`${a}%（${b} 篇配对帖子）`],
 [/^([\d.,]+|Not measured) \(partial \/ (?:unmeasured|incomplete)\)$/,a=>`${tr(a)}（指标缺失／未衡量）`],
 [/^Value error, (.+)$/,a=>tr(a)],
 [/^(String should have at least|String should have at most) (\d+) characters$/, (a,b)=>`文本长度${a.includes('least')?'至少':'最多'}为 ${b} 个字符`],
 [/^Input should be (.+)$/,a=>`输入格式不符合要求：${tr(a)}`],
 [/^([a-z_.]+): (.+)$/, (a,b)=>`${tr(a)}：${tr(b)}`],

 [/^(\d+) saved posts\. Showing the latest (\d+)\. Select Manual Imports on the radar to analyze enabled accounts\.$/,(a,b)=>`已保存 ${a} 条，显示最近 ${b} 条。在雷达选择手动导入，分析已启用账号。`],
 [/^(\d+) imported posts stored\. Choose Imported posts on the radar to analyze them\.$/,a=>`已保存 ${a} 条 JSON 导入帖子。请在雷达选择 JSON 导入进行分析。`],
 [/^(\d+) posts imported\. Select Imported posts on the radar\.$/,a=>`已导入 ${a} 条帖子。请在雷达选择 JSON 导入。`],
 [/^Monitor (.+)$/,a=>`监控 ${a}`], [/^Account: @(.+)$/,a=>`账号：@${a}`],
 [/^Last successful fetch: (.+)$/,a=>`最近成功获取：${tr(a)}`], [/^Last response: (\d+) posts$/,a=>`上次返回：${a} 条`],
 [/^Cached: (\d+) unique posts \((.+)\)$/, (a,b)=>`缓存：${a} 条去重帖子（${tr(b)}）`],
 [/^Request budget: (\d+) \/ (\d+) used$/, (a,b)=>`请求预算：已用 ${a}／${b}`], [/^Next network fetch after: (.+)$/,a=>`下次可获取时间：${a}`],
 [/^(.*?)(\d+) accounts$/, (a,b)=>`${a}${b} 个独立账号`], [/^(.*?)(\d+) unique posts$/, (a,b)=>`${a}${b} 条去重帖子`],
 [/^(.+) available engagement( \(partial\))?$/, (a,b)=>`${tr(a)} 次可获得互动${b?'（部分数据）':''}`],
 [/^([+-]?[\d.]+)% observed change$/,a=>`样本内讨论量变化 ${a}%`],
 [/^Inspect (\d+) source posts & methodology$/,a=>`查看 ${a} 条来源帖子与分析方法`],
 [/^Local synonym normalization, word\/phrase \+ character similarity, exact-text deduplication and multi-document summaries\. Summaries use all documents for theme extraction, with attributed excerpts\. Previous equal window: (\d+) matching posts\. Similarity may merge or split topics incorrectly\.$/,a=>`本地领域概念归一化，结合词语、短语与字符相似度；原文去重后进行平均链接聚类，不预设话题数量。仅凭 AI、agent、workflow 不合并。全部来源参与主题提取；保留署名原文引用。上一等长窗口匹配 ${a} 条。此为可复现启发式方法，仍可能误合并或误拆分。`],
 [/^(\d+) with measured metrics$/,a=>`${a} 篇已记录指标`], [/^(\d+) posts with paired positive impressions$/,a=>`${a} 篇有配对的正展示量数据`], [/^(\d+) \/ (\d+) posts measured$/, (a,b)=>`${a}／${b} 篇已有衡量数据`],
 [/^(\d+) published posts · (\d+) with metrics$/, (a,b)=>`${a} 篇已发布 · ${b} 篇有指标`], [/^Measurement history \((\d+) snapshots\)$/,a=>`衡量历史（${a} 个快照）`],
 [/^Source mode: (.+)$/,a=>`来源模式：${tr(a)}`], [/^(.+) source data$/,a=>`${tr(a)}来源数据`],
 [/^Source: @(.+) \((.+)\) ↗$/, (a,b)=>`来源：@${a}（${tr(b)}）↗`],
 [/^Too few imported posts for reliable trend analysis: (\d+) distinct texts from (\d+) accounts in this window\. (.*)$/, (a,b)=>`导入样本不足以支持可靠趋势分析：当前窗口仅有 ${a} 条不同原文，来自 ${b} 个账号。请增加近期、独立来源；当前结果仅代表所选样本。`],
 [/^This is a cached sample from @(.+?)\. (.*)$/,a=>`这是 @${a} 的缓存样本，不能证明全平台趋势。回复、引用与转帖均已标注；获取的数据可能无法完整覆盖所选时间窗口。`],
 [/^Could not load workspace: (.*)$/,a=>`无法加载工作台：${tr(a)}`],
];
let uiLanguage;
try { uiLanguage=localStorage.getItem('telyclaw.language')==='en'?'en':'zh'; } catch { uiLanguage='zh'; }
function tr(source) {
  if(uiLanguage==='en')return source;
  source=source.replace(/\s+/g,' ').trim();
  if(Object.hasOwn(ZH,source))return ZH[source];
  const caseKey=Object.keys(ZH).find(key=>key.toLowerCase()===source.toLowerCase());
  if(caseKey)return ZH[caseKey];
  for(const [pattern,fn] of RULES){const match=source.match(pattern);if(match)return fn(...match.slice(1));}
  if(/^\d{1,2} [A-Z][a-z]{2} \d{4},/.test(source)){const months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];return source.replace(/^(\d{1,2}) ([A-Z][a-z]{2}) (\d{4}), (.*) CST$/,(_,d,m,y,t)=>`${y}年${months.indexOf(m)+1}月${d}日 ${t} UTC+08:00`);}
  // Translate UI fragments only after complete sentences have been matched.
  if(source.includes(' · '))return source.split(' · ').map(tr).join(' · ');
  for(const [en,zh] of [['Scenario clock: ','演示场景时间：'],['Run completed · ','分析完成 · '],['Approved ','已批准 '],['Updated ','更新于 '],['Engagement: ','互动量：'],['Rate: ','互动率：']])
    if(source.startsWith(en))return zh+tr(source.slice(en.length));
  if(source.endsWith(':'))return tr(source.slice(0,-1))+'：';
  if(source.includes('; '))return source.split('; ').map(tr).join('；');
  if(source.includes(': ')){const idx=source.indexOf(': ');return tr(source.slice(0,idx))+'：'+tr(source.slice(idx+2));}
  return source;
}
const translatedNodes=new WeakMap();
function translateUI(root=document.body){
  const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
  let node;
  while((node=walker.nextNode())){
    if(node.parentElement?.closest('[data-raw],[data-i18n-en],script,style,textarea,pre,code,#language-switch'))continue;
    const old=translatedNodes.get(node);
    const source=old&&node.data===old.rendered?old.source:node.data;
    const trimmed=source.trim();
    const rendered=source.replace(trimmed,tr(trimmed));
    translatedNodes.set(node,{source,rendered});
    if(node.data!==rendered)node.data=rendered;
  }
  root.querySelectorAll?.('[data-i18n-en]').forEach(el=>{
    const value=el.dataset[uiLanguage==='zh'?'i18nZh':'i18nEn'];
    if(value!==undefined&&el.textContent!==value)el.textContent=value;
  });
  root.querySelectorAll?.('[placeholder],[aria-label]').forEach(el=>{
    for(const attr of ['placeholder','aria-label']){
      if(!el.hasAttribute(attr))continue;
      const key='i18n'+attr.replace('-','');
      const original=el.dataset[key]||el.getAttribute(attr);
      el.dataset[key]=original;
      el.setAttribute(attr,tr(original));
    }
  });
  document.documentElement.lang=uiLanguage==='zh'?'zh-CN':'en';
  document.querySelectorAll('[data-language]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.language===uiLanguage)));
}
function setLanguage(language){
  uiLanguage=language==='en'?'en':'zh';
  try{localStorage.setItem('telyclaw.language',uiLanguage);}catch{}
  document.querySelectorAll('input,textarea,select').forEach(field=>field.setCustomValidity(''));
  translateUI();
}
new MutationObserver(()=>translateUI()).observe(document.body,{childList:true,subtree:true,characterData:true});
document.querySelectorAll('[data-language]').forEach(b=>b.onclick=()=>setLanguage(b.dataset.language));
translateUI();
