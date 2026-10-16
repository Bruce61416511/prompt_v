---
name: seedance-handheld-ugc-vlog
description: "Buy believability with camera defects. Name a specific consumer camera era, list its flaws as requirements, and switch cinematic polish off by hand. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (Handheld UGC vlog; 中文触发词: 手持 UGC vlog, 手持, UGC, vlog, 手机拍摄, 生活记录), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# Handheld UGC vlog · 手持 UGC vlog

Buy believability with camera defects. Name a specific consumer camera era, list its flaws as requirements, and switch cinematic polish off by hand.

This Skill carries one prompt structure distilled from 118 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- Personal-feeling footage: daily life, travel, gym, cooking, get-ready-with-me. Use it whenever the goal is looks like someone actually filmed this rather than looks expensive.
- 中文：要私人感的素材：日常、旅拍、健身、做饭、出门前准备。目标是像真有人拍的，而不是像很贵的时候用这套。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. CAMERA: mount, era, handling flaws
   2. LOOK: tape or film texture, grain, halation, contrast, exposure behaviour
   3. STYLE: pacing and mood in one or two lines
   4. SUBJECT and SETTING: who and where, kept short
   5. STORYBOARD: short rows like `→ (3s, propped medium shot)` plus one spoken line
   6. AUDIO NOTES and REALISM NOTES: ambient sound list, then body-language and imperfection list
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Use camera defects as the realism switch: hand shake, focus hunting, exposure breathing, drifting composition, uneven zooms, occasional accidental face cropping. 23 cases in the corpus reach phone-footage texture with this vocabulary.
- Name the gear era rather than asking for realism: mini DV camcorder, 16mm, VHS, iPhone 16 Pro, chest-mounted action cam. A named device carries a whole optical signature that the word realistic does not.
- Switch cinematic polish off explicitly: no cinematic emulation, no stabiliser, no film-style camera moves, no beauty filter, no skin smoothing.
- Write a monotonic body-state progression to give the model an irreversible time cue. The cycling vlog states that sweat only increases and never goes back, and tracks it shot by shot from a first sheen at the temple to a fully soaked jersey.
- Attach one spoken line per storyboard row rather than a separate dialogue block, so speech and action stay welded together.

## Pitfalls

- Asking for handheld authenticity and 4K cinematic lighting in the same prompt. They are two different light logics and the result lands in plastic territory.
- Letting the framing go to extreme close-up. The boyfriend-POV case explicitly bans faces filling the frame and caps the tightest framing at chest-up, because big close-ups expose AI faces.
- Using digital zoom as a transition. If you want a single take, add an explicit ban on digital zoom, sudden push-ins and invisible cuts.
- Over-writing the dialogue. Long lines pull attention off the picture and worsen lip sync; keep each line under about eight words.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：手持 UGC vlog

用相机缺陷换真实感。指名一个具体的消费级器材年代，把它的毛病写成要求，再手动关掉电影感。

**结构:**

1. CAMERA：机器怎么拿、什么年代、有哪些操作毛病
2. LOOK：磁带或胶片质感、颗粒、光晕、对比度、曝光行为
3. STYLE：节奏和情绪，一两行写完
4. SUBJECT 与 SETTING：谁、在哪，都写短
5. STORYBOARD：`→ (3s, propped medium shot)` 这种短行，配一句口语台词
6. AUDIO NOTES 与 REALISM NOTES：环境音清单，然后是肢体语言和瑕疵清单

**要点:**

- 把相机缺陷当真实感开关：手抖、对焦来回找、曝光呼吸、构图漂移、变焦不匀、偶尔切掉半张脸。案例库里 23 条靠这套词表拿到手机实拍质感。
- 指名器材年代，不要笼统要求真实：mini DV 家用摄像机、16mm、VHS、iPhone 16 Pro、胸挂运动相机。一个具体型号带着整套光学特征，realistic 这个词带不来。
- 显式关掉电影感：no cinematic emulation、不使用稳定器、不做电影式运镜、无美颜、无磨皮。
- 写单调递进的身体状态，给模型一个不可逆的时间线索。骑行 vlog 那条写死汗量随时间递增不可倒退，并逐镜从额角第一层汗写到骑行服全湿。
- 台词跟着分镜行走，不要单开对白块，让说话和动作焊在一起。

**常见坑:**

- 同一条 prompt 里既要手持真实感又要 4K 电影级打光。两套光线逻辑打架，结果落在塑料感上。
- 让景别推到大特写。男友视角那条明确禁止脸部填满画面，最近只给到胸口以上，因为大特写会暴露 AI 脸。
- 用数字变焦当转场。要一镜到底就补一句禁止数字变焦、突然推近和隐形剪辑。
- 台词写太长。长句抢画面还拖垮口型，每句控制在八个词以内。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want a handheld, everyday vlog. [On camera: a woman in her twenties wearing an oversized hoodie.] [Scene: making pour-over coffee in her own kitchen on a weekend morning.] I will attach reference images if I have them. Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一条手持感的生活 vlog，【出镜的人是：一位二十多岁的女生，穿宽松卫衣】，【场景是：周末早上在自家厨房做手冲咖啡】，有参考图我会一起发给你。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
