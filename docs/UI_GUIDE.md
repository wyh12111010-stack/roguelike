# 🎨 修仙风格 UI 系统使用指南

## 快速开始

### 1. 运行 UI 演示
```bash
# Windows
run_ui_demo.bat

# 或直接运行
py demo_ui.py
```

**演示内容**：
- 动态星空背景
- 仙气粒子效果
- 古风面板和边框
- 渐变按钮
- 资源显示（道韵、灵石）
- 进度条（生命、灵力）
- 五行元素展示
- 光晕效果

### 2. 运行游戏
```bash
# Windows
run_game.bat

# 或直接运行
py main.py
```

**新增视觉效果**：
- 村子场景全面升级
- 动态背景和粒子
- 古风 UI 元素
- 光晕和渐变效果

---

## 核心文件

### `ui_theme.py` - UI 主题系统
**功能**：
- 配色方案（修仙主题色）
- 渐变效果
- 光晕效果
- 古风边框
- 仙气粒子
- 动态背景
- UI 组件（面板、按钮、资源、进度条）

### `village_visual.py` - 村子视觉效果
**功能**：
- 增强版房间绘制
- 增强版传送门
- 增强版玩家
- 增强版 HUD
- 增强版选择面板
- 增强版对话框

### `village.py` - 村子场景（已升级）
**改动**：
- 集成新的视觉系统
- 替换所有绘制函数

### `scenes/village_scene.py` - 村子场景逻辑（已升级）
**改动**：
- 添加视觉效果更新

---

## 使用示例

### 1. 绘制古风面板

```python
from ui_theme import draw_panel
import pygame

# 创建面板区域
panel_rect = pygame.Rect(100, 100, 400, 300)

# 绘制面板（带标题和光晕）
draw_panel(screen, panel_rect, title="修仙界面", glow=True)
```

**效果**：
- 背景渐变（半透明）
- 四角光晕
- 金铜描边 + 转角装饰
- 标题光晕 + 下划线

---

### 2. 绘制修仙按钮

```python
from ui_theme import draw_button
import pygame

# 创建按钮区域
button_rect = pygame.Rect(200, 200, 120, 40)

# 检测鼠标悬停
mouse_pos = pygame.mouse.get_pos()
is_hover = button_rect.collidepoint(mouse_pos)

# 绘制按钮
draw_button(screen, button_rect, "开始修炼", is_hover, is_active=False)
```

**效果**：
- 背景渐变（上亮下暗）
- 悬停时显示光晕
- 金铜边框
- 文字颜色随状态变化

---

### 3. 绘制资源显示

```python
from ui_theme import draw_resource, THEME_COLORS

# 绘制道韵
draw_resource(screen, x=20, y=20, icon_text="道", value=1234, 
              color=THEME_COLORS["daoyun"])

# 绘制灵石
draw_resource(screen, x=20, y=70, icon_text="石", value=567,
              color=THEME_COLORS["lingshi"])
```

**效果**：
- 图标背景（渐变）
- 图标文字（道/石）
- 数值（大字体）
- 数值光晕

---

### 4. 绘制进度条

```python
from ui_theme import draw_progress_bar, THEME_COLORS

# 生命条
hp_rect = pygame.Rect(100, 100, 200, 30)
draw_progress_bar(screen, hp_rect, value=85, max_value=100,
                 color=THEME_COLORS["health"], show_text=True)

# 灵力条
mp_rect = pygame.Rect(100, 150, 200, 30)
draw_progress_bar(screen, mp_rect, value=60, max_value=100,
                 color=THEME_COLORS["mana"], show_text=True)
```

**效果**：
- 背景暗色
- 进度渐变填充
- 进度末端光晕
- 金铜边框
- 数值文字（带描边）

---

### 5. 绘制光晕效果

```python
from ui_theme import draw_glow, THEME_COLORS

# 在某个位置绘制光晕
center = (400, 300)
radius = 50
color = THEME_COLORS["immortal_gold"]
intensity = 0.5

draw_glow(screen, center, radius, color, intensity)
```

**效果**：
- 多层径向渐变
- 加法混合模式
- 可调强度

---

### 6. 创建动态背景

```python
from ui_theme import AnimatedBackground

# 创建背景实例
background = AnimatedBackground(width=800, height=600)

# 游戏循环中
def update(dt):
    background.update(dt)

def draw():
    background.draw(screen)
```

**效果**：
- 深邃星空渐变
- 100+ 闪烁星辰
- 星星亮度动态变化

---

### 7. 创建仙气粒子

```python
from ui_theme import ImmortalParticle, THEME_COLORS

# 创建粒子列表
particles = []

# 生成粒子
import random
x = random.randint(0, 800)
y = random.randint(500, 600)
color = random.choice([
    THEME_COLORS["immortal_jade"],
    THEME_COLORS["immortal_cyan"],
    THEME_COLORS["immortal_purple"],
])
particle = ImmortalParticle(x, y, color, lifetime=3.0)
particles.append(particle)

# 更新和绘制
def update(dt):
    particles[:] = [p for p in particles if p.update(dt)]

def draw():
    for particle in particles:
        particle.draw(screen)
```

**效果**：
- 从地面缓缓上升
- 碧玉/青灵/紫气三色
- 渐隐效果
- 轻微飘动

---

## 配色方案

### 修仙主题色

