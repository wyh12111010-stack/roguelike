"""
敌人精灵加载辅助
"""

import pygame

from config_assets import get_character_sprite

# 敌人精灵缓存
_enemy_sprites = {}


def load_enemy_sprite(enemy_type):
    """加载敌人精灵"""
    if enemy_type not in _enemy_sprites:
        try:
            path = get_character_sprite("enemy", f"enemy_{enemy_type}")
            sprite = pygame.image.load(path)
            # 缩放到合适大小（敌人比玩家小一些）
            w, h = sprite.get_size()
            scale = 1.5  # 缩放倍数
            sprite = pygame.transform.scale(sprite, (int(w * scale), int(h * scale)))
            _enemy_sprites[enemy_type] = sprite
        except Exception as e:
            print(f"加载敌人精灵失败: {enemy_type} - {e}")
            _enemy_sprites[enemy_type] = None
    return _enemy_sprites[enemy_type]
