# 像素动画 pygame 接入参考

## 替换玩家/敌人绘制

当前 `player.draw()` 使用 `pygame.draw.rect`。接入精灵后改为：

```python
# player.py 或 enemy.py
def draw(self, screen):
    if hasattr(self, "anim_frames") and self.anim_frames:
        idx = play_animation(self.anim_frames, self.anim_timer, fps=8)
        img = self.anim_frames[idx]
        # 按朝向翻转
        if self.facing < -0.5 * math.pi or self.facing > 0.5 * math.pi:
            img = pygame.transform.flip(img, True, False)
        screen.blit(img, self.rect.topleft)
    else:
        pygame.draw.rect(screen, COLOR_PLAYER, self.rect)  # 回退
```

## 初始化动画

```python
# 在 Player.__init__ 或加载时
from tools.sprite_loader import load_sequence, play_animation

self.anim_frames = []
self.anim_timer = 0.0
anim_path = "assets/sprites/player_idle"
if os.path.exists(anim_path):
    self.anim_frames = load_sequence(anim_path, 4, prefix="frame")

# 在 update 中
self.anim_timer += dt
```

## 精灵尺寸

- 32×32：角色、敌人
- 64×64：立绘、Boss
- 与 `self.rect` 一致：如 rect 为 32×32，精灵也建议 32×32

## Rika AI 导出格式

- 序列帧：`frame_0.png` ~ `frame_N.png`
- 精灵表：单张横向拼接，用 `load_sprite_sheet` 加载
