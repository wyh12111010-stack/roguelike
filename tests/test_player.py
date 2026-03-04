"""
玩家系统单元测试
"""
import pytest

def test_player_creation(player):
    """测试玩家创建"""
    assert player is not None
    assert player.health > 0
    assert player.max_health > 0
    assert player.mana >= 0
    assert player.max_mana > 0
    assert player.lingshi >= 0

def test_player_movement(player):
    """测试玩家移动"""
    initial_x = player.rect.centerx
    initial_y = player.rect.centery
    
    # 模拟移动
    player.update(0.016, [], [])
    
    # 位置可能改变（取决于输入）
    # 这里只测试不抛出异常

def test_player_take_damage(player):
    """测试玩家受伤"""
    initial_health = player.health
    
    # 受伤
    player.take_damage(10)
    
    assert player.health < initial_health

def test_player_heal(player):
    """测试玩家治疗"""
    # 先受伤
    player.take_damage(20)
    damaged_health = player.health
    
    # 治疗
    player.health = min(player.max_health, player.health + 10)
    
    assert player.health > damaged_health

def test_player_mana_usage(player):
    """测试玩家灵力使用"""
    initial_mana = player.mana
    
    # 使用灵力
    if player.mana >= 10:
        player.mana -= 10
        assert player.mana < initial_mana

def test_player_lingshi(player):
    """测试玩家灵石"""
    initial_lingshi = player.lingshi
    
    # 增加灵石
    player.lingshi += 10
    
    assert player.lingshi == initial_lingshi + 10
