# 提示词智能体

一个能**自动挑技能**的提示词智能体。你打一句话，它自己判断该用哪个技能包，按里面的规范写分镜提示词。

**技能之间不绑定、不用勾选、没有开关要拨。** 你只管说话，它自己决定。

---

## 它现在是怎么干活的

```
你输入：百芙乐后生元饮品，30秒，竖屏，主打对肠道好
    ↓
① 挑技能
   把 31 个技能的「标签」（只有 name + description）发给模型，让它挑
   → 挑中 seedance-prompt-library
   ※ 挑不出来就不猜，直接告诉你「没找到合适的技能，换个说法」
    ↓
② 装技能
   把挑中的 SKILL.md 正文拼进 system prompt
   附带参考资料按体积分两档（见下文）
    ↓
③ 生成
   模型按技能包里的规则写提示词
    ↓
输出：分镜提示词

你接着说：再短一点，第二个镜头换成特写
    ↓
它记得上文，改，而不是重写一版新的
```

**关键点**：这不是「调用 API」，是**读文件 + 拼进 system prompt**。这就是 skill 的全部秘密。

---

## 目录结构

```
提示词智能体/
├── run.py                    启动入口
├── config.json               配置（API Key 存这里）
├── config.example.json       配置模板
├── app/
│   ├── skill_loader.py       ★ 核心：扫技能 → 拆 frontmatter → 拼 system prompt
│   ├── agent.py              ★ 核心：挑技能 → 生成（含多轮对话、附件按需取）
│   └── server.py             FastAPI 后端接口
├── skills/                   ★ 技能包目录（放这里的会被自动加载）
│   ├── 27 个场景技能         13 个来自 upstream + 14 个本项目生成
│   ├── 2 个通用技能          来自 upstream（prompt-library / production-workflow）
│   └── 2 个自有技能          prompt-lint（质检）/ storyboard-writer（分镜脚本）
├── data/                     数据快照（834 条案例 + 27 个模板定义 + 811 条归类）
├── docs/                     中文文档（27 篇模板详解 + 12 篇案例合集）
├── scripts/
│   ├── build_extra_skills.py ★ 生成新增的 14 个技能（照抄 upstream 渲染逻辑）
│   ├── test_pick_skills.py   挑技能准确率测试（26 项，含 lint 伴随判定）
│   ├── test_lint.py          用质检技能跑 output/ 里的产物
│   └── demo_one_skill.py     强制指定单个技能跑完整流水线（演示用）
├── _参考_技能/                （不参与加载，只是备着）
│   ├── awesome-seedance/     upstream 源码仓库（data/ 与 docs/ 的来源）
│   ├── seedance-prompt-lint/        自有技能原件（已拷进 skills/）
│   ├── seedance-storyboard-writer/  自有技能原件（已拷进 skills/）
│   └── _orig-lint/                   lint 技能改造前的 v1.0.0 备份
├── static/index.html         前端页面（单文件，无依赖）
├── output/                   生成的提示词存这
└── logs/
```

**加新技能**：在 `skills/` 下建文件夹，放 `SKILL.md`（开头要有 `name:` 和 `description:`），点页面左下角「重新扫描」即刻生效，**不用重启**。

**重新生成那 14 个技能**：改完 `data/skills-extra.json`（加一条 `id` / `templateId` / `triggers`）后跑

```bash
python scripts/build_extra_skills.py
```

---

## 怎么跑

### 1. 装依赖

```bash
pip install openai fastapi "uvicorn[standard]" pyyaml
```

### 2. 配置 API Key

三种方式，任选一种：

- **网页里配（推荐）**：启动后点左下角「设置」，填 API Key 保存，会写进 `config.json`
- **改文件**：把 `config.example.json` 复制成 `config.json`，填 `api_key`
- **环境变量**：`set DASHSCOPE_API_KEY=sk-xxxx`

默认走阿里云 DashScope（`qwen-plus`）。要用别的模型，改 `base_url` 和 `model` 就行——**只要是 OpenAI 兼容接口都能接**（本项目当前用的是 DeepSeek）。

### 3. 启动

```bash
python run.py
```

浏览器打开 **http://127.0.0.1:8080**（注意是 8080）

参数：

```bash
python run.py --port 9000              # 换端口
python run.py --host 0.0.0.0           # 允许局域网访问
python run.py --skills "D:\MySkills"   # 换技能目录
python run.py --reload                 # 开发模式，改代码自动重启
```

