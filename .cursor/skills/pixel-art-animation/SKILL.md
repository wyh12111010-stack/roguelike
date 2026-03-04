---
name: pixel-art-animation
description: Generates pixel art animations from static sprites and integrates them into pygame. Use when creating pixel animations, converting static pixel art to animated sprites, loading sprite sheets, or when the user mentions Rika AI, Nano Banana, procedural animation, or pixel sprite frames.
---

# 像素画转像素动画

## 能力范围

| 方式 | 谁做 | 适用 |
|------|------|------|
| **程序化生成** | 本 Skill 脚本 | 待机、轻微浮动等低帧数（2–4 帧） |
| **Rika AI** | 外部服务 | 攻击、行走等完整动画（需手动上传） |

本 Skill 提供：程序化动画脚本、精灵表加载、pygame 接入示例。

---

## 快速流程

### 方案 A：程序化（本地，低帧数）

```bash
python .cursor/skills/pixel-art-animation/scripts/procedural_anim.py assets/player_idle.png -o assets/player_idle_anim --mode bob --frames 4
```

输出：`player_idle_anim_0.png` ~ `player_idle_anim_3.png`

### 方案 B：Rika AI（外部，完整动画）

1. Nano Banana 生成原图 → Image to Pixel Art 转 64×64/128×128
2. 上传到 Rika AI，选动作（IDLE/ATTACK/WALK 等）
3. 导出序列帧或精灵表
4. 用本 Skill 的加载逻辑接入 pygame

---

## 程序化模式

| mode | 效果 | 帧数建议 |
|------|------|----------|
| `bob` | 上下轻微浮动（待机呼吸） | 4 |
| `pulse` | 轻微缩放脉动 | 4 |
| `shift` | 左右 1px 微移 | 2–4 |

---

## pygame 接入

```python
# 加载精灵表或序列帧
from .cursor.skills.pixel-art-animation.scripts.sprite_loader import load_sprite_sheet, load_sequence

# 序列帧
frames = load_sequence("assets/player_idle_anim", 4)
# 精灵表（横向排列）
frames = load_sprite_sheet("assets/player_sheet.png", frame_w=32, frame_count=4)

# 播放
from tools.sprite_loader import play_animation
frame_idx = play_animation(frames, anim_timer, fps=8)
screen.blit(frames[frame_idx], (x, y))
```

详见 [reference.md](reference.md)。`sprite_loader` 已放在项目 `tools/` 目录。
