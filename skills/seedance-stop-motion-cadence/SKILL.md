---
name: seedance-stop-motion-cadence
description: "Stop motion is a timing spec before it is a look. Pin the frame rate and the hold count, name the craft material, and ban the three things that silently smooth it away. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (Stop motion and stepped cadence; 中文触发词: 定格动画与步进节奏, 定格动画, 逐帧, 停格, 黏土), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# Stop motion and stepped cadence · 定格动画与步进节奏

Stop motion is a timing spec before it is a look. Pin the frame rate and the hold count, name the craft material, and ban the three things that silently smooth it away.

This Skill carries one prompt structure distilled from 10 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- Claymation, paper-cut, moving-oil-painting, collage and tabletop object animation. 24 cases in the corpus sit in this family.
- 中文：黏土、剪纸、会动的油画、拼贴、台面物件动画。案例库里 24 条属于这一族。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. Cadence declaration: frames per second, frames held per pose, snap not glide
   2. Craft material, with adjacent materials explicitly excluded
   3. Negative block: no smooth interpolation, no motion blur, no morphing
   4. Camera and surface: locked overhead or locked stage, no hands, no extra objects
   5. Segment-by-segment transformation of the subject
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Pin the cadence numerically: `True 12fps, ANIMATED ON TWOS: 12 distinct hand-painted drawings per second, each pose held two frames then snapping to the next, never gliding`.
- Name the material and exclude its neighbours in the same breath. The wolf-attack case writes a hand-painted 2D look, a moving oil painting, NOT clay, NOT puppets, NOT 3D.
- The negative trio is mandatory: NO smooth interpolation, NO motion blur, NO morphing. These three are the main routes by which stepped motion gets silently smoothed back out.
- For tabletop work, lock the camera completely — perfectly locked top-down overhead, no camera movement, no hands, no surrounding objects — and let only the subject change.
- Add craft imperfections as requirements: uneven handmade edges, tiny positional jitter between poses, an occasional one-frame motion smear, and a constant painterly boil in the outlines.

## Pitfalls

- Not separating environment motion from subject motion. Blizzard haze, smoke and water may drift smoothly while figures step on twos, but you have to say so or everything smooths out together.
- Asking for stop motion and a long moving camera shot at once. These are contradictory requirements and the camera move usually wins.
- Requesting clay and paper in the same prompt. Their light behaviour differs, and the model blends them into an ambiguous surface.
- Keeping normal-scale action at 12fps. Stepped animation drops readability on fast motion, so exaggerate the pose amplitude.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：定格动画与步进节奏

定格首先是时间规格，其次才是质感。写死帧率和保持帧数，指名工艺材质，再禁掉那三样会悄悄把它抹平的东西。

**结构:**

1. 节奏声明：每秒帧数、每个姿势保持几帧、跳变而不是滑动
2. 工艺材质，并显式排除相邻材质
3. 负向块：不插值、不运动模糊、不形变过渡
4. 机位与台面：锁死俯拍或锁死舞台，不出现手，不出现多余物件
5. 被摄物的逐段变形

**要点:**

- 节奏用数字写死：`True 12fps, ANIMATED ON TWOS: 12 distinct hand-painted drawings per second, each pose held two frames then snapping to the next, never gliding`。
- 指名材质的同时排除相邻材质。狼群袭击那条写的是手绘 2D 质感、会动的油画，NOT clay、NOT puppets、NOT 3D。
- 负向三件套是必需的：NO smooth interpolation、NO motion blur、NO morphing。步进感被悄悄抹平，主要就走这三条路。
- 台面类要把机位锁死——perfectly locked top-down overhead、无机位运动、不出现手、不出现周边物件——只让被摄物变。
- 工艺瑕疵要写成要求：手工不齐的纸边、姿势之间的微小位移抖动、偶尔一帧的拖影、轮廓持续的画面 boil。

**常见坑:**

- 没有把环境运动和主体运动分开。风雪、烟、水可以平滑漂移，人物和道具要步进，不写清楚就会一起被平滑掉。
- 同时要定格和长镜头运动。这是互斥需求，通常是运镜赢。
- 同一条里既要黏土又要纸片。两者的光影逻辑不同，模型会混成一种说不清的表面。
- 12fps 下还用常规动作幅度。步进动画在快动作上会丢可读性，姿势幅度要放大。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want a clip with a stop-motion feel. [Materials: felt and clay.] [Content: a little felt fox pitching a tent in the forest.] [The stepped, frame-by-frame cadence should be obvious.] Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一条定格动画质感的短片，【材质是：毛毡和黏土】，【内容是：一只毛毡小狐狸在森林里搭帐篷】，【要有明显的逐帧步进感】。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
