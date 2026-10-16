---
name: seedance-cinematic-narrative-short
description: "Multi-act storytelling in 15 to 60 seconds. Titled acts, a character card ahead of the acts, and a reveal written as a concrete image rather than as a promise of surprise. Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip (Cinematic narrative short; 中文触发词: 电影级叙事短片, 剧情短片, 叙事, 故事短片, 电影感剧情), or asks how published cases of this type were prompted. Read references/cases.md before drafting."
---

# Cinematic narrative short · 电影级叙事短片

Multi-act storytelling in 15 to 60 seconds. Titled acts, a character card ahead of the acts, and a reveal written as a concrete image rather than as a promise of surprise.

This Skill carries one prompt structure distilled from 59 human-verified Seedance cases on [goodcase.ai](https://goodcase.ai). It is a sibling of `seedance-prompt-library` (all templates in one Skill); install this one when you only want this kind of clip. Do not invent structure from general video-generation knowledge: follow the structure below and ground the draft in one anchor case from `references/cases.md`.

## Use when

- Trailers, mini-dramas, disaster set pieces, sci-fi mysteries and romance shorts — anything where the viewer should follow a plot rather than admire a look.
- 中文：预告片、迷你剧、灾难段落、科幻悬念、爱情短片——观众要跟剧情而不是看质感的场合。

## Workflow

1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.
2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.
3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.
   1. Genre and visual key: reference aesthetic, grading, lens behaviour, editing tempo
   2. Character cards ahead of the acts, one short block per person
   3. Acts, each with a title and a time window
   4. Shots inside each act, varying in count between acts
   5. Music and sound trajectory
   6. Ending instruction, stated as a cut rather than as a feeling
4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.
5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.

## Guidance (from the cases)

- Title each act. The romance trailer labels its acts The Message and Running Through the City, and the title itself constrains how much information that act carries.
- Keep the character card to five slots — hair, top, bottom, shoes, carried object. That is enough for the model to recognise the person without overloading the identity budget.
- Past about 30 seconds, split into two prompts and stitch. The high-school romance case declares SHOT 1 = 0-30 seconds and SHOT 2 = 30-60 seconds and requires the two to connect seamlessly as one film; another case in the corpus generates two 15-second halves and stitches manually.
- Write the reveal as a picture. The 2100 mystery resolves on clouds separating to expose an enormous object over an empty Dubai, not on the phrase shocking reveal.
- Bind emotional turns to light changes: golden hour into blue hour, cold blue exterior into warm interior. The disaster case switches grading at the moment the protagonist reaches shelter.

## Pitfalls

- Even pacing. If every act gets the same number of shots, the story reads as a montage; vary shot counts deliberately.
- Leaving the dialogue to the model. Generated lines drift off-genre; write them, even if only one per act.
- Single-generation clips over 30 seconds show a marked rise in identity drift. Restate the identity lock at the start of the second half or split the generation.
- Writing fade out at the end. The model really fades and burns the last two seconds; write a hard cut to black, no fade, no extended tail.

## Language

Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.

## 中文：电影级叙事短片

15 到 60 秒的多幕叙事。每幕带标题，角色卡写在幕之前，反转写成具体画面而不是一句会让人震惊。

**结构:**

1. 类型与视觉基调：参照美学、调色、镜头行为、剪辑节奏
2. 角色卡写在分幕之前，每人一小块
3. 分幕，每幕带标题和时间窗
4. 幕内镜头，各幕镜头数量不要一样
5. 音乐与音效走向
6. 收尾指令，写成一个剪辑动作而不是一种感觉

**要点:**

- 给每一幕起标题。浪漫预告那条把幕命名为 The Message 和 Running Through the City，标题本身就约束了这一幕能装多少信息。
- 角色卡控制在五格——发型、上衣、下装、鞋、随身物。够模型认人，又不会吃光身份预算。
- 超过 30 秒就拆成两条 prompt 再拼。高中初恋那条声明 SHOT 1 = 0-30 秒、SHOT 2 = 30-60 秒，并要求两段无缝相接成一部片；案例库里另有一条直接生成两段 15 秒后手动拼接。
- 反转要写成一幅画。2100 悬念那条落在云层分开、空城迪拜上方露出巨物，不是落在 shocking reveal 这个词上。
- 情绪转折绑在光线变化上：golden hour 转 blue hour、冷蓝外景切暖色内景。灾难那条就在主角进入避难所的瞬间换了调色。

**常见坑:**

- 节奏平均。每幕镜头数一样，故事就读成蒙太奇了，要刻意给不同数量。
- 把台词交给模型。生成的台词会偏离类型，自己写，哪怕每幕只写一句。
- 单条生成超过 30 秒，身份漂移概率明显上升。在后半段开头重申身份锁，或者干脆拆开生成。
- 结尾写 fade out。模型会真的淡出，白白烧掉最后两秒，应该写 hard cut to black、不淡出、不延长尾音。

## Copy-ready lead-in / 可复制引导语

For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:

> I want a cinematic narrative short. [The story: an astronaut in an abandoned space station receives a message from the year 2100.] [Genre and mood: sci-fi mystery, cold palette.] [15 seconds.] Using the prompt template below, rewrite it into one ready-to-use Seedance video prompt for me:
>
> 我要做一条电影感的叙事短片，【故事是：宇航员在废弃空间站里收到一条来自 2100 年的讯息】，【想要的类型和气质：科幻悬疑，冷色调】，【时长 15 秒】。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

## Notes

- `references/cases.md` is generated from `data/` in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.
- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.
- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).
