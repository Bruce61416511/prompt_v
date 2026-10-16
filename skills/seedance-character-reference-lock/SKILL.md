---
name: seedance-character-reference-lock
description: "Name every reference with a stable token, enumerate what to inherit from it, and separately enumerate what must not be inherited. The inherit-nothing-else clause is what separates working locks from broken ones. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (Reference image identity lock; 中文触发词: 参考图身份锁定, 参考图, 角色锁定, 人物一致性, 形象固定), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# Reference image identity lock · 参考图身份锁定

Name every reference with a stable token, enumerate what to inherit from it, and separately enumerate what must not be inherited. The inherit-nothing-else clause is what separates working locks from broken ones.

This Skill carries one prompt structure distilled from 9 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- Any clip where a face, an outfit, a product or a UI layout must survive across shots. Applies to Seedance 2.0 and 2.5 alike; 2.5 additionally accepts audio and video references under the same token scheme.
- 中文：任何需要一张脸、一套衣服、一个产品或一套 UI 布局跨镜头存活的片子。2.0 和 2.5 都适用，2.5 还能用同一套 token 语法引用音频和视频。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. Token declaration: give each reference a name — `@image1`, `@Image2`, `<<<image_1>>>`, `@location1`, `@hands1` — and reuse it verbatim everywhere
   2. Inherit list: enumerated attributes pulled from the reference (face shape, features, hair colour, body proportions, wardrobe items, accessories)
   3. Do-not-inherit list: background, room, furniture, pose, composition, framing, original lighting, any text
   4. Cross-shot clause: same face when turning, looking down, speaking, or with a hand near the face
   5. Negative: no cloning, no duplicates, no feature averaging, no attribute swaps between characters
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Split references by role and lock each separately. The GoPro fishing case declares `@location1` for the river and `@hands1` for the forearms, tools and bottle, each followed by `100% matches reference`.
- Enumerate the inherit list instead of writing keep her consistent. The boyfriend-POV case lists thirteen items: identity, features, face shape, skin tone, apparent age, hairstyle, hair colour, height, build, body proportion, clothing, footwear, overall bearing.
- Always add the do-not-inherit clause. Without it the reference's background, pose and lighting come along; the anime duel case spells out that the reference's background, room, furniture, text, split layout, pose, angle and framing must not be reproduced.
- For a UI or scene reference, separate composition lock from design lock. The character-select case marks `@image1` as LOCKED SCENE COMPOSITION and `@image2` through `@image6` as design-only, then adds DO NOT reproduce their reference poses.
- Identity drifts hardest during head turns, occlusion and fast motion. List those poses explicitly and restate the same-face requirement for the high-energy segments.

## Pitfalls

- Uploading a reference without any textual lock. The model then treats it as a style reference, not an identity reference.
- Compressing wardrobe into same outfit. Every working case in the corpus breaks the outfit into individually named garments and accessories.
- Feeding a sketch or illustration reference without a render instruction. Add use only as design blueprints, render as fully realistic live-action humans, or the line-art survives into the video.
- Adding references that no token names. Each unnamed extra image is one more chance for attributes to bleed between subjects.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：参考图身份锁定

给每张参考图一个稳定 token，逐条列出要继承什么，再单独列出不许继承什么。能不能生效，差别就在后面那条不继承声明。

**结构:**

1. Token 声明：给每张参考图起名——`@图1`、`@Image2`、`<<<image_1>>>`、`@location1`、`@hands1`——并全程原样复用
2. 继承清单：从参考图取哪些属性（脸型、五官、发色、身材比例、服装单品、饰品）
3. 不继承清单：背景、房间、家具、姿势、构图、画角、原始光线、任何文字
4. 跨镜头声明：转头、低头、说话、手靠近脸时保持同一张脸
5. 负向：禁止克隆、分身、五官平均化、角色之间属性互换

**要点:**

- 按角色拆参考图，分别锁定。GoPro 钓鱼那条把 `@location1` 用于河流场景、`@hands1` 用于前臂和工具器物，每个后面各跟一句 100% matches reference。
- 继承清单要逐条枚举，别写保持一致。男友视角那条列了十三项：身份、五官、脸型、肤色、年龄感、发型、发色、身高、体型、身体比例、服装、鞋履、整体气质。
- 一定要补不继承声明。少了这条，参考图的背景、姿势和原始光线会一起被搬进视频；动漫剑戟那条明写参考图的背景、房间、家具、文字、分割布局、姿势、画角、构图都不再现。
- UI 或场景参考要把构图锁和设计锁分开。角色选择界面那条把 `@image1` 标为 LOCKED SCENE COMPOSITION，`@image2` 到 `@image6` 只当设计参考，并补一句不许复制参考图里的站姿。
- 身份最容易在转头、遮挡和快速运动时漂。把这些姿态单独列出来，并在高能量段重申同一张脸。

**常见坑:**

- 只上传参考图不写文字锁定。模型会把它当风格图，不当身份图。
- 把服装压缩成同一套衣服。案例库里生效的写法都把服装拆成逐件命名的单品和饰品。
- 用草图或插画当参考却不写渲染指令。要补 use only as design blueprints, render as fully realistic live-action humans，否则线稿感会留在成片里。
- 塞进没有 token 指名的参考图。每多一张，属性串味的机会就多一次。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want a clip where the character looks the same from start to finish. [I am sending you 2 reference images: a young woman with short hair and thin-framed glasses.] [What she does: browses a bookshop, looks up and smiles at the camera.] Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一条需要人物前后长得一样的视频，【我会发给你 2 张人物参考图，她是一位短发、戴细框眼镜的年轻女性】，【她要做的事：在书店里找书、抬头对镜头笑】。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
