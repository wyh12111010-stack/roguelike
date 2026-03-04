# 主角美术流程

> 主角（男性修士）完整美术流程：MJ 原图 → 转像素 → 待机帧 → 死亡帧

---

## 目标

为主角制作 2 种状态：
- **待机**：4 帧悬浮 bobbing
- **死亡**：4 帧倒地序列

---

## 约束

| 项目 | 约束 |
|------|------|
| 状态数量 | 2 种（待机、死亡） |
| 帧数/状态 | 4 帧 |
| 输出格式 | 2×2 网格精灵图，PNG 透明背景 |
| 风格 | 像素风，粗像素（约 64×64 效果） |

---

## Step 1：MJ 生成原图

**目标**：得到 1 张主角基础图，用于后续转像素和生成各状态。

**操作**：在 MJ 中 `/imagine` 后，粘贴下方完整提示词（含参考图 URL）。

### 主角 MJ 提示词（完整，可直接复制）

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A young Chinese male cultivator in xianxia style, floating in mid-air with legs naturally bent, robes and sleeves flowing downward, wearing traditional daoist robes in vibrant light blue and white, long wide sleeves, black hair in a simple topknot, no weapon, empty hands, arms relaxed at sides, calm serene expression, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, soft diffused lighting, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

**参数说明**：
- `--ar 1:1`：方形，便于转像素
- `--niji 7`：动漫模型 V7
- `--s 250`：风格化强度，颜色更饱满
- `--no glow aura ...`：排除特效

**注意**：不要加 `--p`（需先评分 40+ 张图才能用）。

**验收**：全身、正面、居中、纯色背景、颜色饱满、无特效光晕。

---

## Step 2：转像素图

**目标**：把 MJ 原图转成像素风格，作为 Step 3 的参考图。

**操作**：上传原图到 Nano Banana，粘贴下方提示词。

### 转像素提示词（粗像素，约 64×64 效果）

```
Convert the provided reference image into pixel art. CRITICAL requirements:
- EXTREMELY LOW RESOLUTION: 8-bit NES/Game Boy style. Each pixel block must be 3-5 pixels wide—very chunky, blocky, minimal detail
- Total character should fit in roughly 32-48 pixels width, 64-80 pixels height. Very few pixels to define each feature
- NO anti-aliasing, NO smooth gradients, NO high-resolution rendering—only crisp blocky pixel edges
- Preserve the character's appearance, clothing, hair, pose, colors from the reference—simplified into chunky blocks
- Style: extremely chunky retro pixel art, vivid saturated colors, high contrast
- Background: fully transparent (PNG alpha channel)
- Character centered, full body visible, facing front
- No glow, no aura, no particles—clean minimal pixel art only
```

**注意**：若工具忽略提示词中的数字，请在「输出尺寸」设置中单独指定 64×64 或 64×128。

**验收**：主体清晰、像素风、透明背景、角色正面、无抗锯齿。

---

## Step 3：生成待机帧（2×2 精灵图）

**目标**：用参考图 + 提示词，生成待机 4 帧（悬浮 bobbing）。

**操作**：上传 Step 2 的像素图到 Nano Banana，粘贴下方提示词。

### 待机帧提示词（完整）

