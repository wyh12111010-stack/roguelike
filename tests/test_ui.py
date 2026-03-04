"""
UI 系统单元测试
"""
import pytest
import pygame

def test_ui_manager_creation(screen):
    """测试 UI 管理器创建"""
    from ui.ui_manager import UIManager
    
    ui_manager = UIManager(800, 600)
    
    assert ui_manager is not None
    assert ui_manager.screen_width == 800
    assert ui_manager.screen_height == 600
    assert ui_manager.hud is not None
    assert ui_manager.fabao_display is not None
    assert ui_manager.character_panel is not None

def test_ui_manager_set_player(screen, player):
    """测试 UI 管理器设置玩家"""
    from ui.ui_manager import UIManager
    
    ui_manager = UIManager(800, 600)
    ui_manager.set_player(player)
    
    assert ui_manager.player is not None
    assert ui_manager.hud.player is not None
    assert ui_manager.fabao_display.player is not None
    assert ui_manager.character_panel.player is not None

def test_ui_manager_update(screen, player):
    """测试 UI 管理器更新"""
    from ui.ui_manager import UIManager
    
    ui_manager = UIManager(800, 600)
    ui_manager.set_player(player)
    
    # 更新几帧
    for _ in range(5):
        ui_manager.update(0.016)
    
    # 不应该抛出异常

def test_ui_manager_draw(screen, player):
    """测试 UI 管理器绘制"""
    from ui.ui_manager import UIManager
    
    ui_manager = UIManager(800, 600)
    ui_manager.set_player(player)
    
    # 绘制
    ui_manager.draw(screen)
    
    # 不应该抛出异常

def test_hud_component(screen, player):
    """测试 HUD 组件"""
    from ui.hud import HUD
    
    hud = HUD(10, 10)
    hud.set_player(player)
    
    # 更新
    hud.update(0.016, (0, 0))
    
    # 绘制
    hud.draw(screen)
    
    # 不应该抛出异常

def test_progress_bar(screen):
    """测试进度条组件"""
    from ui.components import ProgressBar, Colors
    
    bar = ProgressBar(10, 10, 100, 20, Colors.HP_RED, Colors.HP_RED_BG)
    
    # 设置值
    bar.set_value(50, 100)
    assert bar.value == 0.5
    
    # 更新
    bar.update(0.016, (0, 0))
    
    # 绘制
    bar.draw(screen)
    
    # 不应该抛出异常

def test_panel_component(screen):
    """测试面板组件"""
    from ui.components import Panel
    
    panel = Panel(10, 10, 200, 100)
    
    # 绘制
    panel.draw(screen)
    
    # 不应该抛出异常

def test_character_panel_toggle(screen, player):
    """测试角色面板切换"""
    from ui.character_panel import CharacterPanel
    
    panel = CharacterPanel(800, 600)
    panel.set_player(player)
    
    # 初始状态
    assert panel.visible == False
    
    # 切换
    panel.toggle()
    assert panel.visible == True
    
    # 再次切换
    panel.toggle()
    assert panel.visible == False

def test_ui_event_handling(screen, player):
    """测试 UI 事件处理"""
    from ui.ui_manager import UIManager
    
    ui_manager = UIManager(800, 600)
    ui_manager.set_player(player)
    
    # 创建按键事件
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_i)
    
    # 处理事件
    handled = ui_manager.handle_event(event)
    
    assert handled == True
    assert ui_manager.character_panel.visible == True