---

## 怎么用

**就两步**：输入框打一句话 → 回车。

### 它会记上下文（多轮对话）

写完一版之后，**直接接着说**就行：

```
再短一点，第二个镜头换成特写
把结尾加一句行动号召
换成口播版
```

它会**改**，不是重写一版新的。顶栏会出现一个「🧠 记忆 N 轮」的小标，**点它可以清空记忆**重新开话题。

换全新话题时它会自己切过去，不会被上一轮绑死。

### 页面上的东西

| 位置 | 是什么 |
|---|---|
| 顶栏 `🧠 记忆 N 轮` | 它现在记得几轮对话。点一下清空记忆 |
| 顶栏 `清空` | 清空页面 + 清空记忆 |
| 左侧技能列表 | 当前加载的 31 个技能。**点一下能看详情**（干什么用的、带不带参考资料、正文开头） |
| 左下角 `重新扫描` | 加了/删了技能文件夹后点一下，不用重启 |
| 左下角 `设置` | 改 API Key / 模型 |

左边那栏**不用勾选**（默认全开），点进去只是给你看功能说明。

---

## 31 个技能

| 来源 | 数量 | 说明 |
|---|---|---|
| upstream 原装 | 15 个 | 来自 [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance)，与源码**字节一致**（改动前先 `diff -rq` 核对） |
| 本项目生成 | 14 个 | 用 `scripts/build_extra_skills.py` 从同一套数据生成，格式与 upstream **逐字节对齐**（13/13 回归验证通过） |
| 自有技能 | 2 个 | `seedance-prompt-lint`（质检）、`seedance-storyboard-writer`（分镜脚本）。不在 upstream 里，我们自己写的 |

> ⚠️ 注意：`skills/` 里**没有**任何一个技能是 upstream 没有的——这 2 个自有技能是唯一例外。

### 13 个 upstream 场景技能

| 技能 | 适用 | 中文触发词 |
|---|---|---|
| `seedance-3d-cartoon` | 3D 卡通角色短片 | 3D 卡通、皮克斯、黏土、卡通角色 |
| `seedance-car-vehicle` | 汽车与载具速度片 | 汽车、赛车、摩托、载具 |
| `seedance-epic-fantasy-scifi` | 奇幻科幻大场面 | 奇幻、科幻、巨龙、怪兽、史诗 |
| `seedance-fashion-lookbook` | 时尚 lookbook / 人像写真 | 时尚、穿搭、人像、写真 |
| `seedance-food-asmr` | 美食特写 / 吃播 ASMR | 美食、吃播、ASMR、烹饪 |
| `seedance-game-ui-livestream` | 游戏录屏 + 直播叠层 | 游戏录屏、实机、直播、HUD、UI 动效 |
| `seedance-horror-suspense` | 恐怖悬疑短片 | 恐怖、悬疑、惊悚 |
| `seedance-meme-comedy` | 反转结尾搞笑短片 | 搞笑、反转、梗、沙雕 |
| `seedance-pet-animal` | 宠物动物当主角 | 宠物、猫、狗、动物 |
| `seedance-retro-dv-home-video` | 早年 DV 家庭录像 | DV、家庭录像、VHS、复古、年代感 |
| `seedance-sports-extreme` | 体育与极限运动 | 体育、极限运动、跑酷、滑板 |
| `seedance-storyboard-grid-to-video` | 分镜网格转视频 | 分镜图、九宫格、故事板 |
| `seedance-travel-city-walk` | 电影感旅行漫游 | 旅拍、城市漫游、旅行 |

### 14 个本项目新增场景技能

upstream 只做了 27 个模板里的 13 个独立技能，剩下 14 个模板的案例（437 条）原本无处落地。这 14 个把缺口补上了：

