# awesome-seedance 未同步功能清单

对比时间：2026-10-16
对比对象：`_参考_技能/awesome-seedance/` → 本项目 `提示词智能体/`

---

## 0. 已完成同步（基线）

| 项 | 状态 |
|---|---|
| `agents/skills/` 15 个技能 | ✅ **100% 同步** |
| └ 13 个场景技能（SKILL.md + references/cases.md） | ✅ 字节一致 |
| └ seedance-prompt-library（SKILL.md + style-library.md + bin/ + CHANGELOG.md + package.json） | ✅ 字节一致 |
| └ seedance-production-workflow（SKILL.md + 4 附件 + scripts/ + agents/openai.yaml） | ✅ 字节一致 |
| 验证方式 | `diff -rq` 零输出 |

> 结论：**"技能"这一层已经没有欠账**，下面列的全是技能以外的东西。

---

## 1. 数据层 `data/`（10 文件 / 4.4 MB）

| # | 文件 | 体积 | 内容 | 优先级 |
|---|---|---|---|---|
| 1 | `cases.json` | 4.06 MB | **834 条人工核验案例**。单条 20+ 字段：slug / 中英标题 / 中英摘要 / `promptFull` 完整提示词 / category / models / creator / sourceUrl / 发布时间 / heatScore / 加权互动 / mediaUrl / posterUrl / evidenceLevel / stabilityScore / tags / contentLocale / provenanceVerified / **retests 复测记录** / retestSummary | ⭐⭐⭐ 高 |
| 2 | `case-taxonomy.json` | 72 KB | **811 条 slug → 模板 id 的归类映射**（每个案例属于 27 个模板中的哪一个） | ⭐⭐⭐ 高 |
| 3 | `style-library.json` | 83 KB | 27 个模板中的 **14 个**（结构化 JSON：en/zh 双语 title / description / useWhen + `tagLabels` 34 个 + `categories` 6 类） | ⭐⭐⭐ 高 |
| 4 | `templates-local.json` | 112 KB | 另外 **13 个模板** + 对上面 14 个的 `overrides` 改写层 | ⭐⭐⭐ 高 |
| 5 | `site-skills.json` | 58 KB | goodcase.ai 上 **65 个视频 Skill 目录**（21 官方 + 44 创作者方法），含分类与案例数 | ⭐⭐ 中 |
| 6 | `skills.json` | 41 KB | README 网格用的 **36 个技能**卡片（标题 / 简介 / coverColor / install 命令） | ⭐⭐ 中 |
| 7 | `site.json` | 607 B | 站点总量快照：1757 案例 / 1057 视频 / 434 创作者 / 复测花费 $300+ | ⭐ 低 |
| 8 | `stats.json` | 397 B | 汇总统计：834 案例 / 80 技能 / 27 模板 / 6 类 / 495 次复测 / 稳定度均分 78 | ⭐ 低 |
| 9 | `fixtures/cases.fixture.json` | — | 10 条**占位**案例（纯测试用） | ✗ 不需要 |
| 10 | `fixtures/style-library.fixture.json` | — | 2 个**占位**模板（纯测试用） | ✗ 不需要 |

**关键发现**：`style-library.json`(14) + `templates-local.json`(13) = **27 个模板的结构化数据**，正好对应本项目 `style-library.md` 里的 27 个模板。也就是说——**27 个模板有 JSON 版**，现在项目里用的是 Markdown 版。

---

## 2. 文档层 `docs/`（95 文件 / 12 MB）

