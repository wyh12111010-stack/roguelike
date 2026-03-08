"""
单元测试框架 - 使用 pytest
测试核心游戏逻辑
"""

import os
import sys

import pygame
import pytest

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="session")
def pygame_init():
    """初始化 pygame（整个测试会话只初始化一次）"""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def screen(pygame_init):
    """创建测试用的屏幕"""
    return pygame.display.set_mode((800, 600))


@pytest.fixture
def player():
    """创建测试用的玩家"""
    from config import ARENA_H, ARENA_W, ARENA_X, ARENA_Y
    from player import Player

    return Player(ARENA_X + ARENA_W // 2, ARENA_Y + ARENA_H // 2)


@pytest.fixture
def game(screen):
    """创建测试用的游戏对象"""
    from game import Game

    return Game(screen)


# 测试配置
def pytest_configure(config):
    """pytest 配置"""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
