# 32 帧动画使用示例

## 加载 32 帧精灵图

```python
from tools.sprite_loader import load_sprite_sheet_grid, play_animation

# 加载碧落的 32 帧动画（假设是 8×4 网格）
biluo_frames = load_sprite_sheet_grid("assets/partner_biluo.png", cols=8, rows=4)

# 或者如果是 4×8 网格
# biluo_frames = load_sprite_sheet_grid("assets/partner_biluo.png", cols=4, rows=8)
```

## 在游戏中播放

```python
class Partner:
    def __init__(self):
        self.frames = load_sprite_sheet_grid("assets/partner_biluo.png", cols=8, rows=4)
        self.anim_timer = 0.0
        self.fps = 8  # 每秒 8 帧
    
    def update(self, dt):
        # dt 是帧间隔时间（秒），例如 1/60 ≈ 0.0167
        self.anim_timer += dt
    
    def draw(self, screen, x, y):
        # 获取当前帧索引
        frame_idx = play_animation(self.frames, self.anim_timer, fps=self.fps)
        
        # 绘制当前帧
        screen.blit(self.frames[frame_idx], (x, y))
```

## 性能说明

- **32 帧 @ 8 fps**：完整循环需要 4 秒（32 / 8 = 4）
- **内存占用**：32 帧比 4 帧多 8 倍，但对于小尺寸像素画（32-48px）影响很小
- **流畅度**：非常流畅，适合站立呼吸等细腻动画

## 不同 FPS 的效果

| FPS | 完整循环时间 | 效果 |
|-----|-------------|------|
| 4 | 8 秒 | 很慢，适合极慢动作 |
| 8 | 4 秒 | **推荐**，流畅且自然 |
| 12 | 2.67 秒 | 较快，适合快节奏动作 |
| 16 | 2 秒 | 很快，可能过快 |

## 混合使用

```python
# 主角：4 帧悬浮动画
player_frames = load_sprite_sheet_grid("assets/player_idle.png", cols=2, rows=2)
player_idx = play_animation(player_frames, timer, fps=4)

# 伙伴：32 帧站立呼吸
partner_frames = load_sprite_sheet_grid("assets/partner_biluo.png", cols=8, rows=4)
partner_idx = play_animation(partner_frames, timer, fps=8)

# 敌人：4 帧原地踏步
enemy_frames = load_sprite_sheet_grid("assets/enemy_melee_anim.png", cols=2, rows=2)
enemy_idx = play_animation(enemy_frames, timer, fps=6)
```

## 注意事项

1. **确认网格布局**：检查精灵图是 8×4 还是 4×8
2. **质心对齐**：如果动画跳动，使用 `get_content_center()` 对齐
3. **缩放**：如果原图太大，先缩放再加载

```python
# 缩放示例
import pygame
sheet = pygame.image.load("assets/partner_biluo.png")
# 缩小到 1/10
new_size = (sheet.get_width() // 10, sheet.get_height() // 10)
sheet = pygame.transform.scale(sheet, new_size)
pygame.image.save(sheet, "assets/partner_biluo_scaled.png")
```