| # | 内容 | 体积 | 说明 | 优先级 |
|---|---|---|---|---|
| 11 | `templates/zh/*.md` **27 篇 + README** | 331 KB（总字符） | **每个模板独立成篇的展开版**，平均 ~12 KB/篇（最大 `game-ui-livestream.md` 13.9 KB）。README 里有分类导航 + 每模板"已归类案例数" | ⭐⭐⭐ **最高** |
| 12 | `templates/en/*.md` 27 篇 + README | 420 KB | 同上英文版 | ⭐ 低 |
| 13 | `gallery-seedance-2-5-part-{1..7}.zh.md` | 2.5 MB | **Seedance 2.5 全 550 条案例**中文合集，按热度排序，每条含海报图 / 作者 / 原帖 / 热度 / 稳定度 / 复测 / 可折叠完整 prompt | ⭐⭐ 中高 |
| 14 | `gallery-seedance-2-0-part-{1..4}.zh.md` | 1.1 MB | **Seedance 2.0 全 284 条案例**中文合集（同上格式） | ⭐⭐ 中高 |
| 15 | `gallery.md` / `gallery.zh.md` / `gallery.ja.md` | 15 KB | 画廊总览 + 分页导航（三语） | ⭐ 低 |
| 16 | `skills.md` / `skills.zh.md` / `skills.ja.md` | 83 KB | 65 个站点 Skill 目录页（三语），含一行安装命令 | ⭐ 低 |
| 17 | 日文/英文大文档（`README_ja.md` 142 KB、`README.md` 136 KB、`README_zh.md` 132 KB） | 409 KB | upstream 三语 README（`README_zh.md` 可作为本项目 README 的内容参考） | ⭐ 低 |

**关键发现**：`docs/templates/zh/` 是 **331 KB / 27 篇**，而本项目正在用的 `skills/seedance-prompt-library/references/style-library.md` 是 **139 KB / 27 个模板**。→ **上游的展开版信息量是现在用的 2.4 倍**，且是中文、按模板拆成独立文件。

---

## 3. 工程层 `scripts/` + `.github/` + `package.json`（33 文件 / 401 KB）

| # | 文件 | 作用 | 优先级 |
|---|---|---|---|
| 18 | `generate-readme.mjs` | 从 `data/` 生成 README + `docs/gallery-*` + `docs/skills.*` | ✗ 不需要（Node 构建脚本，为 GitHub 仓库服务） |
| 19 | `generate-skill-reference.mjs` | 生成技能参考文档 | ✗ 不需要 |
| 20 | `generate-standalone-skills.mjs` | 把技能打平成"独立可装"形态（+ `lib/standalone-skill.mjs`） | ⭐ 可参考思路 |
| 21 | `fetch-site-stats.mjs` | 抓 goodcase.ai 站点数字（公开 API 列表上限 50 条，只能抓 HTML） | ⭐⭐ 中（数据更新用） |
| 22 | `fetch-retest-posters.mjs` | 用 **ffmpeg** 从复测视频抽封面图 | ✗ 不需要 |
| 23 | `check-links.mjs` | 全库链接体检 | ✗ 不需要 |
| 24 | `weekly-taxonomy.mjs` / `taxonomy-todo.mjs` | 每周给未归类案例分配模板 / 列出待办 | ⭐⭐ 中（案例归类用） |
| 25 | `validate-submissions.mjs` + `lib/submissions.mjs` | 投稿 JSON 字段校验 | ✗ 不需要 |
| 26 | `lib/*.mjs` 9 个模块 | `library` / `render` / `sections` / `skill-list` / `standalone-skill` / `submissions` / `templates` / `utm` / `weekly-taxonomy` | ✗ 不需要 |
| 27 | `lib/*.test.mjs` 8 个 | 上述模块的单元测试 | ✗ 不需要 |
| 28 | `run-weekly-taxonomy.sh` | 上面周任务的 shell 包装 | ✗ 不需要 |
| 29 | `.github/workflows/refresh-site-stats.yml` | 每天 09:30（北京）刷新站点数字 + 复测封面，重生成 README | ✗ GitHub 专用 |
| 30 | `.github/workflows/update-readme.yml` | `data/**` 或 `scripts/**` 变更时重生成派生文档 | ✗ GitHub 专用 |
| 31 | `.github/workflows/validate-submissions.yml` | PR 上校验投稿 JSON | ✗ GitHub 专用 |
| 32 | `.github/CODEOWNERS` + `pull_request_template.md` | 仓库协作配置 | ✗ 不需要 |
| 33 | `package.json` | npm scripts：`generate` / `test` / `check:links` / `taxonomy:*` / `validate:submissions` / `refresh:site` | ✗ 不需要 |

