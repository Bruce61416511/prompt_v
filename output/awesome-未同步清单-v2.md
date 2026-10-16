# awesome-seedance 未同步清单 · v2（更新版）

对比时间：2026-10-16 15:45
对比对象：`_参考_技能/awesome-seedance/` → 本项目 `提示词智能体/`
上一版：`output/awesome-未同步功能清单.md`（37 项，那一版的 A 档已全部搬完）

---

## 0. 已经搬过来的（基线）

| 层 | 内容 | 上游体积 | 状态 |
|---|---|---|---|
| `skills/` 15 个 upstream 技能 | 13 个场景技能（各含 SKILL.md + `references/cases.md`）+ `seedance-prompt-library` + `seedance-production-workflow` | 733 KB | ✅ **字节一致** |
| `data/` 8 个 JSON | `cases.json`(4.06 MB) / `case-taxonomy.json` / `style-library.json` / `templates-local.json` / `site-skills.json` / `skills.json` / `site.json` / `stats.json` | 4.4 MB | ✅ **零差异** |
| `docs/templates/zh/` 28 篇 | 27 个模板的中文展开版 + README | 331 KB | ✅ **零差异** |
| `docs/gallery-*.zh.md` | 2.0 全 4 篇 + 2.5 全 7 篇 + `gallery.zh.md`，共 12 篇 | 3.6 MB | ✅ |

> 也就是说：**技能层、数据层、中文文档层——三层都已经没有欠账了。**

---

## 1. 还没搬的：A 档 · 有实际用途（3 类）

### A1 ⭐⭐⭐ 两个自有技能还在 `_参考_技能/` 里，没进 `skills/`

| 技能 | 文件 | 说明 |
|---|---|---|
| `seedance-prompt-lint` | `SKILL.md` + `references/checklist.md` | 提示词质检清单 |
| `seedance-storyboard-writer` | `SKILL.md` | 分镜脚本撰写 |

搬进来 = **29 → 31 个技能**。

**⚠️ 这里有个正在生效的副作用**：`app/agent.py` 的 `lint()` 是这么找质检技能的 ——

```python
skill_name = next((n for n in self.loader.names() if "lint" in n.lower()), None)
if not skill_name or skill_name not in self.loader.skills:
    return {"content": "（未找到质检类 skill，跳过质检）", "skills_used": []}
```

而 `skills/` 里**没有名字含 `lint` 的技能** → 所以流水线的 ④ 质检阶段**现在是死的**。
实测日志可以印证：

```
[picked] {'skills': ['seedance-timeline-shot-script'], 'source': 'user'}
[generated] {'chars': 2569}
[lint_skipped] {'reason': '本次没有选中质检技能，跳过质检'}
```

> **把 `seedance-prompt-lint` 拷进 `skills/` 目录，质检环节就自动复活**，代码一行都不用改。

### A2 ⭐⭐ `docs/templates/en/` 28 篇 / 420 KB

27 个模板的**英文展开版**（中文版已在 `docs/templates/zh/`）。
用途：如果以后要输出英文提示词，这是现成的英文素材；不做英文输出就不必搬。

### A3 ⭐ `scripts/` 27 个 mjs / 376 KB

| 模块 | 体积 | 作用 | 状态 |
|---|---|---|---|
| `generate-standalone-skills.mjs` + `lib/standalone-skill.mjs` + `lib/library.mjs` | 3.4 + 7.8 + 5.7 KB | 生成 27 个场景技能（SKILL.md + cases.md） | ✅ **已用 Python 重写** → `scripts/build_extra_skills.py` |
| `weekly-taxonomy.mjs` + `lib/weekly-taxonomy.mjs` | 12 + 16 KB | **每周一给新案例自动归类到 27 个模板** | ❌ 未重写 |
| `check-links.mjs` | 3.7 KB | 批量检查案例链接是否失效 | ❌ 未重写 |
| `lib/templates.mjs` + `lib/render.mjs` + `lib/sections.mjs` | 33 + 44 + 26 KB | README / docs 渲染引擎 | ❌ 未重写 |
| `fetch-site-stats.mjs` / `fetch-retest-posters.mjs` | 3.5 + 1.8 KB | 联网抓站点统计 / 复测封面 | ❌ 未重写 |
| `validate-submissions.mjs` + `lib/submissions.mjs` + `taxonomy-todo.mjs` | 1.5 + 3.2 + 1.5 KB | 投稿校验 / 归类待办 | ❌ 未重写 |
| `lib/*.test.mjs` 7 个 | 137 KB | Node 单测 | ✗ 用不上 |

