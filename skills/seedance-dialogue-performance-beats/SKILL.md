---
name: seedance-dialogue-performance-beats
description: "Declare the spoken language, tag the speaker, write the reaction as a causal chain rather than a list of expressions, and close each beat with an explicit end state. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (Dialogue and performance beats; 中文触发词: 对白与表演节拍, 对白, 口型同步, 台词, 表演), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# Dialogue and performance beats · 对白与表演节拍

Declare the spoken language, tag the speaker, write the reaction as a causal chain rather than a list of expressions, and close each beat with an explicit end state.

This Skill carries one prompt structure distilled from 10 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- Whenever a line has to be heard rather than implied. 78 of 207 cases carry quoted dialogue inline (38%), and 16 explicitly manage lip sync. Seedance 2.5 additionally supports driving lip sync from an uploaded audio track.
- 中文：台词要被听见而不是被暗示的时候。207 条里 78 条把台词直接写进正文（38%），16 条显式管理口型。Seedance 2.5 还支持用上传的音轨驱动口型。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. Language and audio-source declaration, before any line
   2. Speaker tags, one per character
   3. Per beat: the causal reaction chain, then the line, then the end state
   4. Global performance principles: what the character does and does not know
   5. Negative: no voice-over, no silent gaps, no expression-sticker switching
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Declare the language on its own line before the line itself, in the form `セリフ言語: 日本語` or `Natural English dialogue only`, and wrap the line in braces or quotes so it is not read as scene description.
- With an uploaded audio track, state that lip sync follows the actual vocal in the audio rather than the written text, and require closed lips during instrumental passages. Also restrict lip sync to one performer so background characters do not start mouthing.
- Write the reaction as a chain, not a checklist: hears it, brief pause to understand, expression starts to shift, body follows, residue of the previous expression lingers, then the next state. Listing eyebrows, eyes, nose and mouth separately produces sticker-style switching.
- Close every beat with an end state line so the next beat has a defined starting point — the raid case uses `ending state` per stage, the Japanese dialogue case uses `終了状態`.
- For emotional states with a physical tell, specify the behaviour rather than the symptom. Asking for a blush yields a uniform pink filter; asking for the eyes to look away, the mouth corner to slip, the speech to slow and the hand to pause yields shyness.

## Pitfalls

- Continuous dialogue clips need an explicit `no silent moments and no voice-over`, otherwise the model delivers music plus a mouth moving.
- Proper nouns and digits are the least reliable part of any generated line. Move brand names and numbers out of the dialogue and into on-screen text added in post.
- Two characters speaking in the same beat splits the lip-sync budget. Give one the line and the other a physical reaction.
- A line longer than roughly eight words in a three-second beat will desync. Shorten the line before touching anything else.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：对白与表演节拍

声明对白语种、标出说话人、把反应写成因果链而不是表情清单，每一拍以一个明确的结束状态收尾。

**结构:**

1. 语种与音源声明，写在任何台词之前
2. 说话人标签，每个角色一个
3. 每一拍：因果反应链、台词、结束状态
4. 全局表演原则：角色知道什么、不知道什么
5. 负向：不要旁白、不要静默空档、不要表情包式切换

**要点:**

- 语种单独成行写在台词之前，写成 `セリフ言語: 日本語` 或 `Natural English dialogue only`，并把台词包进花括号或引号，避免被当成场景描述读。
- 有上传音轨时，写明口型依据音频里的真实人声而不是文字，并要求无人声段落闭唇。同时限定只有一个人对口型，背景人物别跟着张嘴。
- 反应写成链，不写清单：先听见、短暂停顿理解、表情开始变化、身体随后跟上、前一个表情留余韵、再进入下一个状态。逐条控制眉毛眼睛鼻子嘴会做出表情包式切换。
- 每一拍以一行结束状态收尾，给下一拍一个明确起点——突袭那条每阶段写结束时，日语对白那条写終了状態。
- 有生理表征的情绪要写行为，不写症状。直接要脸红会得到均匀粉色滤镜；改成视线短暂移开、嘴角压不住、语速变慢、手部停顿，害羞才成立。

**常见坑:**

- 连续对白的片子要明写 `no silent moments and no voice-over`，否则模型会给你配乐加一张动的嘴。
- 专有名词和数字是生成台词里最不可靠的部分。把品牌名和数字从对白挪到后期加的上屏文字里。
- 两个角色在同一拍说话会分掉口型预算。一个给台词，另一个给身体反应。
- 三秒的拍子里台词超过八个词左右就会失步。先砍台词，再调别的。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want an acted scene with dialogue. [Characters: two former lovers meeting again in a cafe on a rainy night.] [Lines: He says, you have not changed. She says, neither have you.] [The mood moves from guarded to softening.] Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一条有对白的表演戏，【人物是：一对在雨夜咖啡馆重逢的旧恋人】，【台词是：男，你还是老样子。女，你也是。】，【情绪从克制到松动】。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
