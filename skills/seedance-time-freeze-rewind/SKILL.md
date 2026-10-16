---
name: seedance-time-freeze-rewind
description: "A five-beat skeleton — normal, collision, freeze at the peak, orbit, precise rewind — with exactly one character exempt from the freeze. The corpus contains the same author reusing this skeleton with a different physical material, which is direct evidence that it transfers. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (Time freeze and rewind set piece; 中文触发词: 时间冻结与倒放奇观, 时间冻结, 倒放, 子弹时间, 时间停止), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# Time freeze and rewind set piece · 时间冻结与倒放奇观

A five-beat skeleton — normal, collision, freeze at the peak, orbit, precise rewind — with exactly one character exempt from the freeze. The corpus contains the same author reusing this skeleton with a different physical material, which is direct evidence that it transfers.

This Skill carries one prompt structure distilled from 8 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- Short high-engagement set pieces built on a physics spectacle rather than a plot. The diner version is the single highest-engagement case in the whole corpus.
- 中文：靠物理奇观而不是剧情撑起来的高互动短片。餐厅那版是整个案例库里互动最高的一条。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. Period and texture line: era, practicals, grain, handheld energy
   2. Beat 1 normal: the exempt character established as calm and slightly bored
   3. Beat 2 collision: the accident detonates, everything launches
   4. Beat 3 freeze: time locks at the peak, every face frozen, one character still moving
   5. Beat 4 orbit: a slow full circle through the frozen scene, cataloguing suspended detail
   6. Beat 5 rewind and dissolve: everything reverses to exact starting positions, closed by a small casual gesture
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Keep the five beats and swap the physical material. The corpus has coffee-and-crockery and a flying wig running the identical skeleton, which is what makes it a template rather than a one-off.
- Name the exempt character and give them an attitude — calm, slightly amused, almost bored. That attitude is the narrative spine of the whole effect.
- Describe the frozen physics concretely: liquid hanging as glassy ribbons and perfect spheres with real surface tension, individual hairs suspended, a tray still rotating in place, faces locked in startled expressions.
- Write the rewind as controlled and elegant, and require it to land back at the exact starting positions. Without that clause the reverse resolves to some other arbitrary state.
- Close by dissolving the accident with one light action — two fingers raised in a casual wave, unwrapping and chewing a stick of gum. It reads better than simply ending.

## Pitfalls

- Describing the freeze as slow motion. That yields slow motion, not a stop; write time locks completely.
- Giving the orbit too little time. The diner version spends nine seconds on one full circle, which is what makes the suspended detail legible.
- Choosing heavy or shattering debris as the frozen material. Liquids and light objects hold up far better in a frozen frame than fragments do.
- Freezing the exempt character by accident. Restate in every frozen beat that this one person keeps moving.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：时间冻结与倒放奇观

五拍骨架——日常、碰撞、峰值锁死、环绕、精确倒放——只留一个人不受冻结影响。案例库里同一作者换了物理材质把这套骨架重跑一遍，这就是它可迁移的直接证据。

**结构:**

1. 年代与质感行：时代、现场灯、颗粒、手持能量
2. 第一拍常态：把那个豁免角色立成从容、略带无聊
3. 第二拍碰撞：事故炸开，所有东西被抛起
4. 第三拍冻结：时间在峰值锁死，所有人的脸定住，只有一个人还在动
5. 第四拍环绕：慢慢绕冻结场景一整圈，把悬浮细节逐一点名
6. 第五拍倒放与消解：一切精确倒回起始位置，用一个轻的随手动作收尾

**要点:**

- 保留五拍，换掉物理材质。案例库里有咖啡和餐具版、有假发飞起版，跑的是同一套骨架，这才让它成为模板而不是一次性作品。
- 指名那个豁免角色并给他一个态度——从容、略带笑意、几乎有点无聊。这个态度是整套效果的叙事支点。
- 冻结的物理要写具体：液体挂成玻璃质飘带和有真实表面张力的完美球体、单根头发悬空、托盘还在原地自转、面孔锁在惊愕表情上。
- 倒放要写成受控而优雅的，并要求精确回到起始位置。少了这条，倒放会解到另一个随机状态上。
- 结尾用一个轻动作把事故消解掉——抬两根手指随意招手、拆开一片口香糖嚼起来。比直接结束好读得多。

**常见坑:**

- 把冻结写成慢动作。那会得到慢动作而不是静止，要写 time locks completely。
- 环绕给的时间太短。餐厅那版用九秒走完一整圈，悬浮细节才看得清。
- 拿重物或会碎裂的东西当冻结材质。液体和轻物件在冻结帧里比碎片扛得住得多。
- 顺手把豁免角色也冻住了。每一个冻结拍里都要重申这个人还在动。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want a time-freeze or rewind set piece. [Scene: a 1990s American diner, a waitress has just spilled her coffee.] [The effect I want: everything freezes, the camera circles the room, then the whole scene rewinds to where it started.] Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一段时间冻结或倒放的奇观镜头，【场景是：九十年代的美式餐厅，服务员手里的咖啡刚泼出去】，【我想要的效果是：全场定住，镜头绕场一圈，再整体倒放回原位】。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