| 技能 | 适用 | 中文触发词 |
|---|---|---|
| `seedance-handheld-ugc-vlog` | 手持 UGC vlog | 手持、UGC、vlog、手机拍摄、生活记录 |
| `seedance-combat-choreography` | 打斗编排 | 打斗、动作戏、格斗、武打、连招 |
| `seedance-cinematic-narrative-short` | 电影级叙事短片 | 剧情短片、叙事、故事短片、电影感剧情 |
| `seedance-product-commercial-shotlist` | 电影级产品广告分镜 | 产品广告、商业广告、产品展示、TVC |
| `seedance-anime-style-lock` | 动漫与风格化画风固定 | 动漫、二次元、画风、动画风格 |
| `seedance-process-transformation-montage` | 流程与变换蒙太奇 | 过程蒙太奇、改造、延时、制作流程、组装 |
| `seedance-music-beat-sync-mv` | 音乐卡点 MV | MV、卡点、音乐、节奏剪辑 |
| `seedance-ugc-creator-review` | UGC 口播测评带货 | 口播、测评、开箱、种草、带货 |
| `seedance-pov-continuous-take` | 第一人称一镜到底 | 第一人称、一镜到底、POV、运动相机、GoPro |
| `seedance-dialogue-performance-beats` | 对白与表演节拍 | 对白、口型同步、台词、表演 |
| `seedance-stop-motion-cadence` | 定格动画与步进节奏 | 定格动画、逐帧、停格、黏土 |
| `seedance-character-reference-lock` | 参考图身份锁定 | 参考图、角色锁定、人物一致性、形象固定 |
| `seedance-time-freeze-rewind` | 时间冻结与倒放奇观 | 时间冻结、倒放、子弹时间、时间停止 |
| `seedance-timeline-shot-script` | 逐秒时间轴分镜脚本 | 逐秒分镜、时间轴、时间码、分镜脚本 |

### 2 个通用技能

| 技能 | 干什么 | 中文触发词 |
|---|---|---|
| `seedance-prompt-library` | **27 个提示词模板总库**（逐秒时间轴、产品广告分镜、口播、对话口型、MV、动漫风……）。类别对不上任何专属技能时走它 | 描述是英文，但实测中文提问照样命中 |
| `seedance-production-workflow` | **端到端制作流程**：从 brief → 素材 → 分镜 → 提交 → 逐镜复盘 → 定点返修。要「完整走一遍」时用它 | 同上 |

### 2 个自有技能

| 技能 | 干什么 | 关键设计 |
|---|---|---|
| `seedance-prompt-lint` | **提示词质检器**。只检查、不生成。对任何一段 Seedance 提示词跑一遍，输出「必改 / 提醒 / 格式备注 / 通过」四级报告 + 可抄的改法 | **v2.0.0 改造版**：检查项拆成 A 类（通用，无条件跑）和 B 类（官方格式专项，条件跑）。见下方说明 |
| `seedance-storyboard-writer` | 分镜脚本撰写 | 手写，无附件 |

#### `seedance-prompt-lint` 为什么要改造（v1.0.0 → v2.0.0）

原版只认**即梦官方四段式**这一种格式（`【素材描述】+【一句话概述】+【具体情节描述】+【全局补充】`），
而本仓 27 条场景技能走的是 **goodcase 案例方言**（分块结构 + 时间轴 + 中英混写机位 + 自然语言音效）。

实测 3 份本仓产物，原版共报 12 项「必改」，其中：

| 类型 | 数量 | 例子 |
|---|---|---|
| 真问题 | 8 | 时间段断档 3 秒、全片无景别、5 段无运镜、整条无声音层、单段 5 事件、运镜与动作空间互斥 |
| **格式误报** | 3 | 缺【一句话概述】3/3（goodcase 路线不要求）、声音未用 `< >` 2/3 |
| 字面主义 | 1 | 抠"固定机位"四个字里没有"固定镜头" |

**改造动作**：

1. 新增「第 0 步：先判方言」——用 `有没有【一句话概述】或 @图片N` 判断这条稿子属于哪条路线，判错就全盘误报
2. 检查项拆两类：**A 类通用**（时间连续性 / 逐段运镜 / 逐段景别 / 反向描述 / 声音层 / 违规词 + 全部语义层 M1-M7）无条件跑；**B 类官方格式**（四段式 / `@图片N` / 声音符号 / 禁止项双写）只在确认是官方方言时跑，结果降级到「📐 格式备注」
3. 新增 **S11 声音层**检查（原版漏了，定格动画那条整条没提声音却没被稳定报出）
4. 给 S3 / S4 / C4 补英文白名单 —— `MEDIUM SHOT` / `lock-off` / `Ground-level Low Angle` 都算合法写法，不再误判缺失

**改造后效果**（同样 3 份产物）：必改项**全部是真问题，零格式误报**。