**关键缺口是 `weekly-taxonomy`**：它负责"新案例 → 归到哪个模板"。
我们现在**只搬了结果（`case-taxonomy.json` 811 条映射），没搬逻辑** →
上游以后新增案例，我们**没有能力自己把它们归组**，只能整包重新拷。

> 但这个逻辑依赖 Node + 上游目录结构，而且真正想用的话，用 Python 重写也就一两百行。
> 只有当你打算"自己维护案例分类"时才值得做。

---

## 2. 还没搬的：B 档 · 建站/发布用，跟智能体无关（4 类）

| # | 项 | 体积 | 说明 |
|---|---|---|---|
| B1 | `README_zh.md` | 132 KB | 上游中文 README，是**本项目 README（16 KB）的 8 倍**：27 个模板全部展开 + 每个模板下的完整案例清单 |
| B2 | `docs/` 根剩下 27 篇 | 7.0 MB | 英文 gallery 11 篇 + 日文 gallery 11 篇 + `gallery.md` / `gallery.ja.md` + `skills.md` / `skills.zh.md` / `skills.ja.md`。**只有做三语对照站才需要** |
| B3 | `assets/` 6 个文件 | 1.5 MB | README 配图：`hero.svg`、2 张站点截图、`retests/` 下 3 张复测示例帧 |
| B4 | `.claude-plugin/marketplace.json` | 8 KB | 把 15 个技能登记成 Claude Code 插件市场的清单（含每个技能的英文简介 + 版本号 0.3.0） |

---

## 3. 还没搬的：C 档 · 用不上（6 类）

| # | 项 | 体积 | 为什么不用 |
|---|---|---|---|
| C1 | `.github/` 5 个文件 | 25 KB | 三个 CI：每天抓站点统计、PR 校验投稿、push 后重生成 README。**本项目没有 GitHub 仓库，跑了也没用** |
| C2 | `submissions/` 2 个文件 | 8 KB | 投稿模板（给外部贡献者用的） |
| C3 | `contributing.md` / `code-of-conduct.md` | 16 KB | 开源协作规范 |
| C4 | `LICENSE` | 4 KB | MIT。**若想合法沿用上游内容，建议把 LICENSE 一起保留** |
| C5 | `package.json` / `.gitignore` | 5 KB | npm 工程文件，本项目用 Python |
| C6 | `data/fixtures/` 2 个 | 28 KB | 单测用的 10 条占位案例、2 个占位模板 |

---

## 4. 汇总

| 档 | 项数 | 体积 | 建议 |
|---|---|---|---|
| **A 档**（有实际用途） | 3 类 | ~800 KB | **A1 强烈建议搬**（能救活质检），A2/A3 按需 |
| **B 档**（建站/发布） | 4 类 | ~8.6 MB | 现在不用搬 |
| **C 档**（用不上） | 6 类 | ~86 KB | 只有 LICENSE 建议保留 |

**未同步总量：约 6.8 MB / 65 个文件。**

### 一句话结论

**真正值得动手的只有一件**：把 `_参考_技能/seedance-prompt-lint` 和 `seedance-storyboard-writer` 拷进 `skills/`。
前者能立刻让流水线第 ④ 步「质检」从"永远跳过"变成"真正运行"，后者补上"分镜脚本撰写"这个能力。
其余 6.7 MB 全是建站素材和开源规范文件，对"自动 load skill 的提示词智能体"没有帮助。
