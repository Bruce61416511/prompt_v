---
name: seedance-process-transformation-montage
description: "Cooking steps, renovation timelapse, blueprint-to-house, miniature city assembly. The craft here is declaring what must not change, then ordering the change spatially. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (Process and transformation montage; 中文触发词: 流程与变换蒙太奇, 过程蒙太奇, 改造, 延时, 制作流程, 组装), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# Process and transformation montage · 流程与变换蒙太奇

Cooking steps, renovation timelapse, blueprint-to-house, miniature city assembly. The craft here is declaring what must not change, then ordering the change spatially.

This Skill carries one prompt structure distilled from 19 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- Any clip whose subject is a process rather than a person: recipes, builds, assemblies, before-and-after reveals. 35 cases in the corpus.
- 中文：主角是过程而不是人的片子：菜谱、建造、组装、前后对比。案例库里 35 条。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. Invariants block: what stays fixed — camera, geometry, layout, scale
   2. Initial state, described concretely
   3. Ordered transformation segments, each with a spatial direction
   4. Final state plus a short life-signs beat
   5. Sound: assembly clicks, ambience, and whether dialogue exists at all
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Spend a whole paragraph on invariants. The renovation case locks camera position, angle, focal length, perspective and composition, then separately locks room dimensions, walls, windows, doors, ceiling height and structural layout.
- Order the change spatially, not vaguely. Flooring spreads left to right, then walls and ceiling transform simultaneously, then furniture lands — this beats gradually transforms every time.
- When two references define different things, say which defines what. The blueprint case declares the floor plan as the source of layout and dimensions, and the exterior photo as the source of architectural style, then forbids any room from moving.
- For cooking, hands only, no faces. That removes the identity budget entirely and lets all detail go to the ingredients.
- Close with a life-signs beat rather than a freeze: water shimmers, flags move, a lighthouse beam rotates, windows light up. The miniature harbour case bans an ending that is completely static.

## Pitfalls

- Moving the camera during the transformation. Any camera motion competes with the change itself, and the audience loses the before-and-after anchor.
- Assembly montages drifting toward toy scale. The miniature case devotes a NEGATIVE block to excluding an island that is too small, a cramped harbour, cheap plastic feel and a town of only a few houses.
- Combining timelapse and slow motion in one segment. Pick one temporal treatment per beat.
- Running more than about six steps in one prompt. Beyond that, split into two generations and stitch.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：流程与变换蒙太奇

烹饪步骤、改造延时、蓝图变房子、微缩城市组装。这类的手艺在于先声明什么不许变，再把变化按空间顺序排开。

**结构:**

1. 不变量块：什么固定不动——机位、几何、布局、尺度
2. 起始状态，写具体
3. 有序变换段，每段带一个空间方向
4. 终态，外加一小段生命感
5. 音效：组装声、环境音，以及到底有没有对白

**要点:**

- 拿一整段写不变量。改造那条锁了机位、角度、焦段、透视、构图，再单独锁了房间尺寸、墙、窗、门、层高和结构布局。
- 变化按空间顺序排，不要含糊。地面从左到右铺开，然后墙和天花板同时变，然后家具落位——这比 gradually transforms 强得多。
- 两张参考图各定义不同东西时要说清谁定义什么。蓝图那条声明平面图是布局和尺寸的来源、外立面照片是建筑风格的来源，再禁止任何房间移位。
- 烹饪类只拍手不拍脸。身份预算直接归零，细节全给食材。
- 收尾给生命感而不是定格：水面反光、旗子飘、灯塔光束转、窗户亮灯。微缩港口那条明确排除了完成后完全静止的结尾。

**常见坑:**

- 变换过程中还运镜。任何机位运动都在跟变化本身抢注意力，观众也丢了前后对比的锚点。
- 组装蒙太奇越拍越小变成玩具感。微缩那条专门用一个 NEGATIVE 块排除了岛太小、港口局促、廉价塑料感和只有几栋房子的小镇。
- 一段里同时用延时和慢动作。每一拍只用一种时间处理。
- 一条 prompt 里排超过六个步骤。超了就拆成两次生成再拼。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want a process and transformation montage. [The process: dough going from kneading to a finished croissant out of the oven.] [Locked overhead camera, 12 seconds.] Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一条过程与变换的蒙太奇，【要展示的过程是：一块面团从揉面到出炉变成牛角包】，【机位固定俯拍，时长 12 秒】。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