| 产物 | 改造前必改 | 改造后必改 | 抓到的真问题 |
|---|---|---|---|
| 雨夜骑手 15 秒 | 3 | 1~2 | 镜头 5 运镜与动作空间互斥（拉远 + 驶出画面 + 仍在画面下三分之一） |
| 定格动画 | 5 | 3 | 全片无时间戳、全片无景别、整条无声音层、单段事件过密 |
| 可口可乐 15 秒 | 4 | 2~3 | **时间段断档**（`0-3 → 4-7 → 8-11 → 12-15`，每段之间空 1 秒） |

> ⚠️ **已知局限**：LLM 当裁判有波动。同一份稿子跑两次，必改项数可能从 3 变 2（例如某次把有 `NEGATIVE` 块的稿子误报成"无反向描述"）。定位是「第二双眼睛」，不是确定性校验器。

#### 它什么时候会被选中

实测行为（26 项挑技能测试）：

| 需求写法 | 选中 |
|---|---|
| "帮我写一条 15 秒产品广告提示词" | 只选 `seedance-product-commercial-shotlist` |
| "写一条美食 ASMR 提示词，**写完顺便帮我检查一下有没有问题**" | `seedance-food-asmr` + `seedance-prompt-lint` |
| "写一条分镜提示词，**别把没查过的稿子交给我**" | `seedance-timeline-shot-script` + `seedance-prompt-lint` |
| "帮我质检一下这段提示词：…" | 只选 `seedance-prompt-lint` |

**即：单纯"写一条"不会带上它（不多花字符），说了"要成稿/帮我检查/确认没问题"才带上。**

**成本**：选中 lint 时额外注入 5,351（正文）+ 6,017（checklist）= 11,408 字符 ≈ 4,000 tokens。只在需要质检时才付。

### 实测挑技能准确率

31 个技能下测 26 项：**26 对 / 0 次多选**（14 个新片型 14/14、重叠边界 4/4、老片型回归 5/5、质检 3/3）。

重叠边界特指 `handheld-ugc-vlog`（手持 vlog）与 `retro-dv-home-video`（DV 家庭录像）——两者都靠「相机缺陷 + 指名器材年代」换真实感，最容易互相抢，实测 4 条边界用例全部分清。

唯一「失败」的是**不说类别的泛化请求**（例如「帮我写一条视频提示词」）——它会**如实告诉你没找到合适技能**，让你换个说法。

这是**故意的**：宁可不猜，也不要勉强塞一个沾边的技能，导致产出驴唇不对马嘴。

---

## 参考资料是怎么给模型的

技能目录里的 `references/` 附件，按**体积**分两档：

| 情况 | 做法 |
|---|---|
| 单个附件 **≤ 40,000 字符** | **自动全文内联**进 system prompt，模型直接看得到 |
| 单个附件 **> 40,000 字符** | 只登记文件名，模型需要时**自己调 `read_reference` 工具**去取 |
| 附件总量预算 | 60,000 字符 |
| 单次回填上限 | 150,000 字符（`agent.REF_READ_MAX_CHARS`） |

**当前只有一个附件走「按需取」**：`seedance-prompt-library/references/style-library.md`（139,380 字符，27 个模板，中英双语）。其余 30 个技能的附件（主要是 `cases.md`，单文件 18,315 ~ 30,526 字符；lint 的 `checklist.md` 6,545 字符）**全部自动内联**，模型一选中就拿到手，不用主动去读。

---

## 核心代码在哪

**`app/skill_loader.py`** — 四步：

```python
# ① 扫 skills/ 目录，读每个 SKILL.md
# ② 拆 frontmatter（--- 包起来那段），拿到 name 和 description
# ③ catalog_for_llm()  给模型一份「名称：描述」清单，让它挑
# ④ build_system_prompt()  把挑中的正文（+可内联的附件）拼成 system prompt
```

**`app/agent.py`** — 关键部分：

```python
PIPELINES           # 技能绑定表。现在是空 []，即技能之间不绑定
pick_skills()       # 用 description 让模型选，返回 (技能列表, 来源)
                    #   来源 = user（手动指定）/ model（模型选的）/ reuse（沿用上一轮）
generate()          # 注入技能全文 → 生成。含多轮对话 + 附件按需取 + 工具调用兜底
resolve_pipeline()  # 去重、校验存在性（PIPELINES 为空时只做清洗）
run_full()          # 总指挥：pick → resolve → generate
```

**技能之间不串联**。`PIPELINES = []` 就是原因——选什么就是什么。想恢复绑定，往这个列表里加 `["主技能", "后置技能"]` 即可，代码一行不用改。

