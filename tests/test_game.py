"""
游戏系统单元测试
"""
import pytest

def test_game_creation(game):
    """测试游戏对象创建"""
    assert game is not None
    assert game.scene == "village"
    assert hasattr(game, 'ui_manager')

def test_game_update(game):
    """测试游戏更新"""
    # 更新几帧
    for _ in range(5):
        game.update(0.016)
    
    # 不应该抛出异常

def test_game_draw(game, screen):
    """测试游戏绘制"""
    game.draw()
    
    # 不应该抛出异常

@pytest.mark.integration
def test_game_village_scene(game):
    """测试村子场景"""
    assert game.scene == "village"
    
    # 更新村子场景
    game.update(0.016)
    game.draw()
    
    # 不应该抛出异常

def test_event_system():
    """测试事件系统"""
    from core import EventBus
    from core.events import PLAYER_HIT
    
    # 测试事件订阅
    called = [False]
    
    def handler(**kwargs):
        called[0] = True
    
    EventBus.on(PLAYER_HIT, handler)
    EventBus.emit(PLAYER_HIT, damage=10)
    
    assert called[0] == True
    
    # 清理
    EventBus.off(PLAYER_HIT, handler)

def test_save_system():
    """测试存档系统"""
    from save import RunSaveData, PlayerSaveData
    from meta import meta
    
    # 检查 meta 对象
    assert hasattr(meta, 'daoyun')
    assert hasattr(meta, 'unlocked_linggen')
    assert hasattr(meta, 'unlocked_fabao')
    
    # 创建存档数据
    save_data = RunSaveData(
        scene="village",
        linggen_choice=0,
        fabao_choice=0
    )
    
    assert save_data.scene == "village"
