---
name: seedance-ugc-creator-review
description: "A creator unboxes, handles and endorses a product on camera. Two independent locks are needed — one on the person, one on the product — and the spoken lines are welded into the actions. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (UGC creator review with spoken lines; 中文触发词: UGC 口播测评带货, 口播, 测评, 开箱, 种草, 带货), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# UGC creator review with spoken lines · UGC 口播测评带货

A creator unboxes, handles and endorses a product on camera. Two independent locks are needed — one on the person, one on the product — and the spoken lines are welded into the actions.

This Skill carries one prompt structure distilled from 15 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- Affiliate-style product videos, unboxings and creator reviews where the product must stay recognisable while being picked up, rotated and worn.
- 中文：带货型产品视频、开箱和创作者测评：产品要在被拿起、旋转、佩戴的过程中始终认得出来。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. Character lock paragraph (face, hair, makeup, skin tone, proportions, full outfit)
   2. Product lock paragraph, structurally decomposed
   3. Setting and light: room, time of day, handheld smartphone feel
   4. Beat flow: unbox, detail rotation, wear or use, mirror or camera check, place-back
   5. Spoken lines placed inline at the beat where they are said
   6. Requirements tail: aspect ratio, duration, realistic hands, no logos or watermarks
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Lock the product separately from the person and decompose it into parts. The sunglasses review names frame shape, lenses, hinges, colours, materials and proportions, and locks the retail box and leather case as their own references.
- Put each line inline at its moment. The coffee-machine ad places `I finally tried this coffee machine` on the second the creator walks into the kitchen, not in a separate dialogue section.
- Write the copy as first-person sensation rather than ad language. The lines that work read like `The finish feels amazing, and they're incredibly lightweight`, not like a slogan.
- End on a fixed two-part hero beat: the product alone in frame, then the creator holding it and looking at the camera. All 16 ad-type cases in the corpus close this way.
- Add `realistic hands` explicitly. Product handling is where finger count fails, and hands are on screen for most of this format.

## Pitfalls

- Holding a macro shot on a printed label. Brand text is almost always rendered wrong; either keep the tight shots off the text or require an unbranded surface.
- Asking the creator to walk and perform a fine product manipulation at the same time. Split them into two beats.
- Letting the spoken line run long. When lip sync slips, cut the sentence rather than adding lip-sync adjectives.
- Requesting on-screen slogans from the model. Generated typography comes out garbled; leave a clean tail frame and add text in post.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：UGC 口播测评带货

创作者对着镜头开箱、上手、种草。要两把独立的锁——一把锁人，一把锁产品——台词焊进动作里。

**结构:**

1. 人物锁定段（脸、发型、妆、肤色、比例、整套服装）
2. 产品锁定段，按结构拆开写
3. 场景与光线：房间、时段、手持手机质感
4. 节拍流程：开箱、细节旋转、佩戴或使用、对镜或对镜头确认、放回
5. 台词就写在它被说出的那一拍里
6. 需求收尾：画幅、时长、realistic hands、no logos or watermarks

**要点:**

- 产品锁和人物锁分开写，并把产品拆成结构件。太阳镜测评那条点名了镜框形状、镜片、铰链、颜色、材质、比例，还把零售盒和皮套各自当独立参考锁住。
- 台词写在它发生的那一拍里。咖啡机广告把 `I finally tried this coffee machine` 放在创作者走进厨房的那一秒，不另开对白区。
- 文案写成第一人称感受句，不写广告腔。生效的台词读起来像 `The finish feels amazing, and they're incredibly lightweight`，不像 slogan。
- 收尾固定两拍：产品单独入画，然后创作者拿着产品看镜头。案例库里 16 条广告型案例全是这个收法。
- 显式补 `realistic hands`。产品上手是手指数量翻车的重灾区，而这类格式里手几乎全程在画面上。

**常见坑:**

- 微距镜头停在印刷标签上。品牌文字几乎必错，要么特写避开文字，要么直接要求无品牌表面。
- 让创作者边走边做精细的产品操作。拆成两拍。
- 台词写太长。口型对不上时应该砍句子，而不是加口型形容词。
- 让模型渲染上屏 slogan。生成的字排出来是乱码，应该留一个干净的收尾画面，文字后期加。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want a UGC creator review that sells a product. [My product is a bottle of shampoo; I am sending you the product photos.] [On camera: a woman with long hair, talking while she uses it in front of the bathroom mirror.] Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一个 UGC 口播测评带货视频，【我的产品是一瓶洗发水，产品图片我提供给你】，【出镜的人是一位长发女生，在浴室镜子前边用边讲】。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
