# 游戏中使用 32 帧动画指南

## ✅ 当前状态

游戏已经完全支持 32 帧动画！

### 玩家动画（player.py）

```python
# 第 692 行
idx = play_animation(frames, self.anim_timer, fps=8)
```

- ✅ 使用 `fps=8`（每秒 8 帧）
- ✅ `anim_timer` 在 update 中累加：`self.anim_timer += dt`
- ✅ 支持任意帧数（4 帧、32 帧都可以）

---

## 📦 如何添加 32 帧角色

### 1. 准备精灵图

碧落的例子：
- **原始尺寸**：3860×3860
- **网格布局**：6×6 = 36 格子
- **使用帧数**：前 32 帧
- **单帧尺寸**：640×640（原始）

### 2. 缩放到游戏尺寸

```python
# 目标单帧尺寸：48×48（清晰可见）
# 6×6 网格 = 288×288 总尺寸

from PIL import Image
img = Image.open("碧落原图.png")
scaled = img.resize((288, 288), Image.LANCZOS)
scaled.save("assets/partner_biluo.png")
```

### 3. 在游戏中加载

```python
from tools.sprite_loader import load_sprite_sheet_grid

# 加载 6×6 网格（36 帧）
all_frames = load_sprite_sheet_grid("assets/partner_biluo.png", cols=6, rows=6)

# 只用前 32 帧
frames = all_frames[:32]
```

### 4. 播放动画

```python
class Partner:
    def __init__(self):
        self.frames = load_sprite_sheet_grid("assets/partner_biluo.png", cols=6, rows=6)[:32]
        self.anim_timer = 0.0
    
    def update(self, dt):
        self.anim_timer += dt
    
    def draw(self, screen, x, y):
        from tools.sprite_loader import play_animation
        idx = play_animation(self.frames, self.anim_timer, fps=8)
        screen.blit(self.frames[idx], (x, y))
```

---

## 🎯 不同角色的帧数

| 角色类型 | 帧数 | 网格 | FPS | 循环时间 |
|---------|------|------|-----|---------|
| 主角 | 4 | 2×2 | 8 | 0.5秒 |
| NPC | 4 | 2×2 | 8 | 0.5秒 |
| 伙伴（碧落等） | 32 | 6×6 | 8 | 4秒 |
| 敌人 | 4 | 2×2 | 8 | 0.5秒 |
| Boss | 4 | 2×2 | 8 | 0.5秒 |

**说明**：
- 4 帧适合简单动作（悬浮、原地踏步）
- 32 帧适合细腻动作（站立呼吸、复杂动画）
- 所有角色统一用 fps=8，保持一致性

---

## 🔧 性能优化

### 内存占用

- **4 帧**（48×48）：约 36 KB
- **32 帧**（48×48）：约 288 KB
- **影响**：可忽略（现代设备轻松支持）

### 渲染性能

- 每帧只绘制 1 张图片
- 无论 4 帧还是 32 帧，性能相同
- 瓶颈在缩放（`pygame.transform.scale`）

### 优化建议

```python
# 预缩放所有帧（初始化时）
scaled_frames = [
    pygame.transform.scale(f, (target_w, target_h))
    for f in frames
]

# 绘制时直接用
screen.blit(scaled_frames[idx], (x, y))
```

---

## 📋 待办事项

### 当前已完成
- ✅ `sprite_loader.py` 支持任意网格
- ✅ `play_animation()` 支持任意帧数
- ✅ 玩家使用 fps=8
- ✅ 测试脚本验证 32 帧流畅

### 需要添加
- [ ] 村子场景中 NPC/伙伴使用 32 帧
- [ ] 战斗场景中伙伴使用 32 帧
- [ ] 敌人/Boss 如果有 32 帧，也支持

---

## 🎨 美术资源清单

### 已有（测试通过）
- ✅ 碧落：32 帧（6×6 网格）

### 待制作
- [ ] 主角：4 帧或 32 帧
- [ ] 栖霞：4 帧或 32 帧
- [ ] 玄真：4 帧或 32 帧
- [ ] 铸心：4 帧或 32 帧
- [ ] 玄霄：4 帧或 32 帧
- [ ] 青璃：4 帧或 32 帧
- [ ] 赤渊：4 帧或 32 帧
- [ ] 墨羽：4 帧或 32 帧
- [ ] 6 种敌人：各 4 帧
- [ ] 4 个 Boss：各 4 帧

---

## 💡 总结

**游戏已经完全支持 32 帧动画！**

只需要：
1. 准备 32 帧精灵图（6×6 或其他网格）
2. 缩放到合适尺寸（单帧 48×48 推荐）
3. 用 `load_sprite_sheet_grid()` 加载
4. 用 `play_animation(frames, timer, fps=8)` 播放

**测试证明：32 帧 @ 8 fps 非常流畅！** 🎉
