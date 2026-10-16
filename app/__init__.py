# -*- coding: utf-8 -*-
"""提示词智能体 —— 让智能体按需加载 skill 并生成分镜提示词。"""

from .skill_loader import Skill, SkillLoader
from .agent import Agent, LLMConfig

__all__ = ["Skill", "SkillLoader", "Agent", "LLMConfig"]
__version__ = "1.0.0"
