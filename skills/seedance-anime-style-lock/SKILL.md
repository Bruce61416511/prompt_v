---
name: seedance-anime-style-lock
description: "Specify the drawing style as measurable parameters, then attach an exclusion list of the neighbouring styles it must not fall into. Without the exclusion list, anime collapses into a generic 3D face. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (Anime and stylized style lock; 中文触发词: 动漫与风格化画风固定, 动漫, 二次元, 画风, 动画风格), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# Anime and stylized style lock · 动漫与风格化画风固定

Specify the drawing style as measurable parameters, then attach an exclusion list of the neighbouring styles it must not fall into. Without the exclusion list, anime collapses into a generic 3D face.

This Skill carries one prompt structure distilled from 31 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- Cel-look action, Ghibli-flavoured slice of life, 3D toon RPG battles, 2D hand-drawn cooking. Roughly a quarter of the corpus is stylized animation of some kind.
- 中文：赛璐珞动作戏、吉卜力味日常、3D 卡通 RPG 战斗、2D 手绘烹饪。案例库里大约四分之一是各类风格化动画。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. Style lock block: line weight, number of cel shading steps, highlight layering, per-material reflectance
   2. Exclusion list: the adjacent styles that must not appear
   3. Character and palette lock: signature colours pulled from the reference, forbidden from swapping between characters
   4. Stage and atmosphere: how the environment is re-tinted toward the character palette
   5. Camera order and action
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Write the style as parameters: thin coloured contour lines, two to three steps of cel shading with translucent mid-shadow, multi-layer highlights in irises and hair, and distinct reflectance and roughness for cloth, leather, metal, gems, wet floor and glass.
- Always attach the exclusion list. The anime duel case rules out thick black outlines, flat single-layer cel shadow, low-budget TV-anime look, generic 3D pretty-girl face, smooth plastic CG, semi-photoreal, photoreal, low-density backgrounds and muddy colour.
- Extract a signature colour set per character from the reference — main colour, support colour, accent colour, material motif — name them and forbid trading them between characters.
- Push the background one step darker than the characters and use each character's signature colour as their key light and shadow tint. This is what reads as 2D rather than as rendered 3D.
- For healing-genre Ghibli work, subtract motion instead of adding it. The forest cooking case shows only a pair of hands, no faces at all, and covers gathering, slicing, simmering and serving in four shots.

## Pitfalls

- Writing anime style without naming a school. The model averages across everything it knows and returns a generic face.
- Mixing 2D hand-drawn vocabulary with 3D toon-render vocabulary. They are two different word sets and blending them lands on semi-photoreal.
- Fast action degrading cel shadow into realistic lighting. Restate the shading spec inside the high-speed segments.
- Letting text, logos or UI appear in the scene. Anime backgrounds attract garbled signage unless it is banned outright.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：动漫与风格化画风固定

把画风写成可测量参数，再附一份相邻画风的排除清单。没有排除清单，动漫会塌成通用 3D 脸。

**结构:**

1. 画风固定块：线条粗细、赛璐珞阴影段数、高光层次、逐材质反射差异
2. 排除清单：不许出现的相邻画风
3. 角色与配色锁：从参考图抽出的固有色，禁止在角色之间交换
4. 舞台与氛围：环境如何向角色配色靠拢
5. 摄影机顺序与动作

**要点:**

- 画风写成参数：细而有色的轮廓线、二到三段赛璐珞阴影加透明感中间影、瞳孔与头发的多层高光、布革金属宝石湿地面玻璃各自不同的反射与粗糙度。
- 一定要附排除清单。动漫剑戟那条排除了粗黑轮廓、单层平涂阴影、低成本 TV 动画感、通用 3D 美少女脸、塑料 CG 感、半写实、写实、低密度背景和浑浊色彩。
- 从参考图给每个角色抽一组固有色——主色、辅助色、点缀色、材质母题——命名之后禁止在角色之间交换。
- 背景压得比角色暗一档，并用各角色的固有色当主光和影色。这是读成 2D 而不是渲染 3D 的关键。
- 治愈系吉卜力要做减法。森林烹饪那条全片只拍一双手，一张脸都不出，四个镜头做完取材、切配、炖煮、成菜。

**常见坑:**

- 只写 anime style 不指名流派。模型会在它知道的一切之间取平均，还你一张通用脸。
- 把 2D 手绘词表和 3D 卡通渲染词表混着写。这是两套词，混出来是半写实。
- 快动作会让赛璐珞阴影退化成写实光影。要在高速段里重申一次上色规格。
- 让文字、logo、UI 出现在画面里。动漫背景特别容易长出乱码招牌，除非明确禁掉。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want an animated clip whose art style stays locked. [Style: 1990s cel-shaded Japanese animation; I am sending you style references.] [Content: a girl on a broomstick gliding over a seaside town at dusk.] Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一条画风固定的动画短片，【画风是：九十年代赛璐璐日式动画，我会发给你风格参考图】，【内容是：少女骑着扫帚掠过黄昏的海边小镇】。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