---

## 几个坑（都踩过，别重犯）

**① 判断附件「要不要内联」只能用 `info["inline"]`，不能用 `bool(info["content"])`**

`read_reference()` 会把读到的内容回填进 `content`。如果拿它当判据，一份大附件**第一次读完之后就被重新归类成「已内联」**，工具不再下发，模型想读却没工具可用——症状是「第一次能用，之后每次都不行」，极难查。`inline` 标记在加载时定死，之后谁都不许改。

**② DeepSeek 会把工具调用「说」成文本**

约一半概率，`msg.tool_calls` 是 `None`，但正文里出现：

```
<｜｜DSML｜｜ invoke name="read_reference">
<parameter name="path">references/style-library.md</parameter>
```

`generate()` 里有兜底：**不解析 DSML 语法**（各家格式不同、版本会变），只认「已知附件文件名有没有出现在回复里」，命中就由代码代它把文件读出来。

**③ 判断阈值一律用「字符数」不是「字节数」**

中文在 UTF-8 占 3 字节。拿 `st_size` 比阈值会把中文附件误判成超大。

**④ `SkillLoader` 是长生命周期单例**

状态污染只在**同一进程内第 2 次调用**才显现。遇到「单机跑单个测试通过、连着跑就失败」，第一反应查单例状态被写脏。

**⑤ token 估算别拍脑袋**

`style-library.md` 是**中英双语**，实测 **0.33 token/字符**（英文约 4 字符/token，把整体密度拉低了）。
106,284 字符 = **35,339 tokens**，塞进 64k 上下文绰绰有余。
纯中文要按 ~0.7 token/字符估，英文 ~0.25。
所以 `REF_READ_MAX_CHARS` 不要再盲目往上调；真要支持更大的附件，应该改成「按章节取」而不是继续放宽。

**⑥ 验证「模型有没有看到某段内容」时，不要让模型自己数总数**

实测问「最后一个模板的 id 是什么」，它答了倒数第二个（差一个）；换成「列出第 23~27 个」就全对。
**给它序号，别让它数。**

**⑦ 目录名 ≠ 技能名**

生效的是 frontmatter 里的 `name:`。

**⑧ 单个技能超 6 万字符、总量超 12 万字符会截断**，并在结果里标注 `truncated`。

---

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/skills` | 看加载了哪些技能（含附件内联/按需状态） |
| POST | `/api/skills/reload` | 重新扫描目录（顺便重读白名单） |
| GET | `/api/config` | 看当前配置（key 打码） |
| POST | `/api/config` | 改配置 |
| POST | `/api/chat` | 一次性返回结果 |
| POST | `/api/stream` | SSE 流式，能看每步进度（前端用的这个） |

`/api/chat` 和 `/api/stream` 的请求体：

```json
{
  "message": "百芙乐后生元饮品，30秒，竖屏",
  "skills": null,
  "do_lint": true,
  "history": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}],
  "last_skills": ["seedance-prompt-library"]
}
```

- `skills` 传数组 = 手动指定技能，跳过模型判断
- `history` = 多轮对话的上文（后端只取最近 8 条）
- `last_skills` = 上一轮用过的技能，追问兜底用

---

## 改了东西之后要不要重启

| 你做了什么 | 要怎么办 |
|---|---|
| 改了 `skills/` 里某个 SKILL.md | 点左下角「**重新扫描**」，不用重启 |
| 新增/删除了技能文件夹 | 同上 |
| 改了 `.py` 代码 | **重启**（或启动时加 `--reload`） |
| 改了 `config.json` 的 `base_url` / `api_key` / `model` | 不用重启，下次请求自动生效 |
| 改了 `skills_whitelist` | 重启，或点「重新扫描」（会顺便重读白名单） |
| 改了 `static/index.html` | 浏览器 `Ctrl+F5` 强刷，不用重启 |
| 换了 `--skills` 目录 / 改了 `SKILLS_DIR` | **必须完全停进程再启**（`--reload` 不会重读环境变量） |

---

## 已隔离在外的技能

`AI_Summary/seedance2.5/seedance25-official`（Seedance 2.5 官方手册，39 万字节）**不进 `skills/`**。

原因：它和 `seedance-prompt-library` 会**抢「写提示词」这个活**，导致产出不稳定。移走之后测试 10/10 全对。