```python
from ui_theme import THEME_COLORS

# 修仙元素
THEME_COLORS["immortal_gold"]   # 仙金 (218, 165, 32)
THEME_COLORS["immortal_jade"]   # 碧玉 (64, 224, 208)
THEME_COLORS["immortal_red"]    # 朱砂 (220, 20, 60)
THEME_COLORS["immortal_purple"] # 紫气 (138, 43, 226)
THEME_COLORS["immortal_cyan"]   # 青灵 (0, 206, 209)

# 五行色
THEME_COLORS["fire"]   # 火红 (255, 69, 0)
THEME_COLORS["water"]  # 水蓝 (30, 144, 255)
THEME_COLORS["wood"]   # 木绿 (34, 139, 34)
THEME_COLORS["metal"]  # 金银 (192, 192, 192)
THEME_COLORS["earth"]  # 土褐 (139, 90, 43)

# 资源颜色
THEME_COLORS["daoyun"]  # 道韵（金色）
THEME_COLORS["lingshi"] # 灵石（青色）
THEME_COLORS["health"]  # 生命（朱红）
THEME_COLORS["mana"]    # 灵力（深空蓝）

# 文本颜色
THEME_COLORS["text_primary"]    # 主文本（米黄）
THEME_COLORS["text_secondary"]  # 次要文本
THEME_COLORS["text_highlight"]  # 高亮文本（金色）
THEME_COLORS["text_dim"]        # 暗淡文本
```

---

## 完整示例

### 创建一个修仙风格的设置面板

```python
import pygame
from ui_theme import (
    THEME_COLORS, draw_panel, draw_button, 
    draw_progress_bar, AnimatedBackground
)
from config import get_font

# 初始化
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# 创建背景
background = AnimatedBackground(800, 600)

# 游戏循环
running = True
volume = 80

while running:
    dt = clock.tick(60) / 1000.0
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 更新
    background.update(dt)
    mouse_pos = pygame.mouse.get_pos()
    
    # 绘制
    background.draw(screen)
    
    # 设置面板
    panel_rect = pygame.Rect(200, 100, 400, 400)
    draw_panel(screen, panel_rect, "设置", glow=True)
    
    # 音量标签
    font = get_font(18)
    label = font.render("音量", True, THEME_COLORS["text_primary"])
    screen.blit(label, (230, 180))
    
    # 音量条
    volume_rect = pygame.Rect(230, 220, 340, 30)
    draw_progress_bar(screen, volume_rect, volume, 100,
                     THEME_COLORS["immortal_cyan"], show_text=True)
    
    # 按钮
    btn_ok = pygame.Rect(250, 450, 120, 40)
    btn_cancel = pygame.Rect(430, 450, 120, 40)
    
    is_hover_ok = btn_ok.collidepoint(mouse_pos)
    is_hover_cancel = btn_cancel.collidepoint(mouse_pos)
    
    draw_button(screen, btn_ok, "确定", is_hover_ok, False)
    draw_button(screen, btn_cancel, "取消", is_hover_cancel, False)
    
    pygame.display.flip()

pygame.quit()
```

---

## 性能优化建议

### 1. 粒子数量控制
```python
# 限制粒子数量
MAX_PARTICLES = 100
if len(particles) < MAX_PARTICLES:
    particles.append(new_particle)
```

### 2. 光晕层数控制
```python
# 减少光晕层数以提升性能
draw_glow(screen, center, radius, color, intensity=0.3)  # 较低强度
```

### 3. 渐变缓存
```python
# 缓存常用渐变表面
gradient_cache = {}

def get_gradient(key, width, height, color_top, color_bottom):
    if key not in gradient_cache:
        gradient_cache[key] = create_gradient_surface(
            width, height, color_top, color_bottom
        )
    return gradient_cache[key]
```

### 4. 条件绘制
```python
# 只在需要时绘制光晕
if is_hover or is_active:
    draw_glow(screen, center, radius, color, intensity)
```

---

## 常见问题

### Q: 游戏运行变慢了？
A: 
1. 减少粒子数量（MAX_PARTICLES = 50）
2. 降低光晕强度（intensity = 0.2）
3. 减少光晕层数（修改 draw_glow 中的 range）

### Q: 如何自定义配色？
A:
```python
from ui_theme import THEME_COLORS

# 修改主题色
THEME_COLORS["immortal_gold"] = (255, 215, 0)  # 更亮的金色
THEME_COLORS["panel_border"] = (200, 180, 120)  # 更亮的边框
```

### Q: 如何禁用某些效果？
A:
```python
# 禁用光晕
draw_panel(screen, rect, title="面板", glow=False)

# 禁用粒子
# 注释掉粒子生成和更新代码
```

### Q: 如何添加新的 UI 组件？
A: 参考 `ui_theme.py` 中的现有组件，使用相同的风格：
- 渐变背景
- 金铜边框
- 光晕效果
- 统一配色

---

## 下一步

### 战斗场景美术升级
1. 复制 `village_visual.py` 的模式
2. 创建 `combat_visual.py`
3. 升级战斗场景的绘制函数
4. 添加技能特效、伤害飘字等

### 音效配合
1. 添加 UI 音效（点击、悬停）
2. 添加环境音效（仙气、风声）
3. 添加背景音乐（古风仙侠）

### 高级效果
1. 场景切换动画（淡入淡出）
2. 面板弹出动画
3. 按钮点击反馈
4. 页面滚动效果

---

## 文档

- **升级文档**：`docs/UI_UPGRADE.md`
- **对比文档**：`docs/UI_COMPARISON.md`
- **本指南**：`docs/UI_GUIDE.md`

---

**享受修仙风格的视觉体验！** ✨🎨