> 说明：整个 `scripts/` + `.github/` 是**为 upstream 那个 GitHub 仓库服务的 Node 流水线**，本项目是 Python + FastAPI 架构，直接照搬没有意义。有价值的是它的**数据更新思路**（见第 5 节）。

---

## 4. 发布 / 元数据层

| # | 内容 | 体积 | 说明 | 优先级 |
|---|---|---|---|---|
| 34 | `.claude-plugin/marketplace.json` | 8 KB | **插件市场清单**：15 个技能各带 `source` 路径 + `version 0.3.0` + `license MIT` + 简介 | ⭐⭐ 中（如果本项目的技能要能被别的 agent 装） |
| 35 | `submissions/TEMPLATE.json` + `README.md` | 1.8 KB | 案例投稿模板与流程（社区贡献入口） | ⭐ 低 |
| 36 | `assets/` | 1.5 MB | `hero.svg` + `goodcase-seedance-gallery.png`(892 KB) + `goodcase-retest-evidence.png`(477 KB) + `retests/` 3 张复测封面 jpg | ⭐ 低（README 配图） |
| 37 | `LICENSE`(MIT) / `code-of-conduct.md` / `contributing.md` / `.gitignore` | 14 KB | 开源仓库标准文件 | ⭐ 低 |

---

## 5. 我的建议

### ⭐⭐⭐ 值得同步（3 件）

1. **`docs/templates/zh/` 27 篇模板文档** ← 收益最大
   - 现在是 **139 KB 压缩版**（style-library.md），上游是 **331 KB 展开版**
   - 中文、单模板单文件，正好能当"按需读取"的参考资料
   - 直接放进 `skills/seedance-prompt-library/references/` 或做成分模板读取

2. **`data/cases.json` + `case-taxonomy.json`（834 案例 + 811 条归类）**
   - 这是整个仓库**最核心的资产**：真人核验 + 完整 prompt + 复测稳定性分
   - 有了 taxonomy，就能做到"用户说要做美食 ASMR → 先查库里有哪 31 条同类案例 → 参考它们的 prompt 结构"
   - ⚠️ 需要你决策：之前你说过"案例页整个不要了"。那这批数据是**当作智能体的参考料**用，还是彻底不碰？

3. **`data/style-library.json` + `templates-local.json`（27 模板的 JSON 版）**
   - 比 Markdown 更好结构化处理，带 en/zh 双语 + 34 个标签 + 6 个分类

### ⭐⭐ 看情况（2 件）

4. **`docs/gallery-*.zh.md`（834 条案例的离线合集）** —— 如果决定要案例能力，这就是现成的语料
5. **`fetch-site-stats.mjs` + `weekly-taxonomy.mjs` 的思路** —— 数据怎么自动更新的参考

### ✗ 不建议同步

- `scripts/` 全部 Node 构建脚本、`lib/` + 测试、`.github/`、`package.json`
- `fixtures/`（占位测试数据）、`assets/`、三语 README、LICENSE / CoC / contributing
- 理由：**这些是"维护 upstream 那个 GitHub 仓库"用的**，本项目是 Python 智能体，两套东西解耦更干净

### 📌 一个待你拍板的遗留项

`_参考_技能/seedance-prompt-lint` 和 `seedance-storyboard-writer` 这两个自有技能，现在还在参考资料目录里。要不要搬回 `skills/`？搬回来就是 17 个技能。

---

## 6. 这些数据是从 goodcase 网页抓来的吗？

**结论：不是。7 个里只有 1 个是真从网页抓的，而那个恰好是低价值的 `site.json`。**

来源分四类，每类的更新方式完全不同：

### ① 真·抓 goodcase 网页（1 个）

| 文件 | 怎么抓 | 频率 |
|---|---|---|
| `data/site.json` | `fetch-site-stats.mjs` 正则抓 `goodcase.ai/` 首页脚注「N 个案例 / N 位创作者」+ 案例页「当前结果 N」 | GitHub Actions 每天 09:30（北京） |

