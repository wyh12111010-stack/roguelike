"""
新手教程系统
引导新玩家了解游戏机制
"""
import pygame
from config import get_font, SCREEN_WIDTH, SCREEN_HEIGHT


class TutorialStep:
    """教程步骤"""
    def __init__(self, title, text, highlight_area=None, wait_for_action=None):
        """
        title: 标题
        text: 说明文本（可以是列表）
        highlight_area: 高亮区域 (x, y, w, h)
        wait_for_action: 等待的操作 ("move", "attack", "skill", "dash", etc.)
        """
        self.title = title
        self.text = text if isinstance(text, list) else [text]
        self.highlight_area = highlight_area
        self.wait_for_action = wait_for_action
        self.completed = False


class Tutorial:
    """教程管理器"""
    def __init__(self):
        self.active = False
        self.current_step = 0
        self.steps = []
        self.first_time = True
        
        # 初始化教程步骤
        self._init_steps()
    
    def _init_steps(self):
        """初始化教程步骤"""
        self.steps = [
            # 步骤1：欢迎
            TutorialStep(
                "欢迎来到修仙肉鸽",
                [
                    "这是一个修仙题材的肉鸽游戏",
                    "你将扮演一位修士，在危险的世界中历练",
                    "按 [空格] 继续",
                ],
                wait_for_action="continue"
            ),
            
            # 步骤2：移动
            TutorialStep(
                "移动",
                [
                    "使用 [WASD] 或 [方向键] 移动角色",
                    "试着移动一下",
                ],
                wait_for_action="move"
            ),
            
            # 步骤3：攻击
            TutorialStep(
                "攻击",
                [
                    "鼠标指向敌人，按 [鼠标左键] 攻击",
                    "攻击方式由你的法宝决定",
                    "试着攻击敌人",
                ],
                wait_for_action="attack"
            ),
            
            # 步骤4：技能
            TutorialStep(
                "法宝技能",
                [
                    "每个法宝都有独特的技能",
                    "按 [E] 释放当前法宝的技能",
                    "技能消耗灵力，注意灵力条",
                ],
                wait_for_action="skill"
            ),
            
            # 步骤5：闪避
            TutorialStep(
                "闪避",
                [
                    "按 [空格] 或 [Shift] 快速冲刺",
                    "冲刺时有短暂无敌时间",
                    "用来躲避危险攻击",
                ],
                wait_for_action="dash"
            ),
            
            # 步骤6：灵根和元素
            TutorialStep(
                "灵根与元素",
                [
                    "你的灵根决定你的元素属性",
                    "不同元素之间会产生反应",
                    "例如：火克金、水克火、木克土等",
                    "利用元素反应造成额外伤害",
                ],
                wait_for_action="continue"
            ),
            
            # 步骤7：饰品
            TutorialStep(
                "饰品系统",
                [
                    "饰品提供被动加成",
                    "可以叠加多个相同饰品提升效果",
                    "按 [C] 查看你的饰品",
                    "在商店可以购买饰品",
                ],
                wait_for_action="continue"
            ),
            
            # 步骤8：资源
            TutorialStep(
                "资源管理",
                [
                    "灵石：战斗中购买物品，死亡后清零",
                    "道韵：村子永久升级，不会丢失",
                    "丹药：按 [R] 使用，恢复生命",
                    "合理分配资源很重要",
                ],
                wait_for_action="continue"
            ),
            
            # 步骤9：帮助
            TutorialStep(
                "获取帮助",
                [
                    "按 [H] 随时打开帮助面板",
                    "查看完整的快捷键和游戏提示",
                    "按 [C] 查看角色面板",
                    "按 [V] 查看共鸣系统",
                ],
                wait_for_action="continue"
            ),
            
            # 步骤10：完成
            TutorialStep(
                "教程完成",
                [
                    "你已经掌握了基础操作",
                    "现在开始你的修仙之旅吧！",
                    "祝你好运！",
                ],
                wait_for_action="continue"
            ),
        ]
    
    def start(self):
        """开始教程"""
        self.active = True
        self.current_step = 0
        for step in self.steps:
            step.completed = False
    
    def skip(self):
        """跳过教程"""
        self.active = False
        self.first_time = False
    
    def next_step(self):
        """下一步"""
        if self.current_step < len(self.steps):
            self.steps[self.current_step].completed = True
            self.current_step += 1
        
        if self.current_step >= len(self.steps):
            self.active = False
            self.first_time = False
    
    def check_action(self, action):
        """检查玩家是否完成了要求的操作"""
        if not self.active or self.current_step >= len(self.steps):
            return
        
        step = self.steps[self.current_step]
        if step.wait_for_action == action:
            self.next_step()
    
    def draw(self, screen):
        """绘制教程UI"""
        if not self.active or self.current_step >= len(self.steps):
            return
        
        step = self.steps[self.current_step]
        
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # 高亮区域
        if step.highlight_area:
            x, y, w, h = step.highlight_area
            pygame.draw.rect(screen, (255, 255, 100), (x, y, w, h), 3)
        
        # 教程面板
        panel_w, panel_h = 600, 300
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = SCREEN_HEIGHT - panel_h - 50
        
        # 面板背景
        panel_bg = pygame.Surface((panel_w, panel_h))
        panel_bg.fill((40, 40, 50))
        panel_bg.set_alpha(230)
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # 边框
        pygame.draw.rect(screen, (255, 215, 0), (panel_x, panel_y, panel_w, panel_h), 3)
        
        # 标题
        title_font = get_font(28)
        title = title_font.render(step.title, True, (255, 215, 0))
        title_x = panel_x + (panel_w - title.get_width()) // 2
        screen.blit(title, (title_x, panel_y + 20))
        
        # 文本
        text_font = get_font(20)
        text_y = panel_y + 70
        for line in step.text:
            text_surface = text_font.render(line, True, (220, 220, 220))
            text_x = panel_x + (panel_w - text_surface.get_width()) // 2
            screen.blit(text_surface, (text_x, text_y))
            text_y += 35
        
        # 进度
        progress_font = get_font(16)
        progress_text = f"步骤 {self.current_step + 1}/{len(self.steps)}"
        progress_surface = progress_font.render(progress_text, True, (150, 150, 150))
        screen.blit(progress_surface, (panel_x + 20, panel_y + panel_h - 35))
        
        # 跳过提示
        skip_text = "[ESC] 跳过教程"
        skip_surface = progress_font.render(skip_text, True, (150, 150, 150))
        screen.blit(skip_surface, (panel_x + panel_w - skip_surface.get_width() - 20, panel_y + panel_h - 35))
    
    def handle_input(self, event):
        """处理输入"""
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            # 跳过教程
            if event.key == pygame.K_ESCAPE:
                self.skip()
                return True
            
            # 继续
            if event.key == pygame.K_SPACE:
                step = self.steps[self.current_step]
                if step.wait_for_action == "continue":
                    self.next_step()
                return True
        
        return False


# ==================== 全局实例 ====================

_tutorial = None


def init_tutorial():
    """初始化教程系统"""
    global _tutorial
    _tutorial = Tutorial()
    return _tutorial


def get_tutorial():
    """获取教程实例"""
    global _tutorial
    if _tutorial is None:
        _tutorial = Tutorial()
    return _tutorial


def should_show_tutorial():
    """是否应该显示教程（首次游戏）"""
    tutorial = get_tutorial()
    return tutorial.first_time


def start_tutorial():
    """开始教程"""
    tutorial = get_tutorial()
    tutorial.start()


def skip_tutorial():
    """跳过教程"""
    tutorial = get_tutorial()
    tutorial.skip()