```
[Overall Format]
A 2D game sprite sheet layout, arranged in a 2×2 grid (4 distinct frames: top-left, top-right, bottom-left, bottom-right). Pure transparent background (PNG alpha channel). Pixel art style.

[Character Reference]
Use the provided reference image for the character design. Match the character's appearance, clothing, hair, and style exactly from the reference. Do not alter or redesign the character. CRITICAL: Preserve the pixel art style of the reference. No anti-aliasing, no smooth gradients, no high-resolution rendering. Keep crisp pixel edges and the same pixel density.

[Crucial: Frame-by-Frame Physical Description]
The character is FLOATING in ALL 4 frames—never sitting, never standing on ground. Each frame shows a different vertical position within the float cycle. Vertical order: Frame 1 (lowest) < Frame 2 (rising) < Frame 3 (highest) > Frame 4 (descending). Frame 4 must be LOWER than Frame 2 for smooth loop.
* Frame 1 (Top-left): Character at the LOWEST point of the float cycle. Still FLOATING, legs bent as if hovering—NOT sitting on ground. Body slightly lower than Frame 2. Robes pooled upwards.
* Frame 2 (Top-right): Character RISING. Body higher than Frame 1. Robes trailing downwards.
* Frame 3 (Bottom-left): Character at the HIGHEST point. Weightless. Robes spread out.
* Frame 4 (Bottom-right): Character DESCENDING. Body LOWER than Frame 2. Robes puffed upwards.

[Liveliness and Material Detail]
The fabric of the robes must have different waving folds and flowing shapes in EVERY frame to convey gentle air movement and liveliness. No stiff fabric. Pixel art style, crisp pixel edges, no anti-aliasing.
```

**验收**：2×2 网格、4 帧、PNG 透明背景、像素风、每帧有明显差异（高度与道袍褶皱）。

---

## Step 4：生成死亡帧（2×2 精灵图）

**目标**：用参考图 + 提示词，生成死亡 4 帧（倒地序列）。

**操作**：上传 Step 2 的像素图到 Nano Banana，粘贴下方提示词。

### 死亡帧提示词（完整）

```
[Overall Format]
A 2D game sprite sheet layout, arranged in a 2×2 grid (4 distinct frames: top-left, top-right, bottom-left, bottom-right). Pure transparent background (PNG alpha channel). Pixel art style.

[Character Reference]
Use the provided reference image for the character design. Match the character's appearance, clothing, hair, and style exactly from the reference. Do not alter or redesign the character. CRITICAL: Preserve the pixel art style of the reference. No anti-aliasing, no smooth gradients, no high-resolution rendering. Keep crisp pixel edges and the same pixel density.

[Crucial: Frame-by-Frame Physical Description]
Each of the 4 frames MUST show the character in a DIFFERENT pose to create a collapse sequence. They must NOT be identical.
* Frame 1 (Top-left): Character standing upright, intact. Calm pose, robes hanging normally.
* Frame 2 (Top-right): Beginning to collapse. Body leaning backward. Arms starting to fall. Robes and hair beginning to scatter.
* Frame 3 (Bottom-left): Mid-fall. Body tilting sharply. Robes and hair disheveled, flying outward from the impact.
* Frame 4 (Bottom-right): Fully collapsed. Body on ground or dissipating. Robes and hair fully scattered, spirit energy fading.

[Liveliness and Material Detail]
The fabric and hair must show progressive disruption in EVERY frame. Pixel art style, crisp pixel edges, no anti-aliasing.
```

**验收**：2×2 网格、4 帧、PNG 透明背景、像素风、每帧有明显差异（站立→后仰→下落→倒地）。

---

## Step 5：预览与接入游戏

### 5.1 预览

```bash
python tools/sprite_preview.py
```

- 拖放或选择精灵图
- 按 A 键切换中间轴对齐
- 空格暂停，左右键切帧

### 5.2 对齐质心（若需要）

AI 生成的各帧质心可能不一致，导致播放时"跳动"。

```bash
# 批量对齐
python tools/align_sprites.py nanobanana_in/

# 单个对齐
python tools/align_sprites.py nanobanana_in/主角待机图.png
```

### 5.3 复制到 assets

| 文件名 | 用途 |
|--------|------|
| `assets/player_idle.png` | 待机 |
| `assets/player_death.png` | 死亡 |

### 5.4 运行游戏

```bash
python main.py
```

**验收**：游戏中能看到待机悬浮动画和死亡倒地动画。

---

## 相关文档

| 文档 | 用途 |
|------|------|
| `docs/SPRITE_FRAME_PROMPT_TEMPLATE.md` | 通用模板结构 |
| `docs/SPRITE_ALIGNMENT_GUIDE.md` | 质心对齐指南 |
