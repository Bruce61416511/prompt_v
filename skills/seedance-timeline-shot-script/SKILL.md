---
name: seedance-timeline-shot-script
description: "Split the clip into contiguous timed segments, each carrying one shot type, one main action and its own sound line. The single most load-bearing structure in the corpus. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (Second-by-second timeline script; 中文触发词: 逐秒时间轴分镜脚本, 逐秒分镜, 时间轴, 时间码, 分镜脚本), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# Second-by-second timeline script · 逐秒时间轴分镜脚本

Split the clip into contiguous timed segments, each carrying one shot type, one main action and its own sound line. The single most load-bearing structure in the corpus.

This Skill carries one prompt structure distilled from 6 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- Any clip longer than about 8 seconds, or any clip where a specific thing must happen at a specific moment. 63 of 207 cases (30%) use timed segments, and the share rises to 45% among Seedance 2.5 cases.
- 中文：长度超过 8 秒，或者某件事必须发生在某个时刻。207 条里 63 条（30%）用了时间分段，在 Seedance 2.5 案例里这个比例升到 45%。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. Global block: duration, aspect ratio, frame rate, overall style and image-quality vocabulary
   2. Fixed block: characters, wardrobe, props and location that stay unchanged for the whole clip
   3. Timeline block: one segment per beat, headed `[00:00-00:04] Shot 1: Ground-level Low Angle`, then frame content, action, detail, sound
   4. Global constraint block: negative list and hard limits, placed after the timeline
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Keep segments 2-5 seconds. Documentary tracking runs 2s per beat, ads run 3s, and an audio-locked MV can go down to sub-second anchors. The shorter the segment, the more it needs a visible action verb rather than a mood adjective.
- Write closed intervals that touch end to end (`0-4s` then `4-8s`) and make them sum to the stated duration. Declaring 30 seconds but listing only 24 makes the model stretch the last beat to fill the gap.
- Give each segment exactly one main action. Two actions in one segment get half-finished at both ends because the model splits the time evenly.
- Hand state over between segments explicitly. The bodycam raid case writes three lines per stage — opening state, main event, ending state — and starts each new stage with a carry-over line naming the same team, same gear, no cut.
- Put camera terminology in English inside the segment header parentheses (Ground-level Low Angle, Dynamic Tracking, Handlebar POV) and keep the prose in your working language. Mixed headers hold better than fully translated ones.

## Pitfalls

- Writing a total duration without segments. Half the corpus states a duration but only 30% segments it, and the un-segmented half visibly drifts after roughly six seconds.
- Repeating wardrobe and hairstyle inside every segment. Restating identity per beat triggers appearance mutation between beats; state it once in the fixed block and add a whole-clip lock line.
- Timing to 0.01s precision without an audio input. Text-only generation resolves to about 0.5s, so finer numbers only add noise.
- Burying the negative list inside a segment. Hard limits belong in one block at the end so they apply to the whole clip.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：逐秒时间轴分镜脚本

把片子切成首尾相接的时间段，每段带一个机位、一个主要动作和一行音效。整个案例库里承重最强的结构。

**结构:**

1. 全局块：时长、画幅、帧率、整体风格与画质词
2. 固定块：全片不变的人物、服装、道具和地点
3. 时间轴块：一段一拍，段头写 `[00:00-00:04] 镜头1：低角度起步（Ground-level Low Angle）`，段内写画面、动作、细节、音效
4. 全局约束块：负向清单与硬性限制，放在时间轴之后

**要点:**

- 段长控制在 2 到 5 秒。纪实跟拍两秒一段，广告三秒一段，有音频驱动的 MV 可以细到亚秒级锚点。段越短，越要给可见的动作动词，别给情绪形容词。
- 时间写成闭区间并首尾相接（`0-4s` 接 `4-8s`），且总和等于声明的时长。写 30 秒却只列到 24 秒，模型会把最后一段拉长填满。
- 每段只给一个主要动作。两个动作挤在一段里，会被平均分配时间，结果两个都做一半。
- 段与段之间显式交接状态。执法记录仪那条案例每一阶段写三行——开始时、主要事件、结束时——并在下一段开头写承接上一阶段、同一批人、同一套装备、不切镜。
- 机位术语用英文原词写在段头括号里（Ground-level Low Angle、Dynamic Tracking、Handlebar POV），正文用工作语言。混写比全译更稳。

**常见坑:**

- 只写总时长不写分段。50% 的案例写了时长，只有 30% 做了分段，没分段的那批普遍在六秒后开始漂。
- 在每段里重写服装发型。逐段重申身份反而诱发段间外观突变，应该在固定块里写一次，再加一句全程不变。
- 没有音频输入却把时间精确到 0.01 秒。纯文生视频的时间分辨率大约在 0.5 秒，更细的数字只是噪音。
- 把负向清单塞进某一段里。硬性限制应该单独成块放在末尾，才对全片生效。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want to make a clip scripted second by second. [It shows: a courier delivering the last order of the night through neon-lit rain.] [Total length 15 seconds, vertical 9:16.] Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一条按时间轴分镜的视频，【内容是：一位骑手在雨夜的霓虹街头送最后一单】，【总时长 15 秒，竖屏 9:16】。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