**为什么只能抓 HTML**：goodcase 公开 API 的列表接口**最多返回 50 条**，拿不到站点总数，只能从服务端渲染的 HTML 里正则抠。

→ 这个文件**不在**你列的 7 个里（我把它列在"低价值"）。

### ② goodcase 私仓导出 → push 到 GitHub（3 个）

| 文件 | 证据 |
|---|---|
| `data/cases.json` | `meta.exportedAt = 2026-10-14T22:09:26Z`，834 条 |
| `data/style-library.json` | `generatedFrom = { caseCount: 207, distilledAt: 2026-08-26 }`，来源注明"私仓蒸馏管线" |
| `data/site-skills.json` | 自述：*"Generated by the goodcase **private repo** … the **daily sync** overwrites it"* |

**决定性证据** —— `.github/workflows/update-readme.yml` 的注释：

> Data refresh comes from the **private goodcase.ai collection pipeline** exporting into `data/cases.json` / `data/style-library.json` and pushing that here — this workflow only regenerates the derived files, **it does not call any external API itself**.

⚠️ **也就是说：`cases.json` 那 834 条完整 prompt + 复测记录，靠爬网页是拿不到的**——只有 goodcase 私仓能产出，导出后 push 进公开仓库。

### ③ 仓库里手写 / 半自动（3 个）

| 文件 | 谁在维护 |
|---|---|
| `data/templates-local.json` | **纯手写**。自述：*"everything hand-written lives here"*（27 个模板里 13 个 + 对另外 14 个的 `overrides` 改写） |
| `data/skills.json` | 标题 / 简介 / 安装命令**手写**；**只有封面图** `cover` 由 `fetch-site-stats.mjs` 抓 goodcase.ai 技能页 |
| `data/case-taxonomy.json` | **半自动**。早期手工标（2026-09-22 标到 463 条 → 10-02 扩到 624 条）；之后由 `weekly-taxonomy.mjs` **每周一自动跑**（跑在维护者本机 LaunchAgent 上，AI 打标 + 闸门校验 → 通过才 `commit + push`） |

### ④ 从 `data/` 本地派生（2 个，不是外部来源）

| 文件 | 怎么来的 |
|---|---|
| `docs/templates/zh/*.md` 27 篇 | `npm run generate` 从 `data/` 生成。文件头注：*"由 data/ 生成，请勿手改；改 data/templates-local.json 后跑 npm run generate"* |
| `docs/gallery-*.zh.md` | 同上，从 `cases.json` 派生。文件头注：*"由 data/cases.json 生成，请勿手改"* |

---

### 完整链路

```
goodcase 私仓管线 ──push──▶ data/cases.json ─────┐
                                                 ├──▶ npm run generate ──▶ docs/templates/zh/ 27 篇
仓库手写 templates-local.json ───────────────────┤                     └──▶ docs/gallery-*.zh.md
                                                 │
本机 LaunchAgent（每周一）──▶ case-taxonomy.json ─┘

goodcase.ai 网页 ──正则抓 HTML──▶ data/site.json（唯一真·抓取）
                                  data/skills.json 的封面字段
```

---

### 对本项目的实际影响

| 事项 | 说明 |
|---|---|
| **能自动更新吗** | ❌ 本项目里只是**一次快照**。`cases.json` 等文件拷过来后就是死的，不会自动跟着 goodcase 更新 |
| **要更新怎么办** | 只能重新从 upstream 仓库拉最新文件（或让 goodcase 那边 push 后再同步一次） |
| **`docs/templates/zh/` 能直接用吗** | ✅ 可以，它是**静态文档**，不依赖网络，拷过来就是成品 |
| **`docs/gallery-*.zh.md` 呢** | ✅ 同样是静态成品，但它内嵌了 `media.goodcase.ai` 的图片外链——离线看不到图 |
| **有没有必要抓 goodcase 网页** | 基本没意义。真正值钱的 `cases.json` / `style-library.json` / `site-skills.json` **都在私仓里**，公开网页抓不到 |
| **唯一值得自己实现的** | `fetch-site-stats.mjs` 的思路（正则抠首页数字）——但只对 `site.json` 这种"总量统计"有效 |
