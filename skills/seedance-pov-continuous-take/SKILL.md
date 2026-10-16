---
name: seedance-pov-continuous-take
description: "Bodycam, GoPro, FPV and handlebar POV. The camera is mounted on a body, so its motion has to be derived from that body, and every cut has to be declared by hand. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (First-person continuous take; 中文触发词: 第一人称一镜到底, 第一人称, 一镜到底, POV, 运动相机, GoPro), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# First-person continuous take · 第一人称一镜到底

Bodycam, GoPro, FPV and handlebar POV. The camera is mounted on a body, so its motion has to be derived from that body, and every cut has to be declared by hand.

This Skill carries one prompt structure distilled from 14 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- Immersive footage where the viewer is the operator: tactical entry, action sports, cooking from the cook's eyes, drone flight. 32 of 207 cases sit here.
- 中文：要观众就是操作者的沉浸素材：破门突入、极限运动、厨师视角做饭、无人机飞行。207 条里 32 条属于这类。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. SCENE CONTEXT: one paragraph naming the subject, the mount and the total duration
   2. ACTIVE REFERENCES: named tokens for location, hands and props
   3. LOCATION MAP: what sits in foreground, midground and background per segment, plus camera height
   4. FIRST FRAME / BLOCKING: a non-empty opening frame, already mid-action
   5. FORMAT MODE: where the hard cuts fall and which stretches are one continuous take
   6. OPTICS: field of view per segment, with a no-drift clause
   7. Timeline and audio
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Declare the physical mount and its height so the model can derive the shake: chest-mounted on the point agent, POV chest-to-eye height, moving only with the body.
- Refuse an empty first frame. The GoPro fishing case writes `Non-empty opening frame: already mid-cast, rod raised, line already peeling off the reel`, which removes the dead first second.
- Separate one-take from cutting. Write the cut plan as an explicit list — A 0-9s river, one continuous take, HARD CUT, B 9-21s board, one continuous take — and add that the camera does not cut anywhere else.
- Pin the field of view per segment in degrees (84° easing to 63° through the fight, 63° easing to 18° across the next block) and follow it with `No drift within any segment`.
- Spell out the optical consequences of a body mount: wide-angle distortion at the edges, vertical bob from walking, motion blur on fast head turns, and a flashlight beam that only lights what the operator faces.

## Pitfalls

- The operator's own face appearing in frame. Add `the camera itself is never visible` and describe only what the hands do.
- Hands entering frame without a left or right assignment. Say which hand holds what, or a third hand grows in.
- Scheduling a large scene jump inside a stretch labelled one continuous take. Either walk there in real time or put a declared hard cut at the boundary.
- Forgetting to ban cinematic treatment. Bodycam and action-cam material needs an explicit `no slow-motion, no cinematic grading` or it turns into a movie trailer.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：第一人称一镜到底

执法记录仪、GoPro、FPV 和车把视角。相机挂在身体上，运动必须从身体推导，每一次剪辑都得手动声明。

**结构:**

1. SCENE CONTEXT：一段话交代主体、挂载方式和总时长
2. ACTIVE REFERENCES：场景、手和道具的命名 token
3. LOCATION MAP：每段的前景、中景、背景各是什么，以及机位高度
4. FIRST FRAME / BLOCKING：首帧非空，开场就在动作中间
5. FORMAT MODE：硬切落在哪里，哪几段是连续一镜
6. OPTICS：每段的视场角，附一句段内不许漂移
7. 时间轴与音频

**要点:**

- 声明挂载位置和高度，模型才能推出该怎么晃：胸挂在破门手身上、POV 保持胸到眼的高度、只随身体移动。
- 拒绝空首帧。GoPro 钓鱼那条写 `Non-empty opening frame: already mid-cast, rod raised, line already peeling off the reel`，把死掉的第一秒省掉了。
- 一镜到底和剪辑要分开声明。剪点写成清单——A 0-9s 河边一镜，HARD CUT，B 9-21s 案板一镜——再补一句除此之外相机不剪。
- 视场角逐段写成度数（84° 在搏斗中收到 63°，下一段 63° 收到 18°），后面跟一句 `No drift within any segment`。
- 把身体挂载的光学后果写出来：边缘广角畸变、行走造成的上下颠动、快速转头的运动模糊、手电只照亮操作者面向的方向。

**常见坑:**

- 操作者自己的脸入画。补一句 `the camera itself is never visible`，只描述手在做什么。
- 手入画却不说左右手和持物。要写清哪只手拿什么，否则会长出第三只手。
- 在标了一镜到底的段落里安排跨场景大跳。要么实时走过去，要么在边界放一个声明过的硬切。
- 忘了禁掉电影化处理。执法记录仪和运动相机素材要明写 no slow-motion, no cinematic grading，否则会变成电影预告片。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want a first-person clip in one continuous take. [My point of view: riding a mountain bike down a forest trail.] [My hands and the handlebars should stay in frame.] Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一条第一人称一镜到底的视频，【我的视角是：骑着山地车从林道冲下山】，【画面里要出现我的双手和车把】。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
