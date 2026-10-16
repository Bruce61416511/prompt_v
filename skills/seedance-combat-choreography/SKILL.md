---
name: seedance-combat-choreography
description: "Fights read as real when the prompt specifies biomechanics, contact points and an attack chain. Adjectives like epic produce two people swinging at air. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (Combat choreography; 中文触发词: 打斗编排, 打斗, 动作戏, 格斗, 武打, 连招), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# Combat choreography · 打斗编排

Fights read as real when the prompt specifies biomechanics, contact points and an attack chain. Adjectives like epic produce two people swinging at air.

This Skill carries one prompt structure distilled from 78 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- Martial arts, swordplay, street fights, superhero traversal and stunt sequences. 40 cases in the corpus, split fairly evenly between live-action and anime treatments.
- 中文：武术、剑戟、街头格斗、超能力位移和特技段落。案例库里 40 条，真人和动漫处理大致对半。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. Biomechanics and body spec: discipline, height and weight, muscle intention
   2. Attack chain per beat: attack, defence, counter, reposition
   3. Contact points and camera axis
   4. Weapon lock: count, grip position, how blade, guard and hilt stay one object
   5. Effects and gore ceiling, plus negatives
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Name the discipline and its biomechanics. Authentic Taekwondo biomechanics, realistic anatomy, weight, gravity and momentum reads very differently from epic fight scene.
- Write attacks as chains: straight punch into hook into low kick, met with parry, slip under, check, then an immediate counter body kick. Add that both fighters stay aggressive with no passive waiting, idle stance, reset, teleportation or position jumps.
- Ban ragdolling explicitly. The spider-traversal case writes NEVER ragdoll, NEVER limp, NEVER floppy, core always engaged, every movement has muscle intention — and then specifies body position per movement type.
- Orbit the camera around the contact point and say that the camera and background rotate rather than the characters spinning for no reason.
- Lock weapon count and grip. The anime duel case fixes two blades total, hands gripping only behind the guard, and the blade, guard, hilt, sheath and tassel connection held constant across every cut.

## Pitfalls

- Omitting contact points. Without them you get two people swinging near each other and never connecting.
- Over-cutting. Beyond about four segments in a 7 to 10 second fight, the action stops being legible.
- Leaving the gore level unstated. Safety filtering then softens the whole sequence; the cyber-blade case substitutes black digital particles and glitch fragments and writes No blood.
- Crossing the axis. Left-right relationships flip and the fight becomes incoherent; add an explicit do-not-cross-the-axis line.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：打斗编排

打斗要成立，靠的是生物力学、接触点和连招链。写 epic fight 只会得到两个人互相挥空。

**结构:**

1. 生物力学与身体规格：流派、身高体重、肌肉意图
2. 逐拍连招链：进攻、格挡、反击、重新占位
3. 接触点与镜头轴线
4. 武器锁：数量、握持位置、刀身与鍔柄如何保持一体
5. 特效与血腥尺度，以及负向

**要点:**

- 指名流派和它的生物力学。authentic Taekwondo biomechanics、真实解剖、重量、重力、动量，读起来跟 epic fight scene 完全是两回事。
- 招式写成链：直拳接勾拳接低扫，对方格挡、滑步下潜、封挡，随即反击体踢。再补一句双方持续进攻，不待机、不摆架子、不重置、不瞬移、不跳位。
- 显式禁掉布娃娃化。蜘蛛位移那条写 NEVER ragdoll、NEVER limp、NEVER floppy、核心始终发力、每个动作都有肌肉意图，然后按动作类型逐条规定身体姿态。
- 镜头绕接触点转，并写明是镜头和背景在转，不是人物无意义自转。
- 锁死武器数量和握持。动漫剑戟那条固定全场共两把刀、手只握在鍔之后的柄上，刀身、鍔、柄、鞘、房饰的连接在每个 Cut 里都不变。

**常见坑:**

- 不写接触点。结果是两个人在彼此附近挥舞，永远打不到。
- 切太碎。7 到 10 秒的打斗超过四段左右，动作就读不出来了。
- 不声明血腥尺度。安全过滤会把整段削软；赛博之刃那条用黑色数字粒子和故障碎片替代，并写 No blood。
- 越轴。左右关系会翻转，打斗就散了，要补一句不许越轴。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want a fight scene. [The two fighters: a swordsman in white and a blade-wielder in a bamboo hat.] [Location: a bamboo forest in falling snow.] [Style: wuxia, clean and sharp movement, a camera that keeps up.] Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一段打斗戏，【对打双方是：白衣剑客和戴斗笠的刀客】，【场地是：下着雪的竹林】，【想要的风格：武侠，动作干净利落，镜头跟得上】。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
