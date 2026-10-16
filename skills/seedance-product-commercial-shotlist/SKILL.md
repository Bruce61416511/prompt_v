---
name: seedance-product-commercial-shotlist
description: "A polished 8 to 20 second ad: a stated commercial aesthetic up front, a numbered or timed shot breakdown in the middle, a hero frame at the end, and a keyword tail. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (Cinematic product commercial shot list; 中文触发词: 电影级产品广告分镜, 产品广告, 商业广告, 产品展示, TVC), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# Cinematic product commercial shot list · 电影级产品广告分镜

A polished 8 to 20 second ad: a stated commercial aesthetic up front, a numbered or timed shot breakdown in the middle, a hero frame at the end, and a keyword tail.

This Skill carries one prompt structure distilled from 41 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- Beauty, beverage, jewellery, automotive and fragrance spots where the look has to read as paid production rather than as a creator video.
- 中文：美妆、饮品、珠宝、汽车、香水这类要读成投放级制作、不能读成创作者视频的广告。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. Opening paragraph: category, duration, aspect ratio, commercial aesthetic vocabulary, colour grading, depth of field
   2. Hero product description: material, silhouette, finish, how light behaves on it
   3. Shot Breakdown: either `0-2s:` timed rows or `Shot 1:` numbered rows, never both
   4. Text and slogan lines, each with its own time window
   5. Style Keywords tail as a single trailing block
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Open with the ad-aesthetic vocabulary before any shot: premium beauty-commercial aesthetics, luxury advertising aesthetic, anamorphic lens, volumetric lighting. This sets the light logic for every shot that follows.
- Name the object of every macro and slow-motion beat: foam texture, liquid ribbons, diamond dispersion, metallic reflections across the packaging. Unnamed macro produces a generic blurred close-up.
- When a reference image defines the final frame, say so directly. The paper-cut perfume case writes `Use @image1 as the exact final hero-frame composition. Use @image2 as the strict product identity lock`, then lists the silhouette, lattice, inner body, cap and plaque under a PRODUCT LOCK heading.
- Give on-screen text its own row with its own window, such as `Text: "Cleanse • Refresh • Glow."` at 0-2s, so it does not bleed across the whole clip.
- Keep the keyword pile at the very end. Style keywords scattered between shots get read as shot content.

## Pitfalls

- Expecting the model to render a logo or slogan cleanly. Reserve a clean end frame and composite the type afterwards.
- Mixing high-end commercial light with phone-UGC texture. Pick one; blending them yields a plastic look.
- Stacking multiple physics effects in one beat. Liquid, smoke and powder each need their own shot.
- Packing eight shots into eight seconds. Under about one second per shot the model stops resolving individual actions.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：电影级产品广告分镜

8 到 20 秒的精修广告：开头写死广告美学，中间是编号或计时的分镜拆解，结尾一个英雄镜头，最后甩一段关键词。

**结构:**

1. 开头段：品类、时长、画幅、广告美学词、调色、景深
2. 英雄产品描述：材质、轮廓、表面处理、光在上面怎么走
3. Shot Breakdown：要么用 `0-2s:` 计时行，要么用 `Shot 1:` 编号行，不要混用
4. 文字与 slogan 行，各自带出现时段
5. Style Keywords 收尾，堆成一个尾块

**要点:**

- 分镜之前先写广告美学词：premium beauty-commercial aesthetics、luxury advertising aesthetic、变形宽银幕镜头、体积光。它决定后面每个镜头的光线逻辑。
- 每个微距和慢动作都指名拍什么：泡沫质地、液体飘带、钻石色散、金属反光扫过包装。不指名的微距只会给一个通用虚化特写。
- 参考图定义的是终帧构图就直说。剪纸香水那条写 `Use @image1 as the exact final hero-frame composition. Use @image2 as the strict product identity lock`，再在 PRODUCT LOCK 标题下列出瓶身轮廓、几何镂空、内胆、瓶盖和铭牌。
- 上屏文字单独成行并带时段，比如 0-2s 的 `Text: "Cleanse • Refresh • Glow."`，避免它糊满全片。
- 关键词堆在最末尾。散落在分镜之间的风格词会被当成镜头内容读。

**常见坑:**

- 指望模型把 logo 或 slogan 渲染干净。留一个干净的收尾帧，字后期合成。
- 把高端广告光和手机 UGC 质感混着写。二选一，混着写会得到塑料感。
- 一拍里堆多种物理效果。液体、烟雾、粉末各占一个镜头。
- 八秒塞八个镜头。单镜低于一秒左右，模型就解析不出单独动作了。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want a cinematic product commercial. [My product is a pair of matte black wireless earbuds; I am sending you the product photos.] [The tone I want: cool, technical, slow-paced.] [10 seconds, horizontal 16:9.] Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一条电影质感的产品广告，【我的产品是一款哑光黑的无线耳机，产品图片我提供给你】，【想要的调性是：冷峻、科技感、慢节奏】，【时长 10 秒，横屏 16:9】。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
