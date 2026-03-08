"""
侵蚀度系统 - 管理玩家的侵蚀度状态和效果
"""

import random
from dataclasses import dataclass


@dataclass
class ErosionEffect:
    """侵蚀度效果"""

    name: str
    description: str
    stat_changes: dict[str, float]  # 属性变化
    special_effects: list[str]  # 特殊效果标识


class ErosionSystem:
    """侵蚀度系统"""

    # 侵蚀度阈值和对应效果
    EROSION_THRESHOLDS = {
        0: ErosionEffect(name="纯净", description="心智清明，未受侵蚀", stat_changes={}, special_effects=[]),
        20: ErosionEffect(
            name="轻度侵蚀",
            description="开始感受到异界的低语",
            stat_changes={"max_hp": -5, "attack": 2},
            special_effects=["whispers"],
        ),
        40: ErosionEffect(
            name="中度侵蚀",
            description="现实与幻象的边界开始模糊",
            stat_changes={"max_hp": -10, "attack": 5, "defense": -2},
            special_effects=["whispers", "hallucinations"],
        ),
        60: ErosionEffect(
            name="重度侵蚀",
            description="身体开始发生异变",
            stat_changes={"max_hp": -15, "attack": 10, "defense": -5},
            special_effects=["whispers", "hallucinations", "mutation"],
        ),
        80: ErosionEffect(
            name="深度侵蚀",
            description="已经难以分辨自我与异界",
            stat_changes={"max_hp": -20, "attack": 15, "defense": -8, "speed": 3},
            special_effects=["whispers", "hallucinations", "mutation", "reality_distortion"],
        ),
        100: ErosionEffect(
            name="完全侵蚀",
            description="你已成为异界的一部分",
            stat_changes={"max_hp": -25, "attack": 20, "defense": -10, "speed": 5},
            special_effects=["whispers", "hallucinations", "mutation", "reality_distortion", "transformation"],
        ),
    }

    def __init__(self):
        self.erosion_level = 0
        self.erosion_events_seen = set()  # 已触发的侵蚀事件

    def add_erosion(self, amount: int, reason: str = "") -> tuple[int, bool]:
        """
        增加侵蚀度

        Args:
            amount: 增加的侵蚀度
            reason: 侵蚀原因

        Returns:
            (新的侵蚀度, 是否跨越了新的阈值)
        """
        old_level = self.erosion_level
        old_threshold = self._get_current_threshold(old_level)

        self.erosion_level = min(100, self.erosion_level + amount)

        new_threshold = self._get_current_threshold(self.erosion_level)
        threshold_crossed = new_threshold > old_threshold

        return self.erosion_level, threshold_crossed

    def reduce_erosion(self, amount: int) -> int:
        """
        降低侵蚀度（某些特殊道具或事件可以降低）

        Args:
            amount: 降低的侵蚀度

        Returns:
            新的侵蚀度
        """
        self.erosion_level = max(0, self.erosion_level - amount)
        return self.erosion_level

    def _get_current_threshold(self, level: int) -> int:
        """获取当前侵蚀度对应的阈值"""
        for threshold in sorted(self.EROSION_THRESHOLDS.keys(), reverse=True):
            if level >= threshold:
                return threshold
        return 0

    def get_current_effect(self) -> ErosionEffect:
        """获取当前侵蚀度效果"""
        threshold = self._get_current_threshold(self.erosion_level)
        return self.EROSION_THRESHOLDS[threshold]

    def get_stat_modifiers(self) -> dict[str, float]:
        """获取当前侵蚀度造成的属性修正"""
        return self.get_current_effect().stat_changes.copy()

    def has_special_effect(self, effect_name: str) -> bool:
        """检查是否有特定的特殊效果"""
        return effect_name in self.get_current_effect().special_effects

    def get_erosion_event(self) -> str:
        """
        根据当前侵蚀度获取随机事件文本
        这些事件会在探索中随机触发，增强沉浸感
        """
        threshold = self._get_current_threshold(self.erosion_level)

        events = {
            0: ["你感觉一切正常。", "周围的环境看起来很真实。"],
            20: ["你似乎听到了远处的低语声...", "眼角余光中，似乎有什么东西在移动。", "你感到一阵莫名的不安。"],
            40: [
                "墙壁上的纹理开始扭曲变形...",
                "你看到了不应该存在的影子。",
                "现实感觉有些不对劲。",
                "你的手看起来有些陌生。",
            ],
            60: [
                "你的皮肤上出现了奇怪的纹路。",
                "你能感受到体内有什么在生长。",
                "镜中的倒影不再完全是你。",
                "你开始理解那些低语的含义。",
            ],
            80: [
                "你已经不确定什么是真实的了。",
                "异界的景象与现实重叠在一起。",
                "你感觉自己正在变成别的什么东西。",
                "那些低语现在如此清晰，如此诱人。",
            ],
            100: [
                "你就是异界，异界就是你。",
                "所谓的'现实'不过是一个笑话。",
                "你已经超越了人类的限制。",
                "你终于明白了一切的真相。",
            ],
        }

        event_list = events.get(threshold, events[0])
        event = random.choice(event_list)

        # 记录已触发的事件
        event_key = f"{threshold}_{event}"
        if event_key not in self.erosion_events_seen:
            self.erosion_events_seen.add(event_key)
            return event

        return ""

    def get_status_display(self) -> str:
        """获取侵蚀度状态显示文本"""
        effect = self.get_current_effect()

        # 侵蚀度条
        bar_length = 20
        filled = int(self.erosion_level / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        # 颜色提示（用于终端显示）
        if self.erosion_level < 20:
            color = "绿"
        elif self.erosion_level < 40:
            color = "黄"
        elif self.erosion_level < 60:
            color = "橙"
        elif self.erosion_level < 80:
            color = "红"
        else:
            color = "紫"

        status = f"\n{'=' * 50}\n"
        status += f"侵蚀度: [{bar}] {self.erosion_level}/100 ({color}色)\n"
        status += f"状态: {effect.name}\n"
        status += f"描述: {effect.description}\n"

        if effect.stat_changes:
            status += "\n属性影响:\n"
            for stat, change in effect.stat_changes.items():
                sign = "+" if change > 0 else ""
                stat_name = {"max_hp": "最大生命", "attack": "攻击力", "defense": "防御力", "speed": "速度"}.get(
                    stat, stat
                )
                status += f"  {stat_name}: {sign}{change}\n"

        if effect.special_effects:
            status += "\n特殊效果:\n"
            effect_names = {
                "whispers": "异界低语",
                "hallucinations": "幻觉",
                "mutation": "身体异变",
                "reality_distortion": "现实扭曲",
                "transformation": "完全转化",
            }
            for eff in effect.special_effects:
                status += f"  - {effect_names.get(eff, eff)}\n"

        status += f"{'=' * 50}\n"

        return status

    def should_trigger_erosion_event(self) -> bool:
        """判断是否应该触发侵蚀事件（随机）"""
        # 侵蚀度越高，触发概率越大
        chance = self.erosion_level / 100 * 0.3  # 最高30%概率
        return random.random() < chance

    def get_erosion_sources(self) -> dict[str, int]:
        """
        获取各种行为导致的侵蚀度增加量
        供其他系统参考
        """
        return {
            "使用禁忌道具": 10,
            "阅读禁忌知识": 15,
            "与异界生物交易": 8,
            "进入深层区域": 5,
            "使用异界力量": 12,
            "目睹不可名状之物": 20,
            "死亡": 3,  # 每次死亡增加少量侵蚀度
            "完成黑暗仪式": 25,
        }
