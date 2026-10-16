# -*- coding: utf-8 -*-
"""挑技能准确率测试（31 个技能版 · 含 lint 伴随判定）。

用法：python scripts/test_pick_skills.py

2026-10-16 改动：装上 seedance-prompt-lint 后，它会在「要成稿」的需求里
与负责写的技能一起被选中（生成完立刻质检）。所以判定规则改成：

  · 需求是「写一条 XX 提示词」→ 负责写的技能必中，**允许 lint 伴随**，不允许其他技能乱入
  · 需求是「质检 / 检查这条提示词」→ **只应选中 lint**，不许夹带任何生成技能
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.agent import Agent, LLMConfig          # noqa: E402
from app.skill_loader import SkillLoader        # noqa: E402

LINT = "seedance-prompt-lint"

# (需求, 期望技能名, 分组)
CASES: list[tuple[str, str, str]] = [
    # ---- A. 新建的 14 个片型 ----
    ("帮我写一条手持感的生活 vlog，女生周末早上在厨房做手冲咖啡", "seedance-handheld-ugc-vlog", "新"),
    ("写个打斗戏提示词，两个人在雨里贴身对打，要有连招", "seedance-combat-choreography", "新"),
    ("给我写一条 30 秒的电影感剧情短片提示词，讲深夜便利店的一次相遇", "seedance-cinematic-narrative-short", "新"),
    ("帮我写个 15 秒的产品广告提示词，卖的是一款香水", "seedance-product-commercial-shotlist", "新"),
    ("我要做一条动漫风格的短片，锁定日式赛璐璐画风", "seedance-anime-style-lock", "新"),
    ("写一条把毛坯房改造成精装房的过程延时提示词", "seedance-process-transformation-montage", "新"),
    ("帮我写个卡点 MV 提示词，跟着 120 BPM 的音乐剪", "seedance-music-beat-sync-mv", "新"),
    ("写一条口播测评提示词，测评一款吹风机，要开箱种草", "seedance-ugc-creator-review", "新"),
    ("写个第一人称一镜到底的提示词，GoPro 视角骑车穿城", "seedance-pov-continuous-take", "新"),
    ("写一条两个人对话的提示词，要有口型同步和台词", "seedance-dialogue-performance-beats", "新"),
    ("帮我写个定格动画提示词，黏土小人一步步走路", "seedance-stop-motion-cadence", "新"),
    ("我有三张参考图，想锁定同一个人物的形象做短片", "seedance-character-reference-lock", "新"),
    ("写一条时间冻结加倒放的提示词，子弹时间那种", "seedance-time-freeze-rewind", "新"),
    ("帮我写一条带时间码的逐秒分镜提示词", "seedance-timeline-shot-script", "新"),

    # ---- B. 重叠边界（handheld-ugc-vlog 与 retro-dv-home-video）----
    ("拍一条手机随手拍的日常 vlog，画面有点糊有点抖", "seedance-handheld-ugc-vlog", "重叠"),
    ("做一条 2000 年代 DV 家庭录像那种老带子质感", "seedance-retro-dv-home-video", "重叠"),
    ("手持 UGC 风格的健身打卡 vlog", "seedance-handheld-ugc-vlog", "重叠"),
    ("模仿老式家用摄像机拍的家庭出游记录，有年代感", "seedance-retro-dv-home-video", "重叠"),

    # ---- C. 老片型回归 ----
    ("写个美食 ASMR 提示词，拍煎牛排滋滋作响", "seedance-food-asmr", "回归"),
    ("写个宠物猫当主角的短视频提示词", "seedance-pet-animal", "回归"),
    ("帮我写个恐怖短片提示词，走廊尽头有东西", "seedance-horror-suspense", "回归"),
    ("写个跑车广告提示词，城市夜景飙车", "seedance-car-vehicle", "回归"),
    ("做一条 3D 卡通角色短片，皮克斯风格的小机器人", "seedance-3d-cartoon", "回归"),

    # ---- D. 质检（只应选中 lint，不许夹带生成技能）----
    ("帮我质检一下这段提示词：一个男人在雨里跑步，镜头慢慢推近", LINT, "质检"),
    ("检查下这条提示词有没有问题：产品放在桌上，画面很高级很有电影感", LINT, "质检"),
    ("这条提示词帮我挑挑错：0-3秒他站起来，4-7秒他走过去", LINT, "质检"),
]


def judge(picked: list[str], want: str) -> tuple[bool, str]:
    """返回 (是否通过, 失败原因)。"""
    if want == LINT:
        if picked == [LINT]:
            return True, ""
        return False, "质检需求必须且只能选中 lint（不许夹带生成技能）"

    extra = set(picked) - {want, LINT}
    if want not in picked:
        return False, f"没选中 {want}"
    if extra:
        return False, f"多选了 {sorted(extra)}"
    return True, ""



def main() -> int:
    cfg = LLMConfig(**json.loads((ROOT / "config.json").read_text(encoding="utf-8")))
    loader = SkillLoader(ROOT / "skills")
    agent = Agent(loader, cfg)
    print(f"技能库 {len(loader.skills)} 个 · 清单 {len(loader.catalog_for_llm())} 字符")
    print()

    groups: dict[str, list[int]] = {}
    rows = []
    t0 = time.time()
    for i, (req, want, grp) in enumerate(CASES, 1):
        try:
            picked, src = agent.pick_skills(req)
        except Exception as e:                                   # noqa: BLE001
            picked, src = [], f"错误:{e}"
        hit, why = judge(picked, want)
        groups.setdefault(grp, [0, 0])
        groups[grp][0] += hit
        groups[grp][1] += 1
        rows.append((i, req, want, picked, src, hit))
        mark = "✅" if hit else "❌"
        got = ", ".join(picked) if picked else "（空）"
        print(f"{mark} {i:>2}. {req[:38]:40} → {got}   [{src}]")
        if not hit:
            print(f"      期望: {want}   原因: {why}")
    print()
    print(f"总耗时 {time.time() - t0:.0f}s")
    print()
    total_hit = sum(v[0] for v in groups.values())
    total_all = sum(v[1] for v in groups.values())
    for grp, (h, n) in groups.items():
        print(f"  {grp:4} {h}/{n}")
    print(f"  --------")
    print(f"  合计 {total_hit}/{total_all}  （{total_hit / total_all * 100:.0f}%）")
    multi = [r for r in rows if len(r[3]) > 1]
    with_lint = [r for r in multi if set(r[3]) - {r[2]} == {LINT}]
    print(f"  多选: {len(multi)} 项，其中「lint 伴随」{len(with_lint)} 项"
          f"（预期行为：要成稿时生成完立刻质检）")
    bad_multi = [r for r in multi if r not in with_lint]
    if bad_multi:
        print(f"  ⚠️ 非预期多选: {[(r[0], r[3]) for r in bad_multi]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
