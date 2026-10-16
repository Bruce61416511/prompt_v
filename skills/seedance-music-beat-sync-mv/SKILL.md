---
name: seedance-music-beat-sync-mv
description: "Derive beat anchors from BPM, pin every cut, hair flip and formation change to a real downbeat, and constrain the backup dancers so they never steal the visual centre. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (Beat-synced music video; 中文触发词: 音乐卡点 MV, MV, 卡点, 音乐, 节奏剪辑), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# Beat-synced music video · 音乐卡点 MV

Derive beat anchors from BPM, pin every cut, hair flip and formation change to a real downbeat, and constrain the backup dancers so they never steal the visual centre.

This Skill carries one prompt structure distilled from 19 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- K-pop MVs, dance covers, beat-cut fitness edits and club performance clips. Use the audio-anchored variant only on Seedance 2.5, which accepts an audio track as an input modality.
- 中文：K-pop MV、翻跳、卡点健身剪辑、俱乐部演出片段。带音频锚点的写法只在 Seedance 2.5 上用，它接受音轨作为输入模态。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. Audio source declaration: which track, and a ban on regenerating, retiming or fading it
   2. BPM and a list of named beat anchors with their timestamps
   3. Per-segment choreography and formation
   4. Wardrobe and identity lock, plus dancer-count limits
   5. Typography rules, if captions are on screen
   6. A hard stop on a physical action
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Compute the beat interval before writing shots. The Y2K MV states roughly 128 BPM with about 0.469s per beat, then lists nine named anchors — first downbeat at 2.78s, first scene change at 6.06s, energy drop at 14.02s, chorus at 21.07s, music cut-out at 24.82s — and pins every cut, hair flip, turn and formation change to them.
- Constrain backup dancers by count and by permission: two to six allowed, no facial close-ups, no lip sync, never occluding the lead, never becoming a second visual centre.
- Write formations as geometry: V-shape queue, horizontal line, diamond, symmetrical semicircle, and state where the lead stands inside each one.
- Give on-screen captions their own rule block — bold condensed display font, upper third or side margin, never over faces or hands, quick fade or slide-in on the beat, one line active at a time.
- End on a physical hard stop synced to the final note (a flip phone snapping shut, lights cutting out), and ban fade-outs, extended tails and extra end cards.

## Pitfalls

- Not declaring an audio source. The model invents background music and the lip sync drifts with it.
- Dressing backup dancers too close to the lead. Make the lead's colours the most saturated and keep her nearest the camera.
- Identity drift concentrating in the high-energy dance segments. Restate the same-face requirement inside those segments specifically.
- Asking for complex choreography and complex camera movement in the same beat. Give one of them the beat and let the other hold steady.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：音乐卡点 MV

从 BPM 推出节拍锚点，把每一次剪辑、甩发和队形变化钉在真实重拍上，再把伴舞约束住，别让他们抢走视觉中心。

**结构:**

1. 音源声明：用哪条音轨，以及禁止重新生成、变速和自动淡出
2. BPM 与一份带时间戳的命名节拍锚点清单
3. 逐段编舞与队形
4. 服装与身份锁，外加伴舞人数上限
5. 字幕排版规则，如果有字上屏
6. 用一个物理动作硬收

**要点:**

- 先算节拍间隔再写镜头。Y2K 那条写约 128 BPM、每拍约 0.469 秒，然后列了九个命名锚点——2.78 秒第一个强重拍、6.06 秒第一次换景、14.02 秒能量下降、21.07 秒高潮副歌、24.82 秒音乐抽空——并把每次剪辑、甩发、转身和队形变化都钉上去。
- 伴舞按人数和权限双重约束：允许二到六名，不给面部特写、不对口型、不遮挡主角、不成为第二视觉中心。
- 队形写成几何：V 字行进、横排、菱形、对称半圆，并写清主角在每种队形里站哪。
- 字幕单独一块规则——粗体窄体展示字、位置在上三分之一或侧边、不压脸和手、随拍快速淡入或滑入、同一时间只有一行。
- 结尾用一个跟末音同步的物理硬停（翻盖手机啪地合上、灯瞬间灭），并禁止淡出、延长尾音和多余的结束镜头。

**常见坑:**

- 不声明音源。模型会自己编一段背景音乐，口型也跟着乱。
- 伴舞穿得跟主角太像。主角的颜色要最饱和，位置离镜头最近。
- 身份漂移集中在高能量舞蹈段。要专门在那些段里重申同一张脸。
- 同一拍里既要复杂编舞又要复杂运镜。一拍给一样，另一样保持稳定。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want a beat-synced music video. [Genre: K-pop dance track, around 120 BPM.] [The artist: a female soloist with short silver hair in a futuristic stage outfit.] I will send you the audio or lyrics as well. Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一条卡点音乐 MV，【曲风是：K-pop 舞曲，节奏大约每分钟 120 拍】，【艺人形象是：银色短发的女 solo 歌手，未来感舞台服】，音频或歌词我会一起发给你。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
