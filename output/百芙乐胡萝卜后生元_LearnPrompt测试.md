# 输入

帮我写一条「百芙乐」胡萝卜后生元饮品的产品广告视频提示词。竖屏 9:16，15 秒，突出胡萝卜的天然色泽和肠道健康的卖点。

---

# 输出

# 「百芙乐」胡萝卜后生元饮品 · Seedance 视频提示词

**选用模板：** 电影级产品广告分镜（`product-commercial-shotlist`）

**为什么选它：** 你要的是投放级的产品广告质感（不是 UGC 口播、不是叙事短片），15 秒正好落在该模板 8–20 秒的区间里。胡萝卜的天然色泽靠「英雄产品描述 + 指名微距拍什么」来立，肠道健康这个卖点不靠上屏文字，而是靠**质地语言**（纤维、活性粒子、顺滑入喉的流动）来暗示——这是模板里明确要求的做法，因为生成的字必然乱码。

---

## 可直接复制的提示词

```
Premium beverage commercial, 15 seconds, vertical 9:16, 24fps.
Advertising aesthetic: premium health-drink commercial aesthetics, clean natural light
with warm golden accents, shallow depth of field, macro lens, subtle volumetric haze.
Color grade: fresh orange-gold, crisp whites, soft green from fresh carrot tops.
Shot on macro and medium lenses.

HERO PRODUCT:
A slender clear glass bottle of "百芙乐" carrot postbiotic drink. Label-free clean glass
surface (no printed text, no logo — leave a clean label area for post-production).
The liquid inside is a dense, opaque, vivid carrot-orange with a natural matte sheen,
slight pulp sediment visible, tiny live bubbles rising slowly. Condensation beads on
the cold glass. A whole fresh carrot with green tops rests beside it.

SHOT BREAKDOWN:
0-3s: Macro. A whole fresh carrot is sliced cleanly; the cross-section reveals bright
orange flesh, fine fibrous texture, a bead of juice welling up at the cut. Camera slowly
pushes in. Natural light rakes across the cut surface.
3-6s: Macro. The vivid carrot-orange liquid pours into the glass bottle in a slow,
thick, glossy ribbon. The stream folds over itself; bubbles rise and settle. Camera
holds low, backlit so the liquid glows from within.
6-9s: Medium close-up. The bottle stands on a pale stone surface with fresh carrot tops
and a few water droplets in the foreground. Camera slowly orbits 45 degrees, catching
the light sweeping across the glass and the liquid's inner glow.
9-12s: Macro, slow motion. A hand lifts the bottle and tilts it; the liquid flows in a
smooth continuous ribbon. Cut to: a single drop falls into a clear glass of water,
blooming into soft orange swirls — a visual metaphor for gentle, active digestion.
12-15s: Hero shot. The bottle centered, slowly rotating, soft rim light tracing its
silhouette, tiny bubbles still rising inside. Camera settles and holds. Clean final
frame, no text.

STYLE KEYWORDS:
premium beverage commercial, macro food cinematography, natural warm light, glossy
liquid texture, shallow depth of field, 35mm film grain, clean minimal composition,
fresh and healthy mood, no plastic look.

AUDIO: soft ambient hum, gentle liquid pour, a light crisp "clink" on the final hero shot.
No voice-over. No music with lyrics.

NEGATIVE: no on-screen text, no logos, no watermarks, no brand markings on the bottle,
no deformed hands, no extra bottles, no duplicate product, no cartoon style,
no plastic CG rendering, no harsh studio lighting.
```

---

## 使用要点（对照模板的 guidance 与 pitfalls）

1. **瓶身刻意留白。** 模板明确说别指望模型把 logo/slogan 渲染干净——所以提示词里写死「no printed text, no logo」，留一块干净标签区，品牌名「百芙乐」后期合成。这是这条片子在投放前唯一必须补的一步。
2. **肠道健康用画面说，不用字说。** 9–12s 那一拍「一滴入水、绽开橙色涡流」就是卖点的视觉隐喻，比任何上屏文案都稳，也避开了生成文字乱码的坑。
3. **微距都指名拍什么。** 模板警告「不指名的微距只会给一个通用虚化特写」——所以每一拍都点了具体对象：切面的纤维与汁水、倒液时的飘带与气泡、玻璃上的光扫。
4. **一拍一个物理效果。** 液体、气泡、水花各自占不同镜头，没有在一拍里堆多种效果。
5. **15 秒 5 个镜头，平均 3 秒一个**，高于模板「单镜不低于 1 秒」的红线，节奏不碎。

---

## 参考案例（同模板在 goodcase.ai 上的实际成片）

- [Luxury Skincare Commercial](https://goodcase.ai/cases/luxury-skincare-commercial)
- [Crimson Cola](https://goodcase.ai/cases/crimson-cola-99e9ec88e937)
- [Case e53b614b0f42](https://goodcase.ai/cases/case-e53b614b0f42)
- [Case 7aea1313f63b](https://goodcase.ai/cases/case-7aea1313f63b)

---

**如果你更想自己在对话模型里跑这条模板**，用这句引导语起头即可：

> 我要做一条电影质感的产品广告，【我的产品是一瓶「百芙乐」胡萝卜后生元饮品，主打天然胡萝卜色泽与肠道健康】，【想要的调性是：干净、自然、有食欲感、慢节奏】，【时长 15 秒，竖屏 9:16】。请根据下面这个提示语模板，帮我改写成一条可以直接用的 Seedance 视频提示语：

需要我再出一版**带人物出镜**的版本（比如一位女性在晨光厨房里喝、更偏生活方式调性），或者把这条拆成**分镜图 + 转视频**的两步流程吗？
