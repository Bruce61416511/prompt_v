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
   ※ 挑不出来就不猜，直接说清原因（四选一）：
      · 没匹配 —— 换个说法，或点左侧技能名带入召唤词
      · 技能名无效 —— 调 API 时手填了库里没有的名字
      · 技能库为空 —— 去点「重新扫描」
      · 接口出错 —— 选技能这一步调用失败，跟你的描述无关，查服务
    ↓
② 装技能
   把挑中的 SKILL.md 正文拼进 system prompt
   附带参考资料按体积分两档（见下文）
    ↓
③ 生成
   模型按技能包里的规则写提示词
    ↓
④ 质检
   固定环节：生成完自动跑 seedance-prompt-lint，出「必改 / 提醒 / 格式备注」报告
    ↓
⑤ 按质检修正
   拿质检报告把提示词改一遍，产出**可直接复制去生成视频的定稿**
    ↓
输出：① 分镜提示词　② 质检报告　③ 纠正后的提示词（复制即用）

你接着说：再短一点，第二个镜头换成特写
    ↓
它记得上文，改，而不是重写一版新的
```

**关键点**：这不是「调用 API」，是**读文件 + 拼进 system prompt**。这就是 skill 的全部秘密。

---

## 目录结构

```
prompt_v/
├── run.py                    网页服务启动入口（FastAPI + 静态页，同一个进程）
├── feishu_bot.py             ★ 飞书通道：长连接接消息 → 跑同一条流水线 → 卡片回帖
├── start.bat                 ★ 一键启动：双击即可（自动找 Python + 挑空闲端口 + 开浏览器 + 拉起飞书）
├── requirements.txt          运行依赖清单（fastapi / uvicorn / lark-oapi）
├── config.json               配置（API Key、飞书凭据存这里；已 gitignore）
├── config.example.json       配置模板
├── .gitignore                不提交 config.json / output/ / update-status.json / .venv 等
├── LICENSE
├── app/
│   ├── skill_loader.py       ★ 核心：扫技能 → 拆 frontmatter → 拼 system prompt
│   ├── agent.py              ★ 核心：挑技能 → 生成 → 质检 → 修正（含多轮对话、附件按需取）
│   └── server.py             FastAPI 后端接口（聊天、配置、技能扫描、案例库、检查更新）
├── skills/                   ★ 技能包目录（放这里的会被自动加载）
│   ├── 27 个场景技能         13 个来自 upstream + 14 个本项目生成
│   ├── 2 个通用技能          来自 upstream（prompt-library / production-workflow）
│   └── 2 个自有技能          prompt-lint（质检）/ storyboard-writer（分镜脚本）
├── data/
│   ├── cases.json            834 条人工核验案例（含完整 prompt）
│   ├── case-taxonomy.json    811 条「案例 → 模板」归类
│   ├── style-library.json    14 个模板的结构化定义（中英双语）
│   ├── templates-local.json  另外 13 个模板 + 对上面 14 个的改写层
│   ├── skills-extra.json     ★ 本项目自己的：14 个自建技能的配置
│   ├── skills.json / site-skills.json / site.json / stats.json
│   ├── feishu-whitelist.json 飞书白名单（open_id / chat_id）
│   └── update-status.json    「上次检查上游」的时间戳（运行时生成，已 gitignore）
├── docs/                     中文文档（27 篇模板详解 + 12 篇案例合集）
├── scripts/
│   ├── build_extra_skills.py ★ 生成新增的 14 个技能（照抄 upstream 渲染逻辑）
│   ├── sync_upstream.py      ★ 从上游拉最新数据并同步（左下角「检查更新」调的就是它）
│   ├── test_pick_skills.py   挑技能准确率测试（26 项，含 lint 伴随判定）
│   ├── test_lint.py          用质检技能跑 output/ 里的产物
│   └── demo_one_skill.py     强制指定单个技能跑完整流水线（演示用）
├── backup_awesome/           （不参与加载，**可整目录删掉**，不影响任何功能）
│   ├── awesome-seedance/     upstream 源码仓库（data/ 与 docs/ 的来源）
│   ├── seedance-prompt-lint/        自有技能原件（已拷进 skills/）
│   ├── seedance-storyboard-writer/  自有技能原件（已拷进 skills/）
│   └── _orig-lint/                   lint 技能改造前的 v1.0.0 备份
├── static/index.html         前端页面（单文件，无依赖）
├── output/                   生成的提示词存这（已 gitignore）
└── logs/
```

**加新技能**：在 `skills/` 下建文件夹，放 `SKILL.md`（开头要有 `name:` 和 `description:`），点页面左下角「重新扫描」即刻生效，**不用重启**。

**重新生成那 14 个技能**：改完 `data/skills-extra.json`（加一条 `id` / `templateId` / `triggers`）后跑

```bash
python scripts/build_extra_skills.py
```

---

## 怎么跑呢

### 1. 装依赖

```bash
pip install -r requirements.txt
```

三个包，分两拨：

| 包 | 给谁用 | 不装会怎样 |
|---|---|---|
| `fastapi` + `uvicorn` | 网页服务（`run.py`） | **什么都不能跑**，必装 |
| `lark-oapi` | 飞书通道（`feishu_bot.py`） | 网页照常跑；只是双击 `start.bat` 时飞书那个小窗口会报 `ModuleNotFoundError: No module named 'lark_oapi'` |

`lark-oapi` 会顺带装下来 `requests` / `websockets` / `httpx` / `pycryptodome`——长连接和事件加解密要用，别手动卸。

没有前端构建工具，页面是原生 HTML + JS，不用 `npm install`。

> **Ubuntu 24.04 这类系统**有 PEP 668 限制，直接 `pip install` 会被系统拦下报 `externally-managed-environment`，
> 必须先建虚拟环境：`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`

### 2. 配置 API Key

三种方式，任选一种：

- **网页里配（推荐）**：启动后点左下角「设置」，填 API Key 保存，会写进 `config.json`
- **改文件**：把 `config.example.json` 复制成 `config.json`，填 `api_key`
- **环境变量**：`set DASHSCOPE_API_KEY=sk-xxxx`

默认走阿里云 DashScope（`qwen-plus`）。要用别的模型，改 `base_url` 和 `model` 就行——**只要是 OpenAI 兼容接口都能接**（本项目当前用的是 DeepSeek）。

### 3. 启动

**最省事：双击 `start.bat`**（项目根目录里一个，桌面上也放了一个入口）。它把两个进程一起管了：

| 它做什么 | 说明 |
|---|---|
| **网页服务**（run.py） | 已在跑就只开浏览器，不重复启动；没在跑就从 8099 起自动挑空闲端口启动并打开页面 |
| **飞书通道**（feishu_bot.py） | 已在跑就跳过；没在跑就在**独立的小窗口**里拉起——窗口标题写着"closing this window = channel stopped" |

两个互相独立：关掉飞书的小窗口不影响网页，关掉主窗口不影响飞书。

**改了代码想强制重启？** 带参数运行：

```bat
start.bat restart
```

它会先把网页 + 飞书两个进程都杀掉，再全部重新拉起（普通双击永远是"复用不杀"，防止误停）。

> 提示：start.bat 里的提示文字是**英文的**——这是刻意的。中文批处理在 cmd 里有编码坑
> （UTF-8+chcp 会截断命令行、GBK 在编辑器里乱码），纯 ASCII 两边都干净。

命令行方式也一样，只是参数自己写：

```bash
python run.py                        # 默认 8080 端口（网页 + 接口，前端无需单独启动）
python run.py --port auto            # 从 8099 起自动找空闲端口（日常推荐）
python feishu_bot.py                 # 飞书通道（需要 config.json 里配好 feishu 凭据）
```

浏览器打开 **http://127.0.0.1:8080**（默认端口；用 `--port auto` 时看启动时打印的地址）

参数：

```bash
python run.py --port 9000              # 指定端口；被占用会直接告诉你被谁占了
python run.py --port auto              # 自动挑一个空闲端口（从 8099 起）
python run.py --host 0.0.0.0           # 允许局域网/公网访问（默认只监听 127.0.0.1）
python run.py --open                   # 启动后自动打开浏览器
python run.py --skills "D:\MySkills"   # 换技能目录
python run.py --reload                 # 开发模式，改代码自动重启
```

> ⚠️ **部署到服务器时**：默认只监听 `127.0.0.1`，也就是**只有服务器自己能访问**，外部打不开；
> 必须显式加 `--host 0.0.0.0`，否则你会去查防火墙/安全组，其实根本没到那一步。

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

### 案例库（顶栏第二个页签）

顶栏切到「🎬 案例库」，834 条上游案例直接翻：

- **卡片墙**：封面 + 中文标题 + 版本/证据徽章 + 热度，滚动到底自动加载下一批（一批 60 条）
- **筛选**：按版本（2.5 / 2.0）、按 27 个模板分类、按作者、只看 L2 人审实测；顶部搜索框能搜标题、prompt 正文和作者
- **详情**：点封面打开，左边视频 + 复现验证记录，右边完整 prompt
- **用这条生成**：详情里点这个按钮，这条案例的写法会自动带回聊天输入框，改一下【我的需求】就能让智能体照着写一条新的
- 数据直接读 `data/cases.json`，**点「检查更新」拉到新案例后这里自动就有**，不用额外操作

### 页面上的东西

| 位置 | 是什么 |
|---|---|
| 顶栏 `💬 生成分镜提示词 / 🎬 案例库` | 两个视图来回切，聊天记录不会丢 |
| 顶栏 `🧠 记忆 N 轮` | 它现在记得几轮对话。点一下清空记忆 |
| 顶栏 `清空` | 清空页面 + 清空记忆 |
| 左侧技能列表（31 个，行为完全统一） | **点一下 = 把它的名字填进输入框**（风格填中文名，工具填一句现成的说法），接着补上你的要求发送即可。点右侧 `›` 看技能详情 |
| 左下角 `重新扫描` | 加了/删了技能文件夹后点一下，不用重启 |
| 左下角 `检查更新` | 去上游看一眼有没有新案例。**按钮下面那行字就是状态**：`数据 2026-10-14（834 条） · 检查 今天 19:08` |
| 左下角 `设置` | 改 API Key / 模型 |

侧栏显示的是**中文名**（取自技能标题），下面一行小字是去掉 `seedance-` 前缀的英文短名；
技能的真名不会出现在界面上，只用于内部匹配。

**关于指定风格**：不需要任何"锁定"开关——**技能的中文名本身就是召唤词**。
2026-10-16 实测：用中文名点名 12 个风格（专挑最容易互相抢的），自动挑选 **12/12 精确命中**。
所以把名字写进输入框（点侧栏帮你填）比隐藏开关更好：看得见、能改、能叠加别的要求，
也不存在"锁了但内容和风格不搭"的陷阱。技能全部由系统自动选，质检固定自动跑。

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

**成本**：质检现在是**固定环节**（2026-10-16 起）：不管选中没选中 `seedance-prompt-lint`，生成完一律自动查一遍，没选中时由后端自动补上这个技能。每次生成多花一次调用（实测总耗时从约 9 秒变 19~23 秒）+ 额外注入约 4,000 tokens。唯一例外：你只说「检查这段提示词」时，产出物本身就是质检报告，不会再查第二遍。

**修正环节**（2026-10-17 起）：质检完再跑一次「按报告改稿」，产出第 ③ 段「纠正后的提示词」。这一段原先只写在 `feishu_bot.py` 里，网页端跑完质检就结束 —— 同一条需求两边产出不一样。现在收进 `Agent.revise()`，网页 / 飞书共用；实现见 `app/agent.py` 的 `REVISE_PROMPT` 与 `_split_revision()`。多一次调用（实测整条链路约 23 秒，其中修正 4~5 秒）。

### 实测挑技能准确率

31 个技能下测 26 项：**26 对 / 0 次多选**（14 个新片型 14/14、重叠边界 4/4、老片型回归 5/5、质检 3/3）。

重叠边界特指 `handheld-ugc-vlog`（手持 vlog）与 `retro-dv-home-video`（DV 家庭录像）——两者都靠「相机缺陷 + 指名器材年代」换真实感，最容易互相抢，实测 4 条边界用例全部分清。

唯一「失败」的是**不说类别的泛化请求**（例如「帮我写一条视频提示词」）——它会**如实告诉你没找到合适技能**，让你换个说法。如果失败原因是接口出错或技能库为空，提示会明确指向那种情况，不会让你白白去改措辞。

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

## 检查更新（同步上游数据）

`data/` 里的数据来自 upstream 仓库。想看看有没有新的，点左下角「**检查更新**」，或直接跑命令行：

```bash
python scripts/sync_upstream.py            # 检查并同步
python scripts/sync_upstream.py --check    # 只看有没有新数据，一个字节都不写
python scripts/sync_upstream.py --force-regen   # 数据没变也重生成技能
```

它做四件事：

1. 拉 `data/cases.json`（案例）、`data/case-taxonomy.json`（归类表）、`data/style-library.json`（模板库）、`data/skills.json`
2. 和本地**逐字节比对**（忽略行尾差异），**只有真变了才落盘**
3. 数据有变化时，重生成 14 个自建技能 + 从上游拉 13 个上游技能的 `SKILL.md` / `cases.md`
4. 拉 `EXTRA_FILES` 里的「孤儿文件」（原因见下）

之后把结果写进 `data/update-status.json`。

> **为什么要第 4 步**：`skills/seedance-prompt-library/references/style-library.md`（141 KB）是从上游
> `data/style-library.json` 渲染出来的，但本项目**没有任何脚本生成它**，而它所在的技能又在「不碰」名单里。
> 结果就是上游数据更新了、这个文件却永远停在搬运那天。`EXTRA_FILES` 专门补这个缺口。

### 那行字怎么读

```
数据 2026-10-14（834 条） · 检查 今天 19:08
```

| 位置 | 含义 |
|---|---|
| `数据 …（N 条）` | **上游数据的版本**。只有上游真出新数据才变 |
| `检查 今天 19:08` | **上次检查的时间**。每点一次都会更新，哪怕没新数据 |

两个分开显示，是为了不出现「数据其实还是旧的、界面却显示刚刚」的误导。

### 会动哪些文件、不碰哪些

| | |
|---|---|
| **会覆盖** | `data/` 下那 4 个数据文件；14 个自建技能的 `SKILL.md` + `references/cases.md`；13 个上游技能的这两个文件；`EXTRA_FILES` 里的孤儿文件 |
| **不碰** | `seedance-prompt-lint`（我们改造过的）、`prompt-library`、`storyboard-writer`、`production-workflow` 的 SKILL.md 与 cases.md；`data/templates-local.json`、`data/skills-extra.json`（本项目自己的）；`docs/`、`backup_awesome/`、`static/`、`app/` |

- **没新数据时，技能文件一个字节都不会变**（已验证幂等：连跑两次哈希完全一致）
- 拉到的东西**必须是合法 JSON 才会落盘**，拿到坏数据不会覆盖本地
- 孤儿文件另有两道校验：**体积 ≥ 4 KB** 且 **以 `#` 开头**（挡住上游返回 HTML 错误页之类的情况）
- 源顺序：默认走 `gh-proxy.com` 镜像（实测 ~1.9 秒），失败自动回退直连
  （实测直连 `raw.githubusercontent.com` **首次要 60 秒**，所以不作为首选）

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
| GET | `/api/update/status` | 上次检查上游的时间 + 当前数据版本（前端左下角显示的那行字） |
| POST | `/api/update/run` | 手动检查上游并同步，约 10~20 秒返回（左下角「检查更新」按钮） |
| GET | `/api/cases` | 案例库列表：分页 + 搜索（q）+ 筛选（model / template / level / creator）+ 排序（sort），只返回轻量字段，封面/标题/热度等 |
| GET | `/api/cases/{slug}` | 单条案例详情：完整 prompt、复现记录、来源链接（案例库详情弹窗用的这个） |

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
| 想同步上游最新案例 | 点左下角「**检查更新**」，不用重启；命令行 `python scripts/sync_upstream.py` |
| 换了 `--skills` 目录 / 改了 `SKILLS_DIR` | **必须完全停进程再启**（`--reload` 不会重读环境变量） |

---

## 已隔离在外的技能

`AI_Summary/seedance2.5/seedance25-official`（Seedance 2.5 官方手册，39 万字节）**不进 `skills/`**。

原因：它和 `seedance-prompt-library` 会**抢「写提示词」这个活**，导致产出不稳定。移走之后测试 10/10 全对。
