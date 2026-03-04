# 伙伴美术流程与模板

> 伙伴只需村子展示，状态比主角少，流程可精简。

---

## 目标

- 为 5 位伙伴（玄霄、青璃、赤渊、碧落、墨羽）制作村子立绘
- 每人 **1 种状态**：站立（可选 4 帧轻微呼吸增加活气）
- 不参与战斗实体表现，无需死亡、攻击等状态

---

## 约束

| 项目 | 约束 |
|------|------|
| 状态数量 | 每人 1 种（站立 / 站立呼吸） |
| 帧数 | 1 帧（静态）或 4 帧（轻微呼吸） |
| 展示场景 | 村子房间（约 100×90 像素区域） |
| 输出尺寸 | 32×32 或 64×64 单帧，透明背景 |
| 风格 | 与主角一致的像素风 |

---

## 流程总览

```
Step 1: MJ 生成原图（每人 1 张，提示词按身份定制）
  → Step 2: 转像素图
  → Step 3: 生成站立图（1 帧或 4 帧轻微呼吸）
  → Step 4: 放入 assets，命名 partner_{id}.png
```

---

## Step 1：MJ 生成原图（每人 1 张）

**目标**：得到每位伙伴的 1 张基础图，用于转像素和站立图。

**操作**：在 MJ 中 `/imagine` 后，先粘贴参考图 URL（主角图，用于保持风格一致），再粘贴下方对应伙伴的完整提示词。**可直接整段复制到 MJ**。

**主角参考图 URL**（用于风格一致，每个伙伴提示词前都要加）：
```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc&
```

**5 位伙伴完整 MJ 提示词**（含参考图 URL，可直接复制）：

### 玄霄（雷宗掌门）
```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A mature Chinese male cultivator, sect leader, dignified, wearing dark blue and silver daoist robes with thunder motifs, black hair in formal topknot, no weapon, arms relaxed, standing calmly, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

### 青璃（青丘狐族长老）
```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& An elegant Chinese fox spirit elder, female, wearing flowing green and jade robes, fox ears visible, long dark hair, serene expression, no weapon, standing calmly, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

### 赤渊（散修剑尊）
```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A weathered Chinese male swordsman, lone cultivator, wearing worn dark red and brown robes, sword sheathed at side or back, short beard, determined expression, standing calmly, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

### 碧落（丹道宗师）
```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A gentle Chinese female alchemist, wearing soft blue and white robes, hair in simple bun, holding a small pill or herb (optional), calm expression, standing calmly, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

### 墨羽（影宗宗主）
```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A mysterious Chinese male in dark grey and black robes, shadow sect master, face partially obscured, hood or cloak, no weapon visible, standing calmly, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

**MJ 参数说明**：与主角一致，`--ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils`。不要加 `--p`。

**验收**：全身、正面、居中、纯色背景、颜色饱满、无特效、与主角风格一致。

---

## Step 2：转像素图

**目标**：把 Step 1 的 MJ 原图转成像素风格，作为 Step 3 的参考图。

**操作**：上传原图到 Nano Banana（或同类工具），粘贴下方提示词。**若 64×64 和 128×128 生成结果相同**，请在工具的「输出尺寸」设置中单独指定，或生成后用图像软件缩放；提示词内用「像素密度描述」区分粗细风格。

**推荐：方案 A（粗像素，约 64×64，8-bit 风格）**：
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

**细像素（方案 B）** 见 `docs/NANOBANANA_PROMPTS.md` 第二节。

**验收**：主体清晰、像素风、透明背景、与主角风格一致。

---

## Step 3：生成站立图

**目标**：用参考图生成村子用的站立立绘。

### 方案 A：单帧静态（最简单）

直接使用 Step 2 的像素图，无需再生成。重命名为 `partner_{id}.png` 即可。

### 方案 B：4 帧轻微呼吸（推荐）

用参考图 + 下方模板，生成 2×2 精灵图（4 帧），与主角待机布局一致。

**4 帧站立呼吸模板**：
```
[Overall Format]
A 2D game sprite sheet layout, arranged in a 2×2 grid (4 distinct frames: top-left, top-right, bottom-left, bottom-right). Pure transparent background (PNG alpha channel). Pixel art style.

[Character Reference]
Use the provided reference image for the character design. Match the character's appearance, clothing, hair, and style exactly from the reference. Do not alter or redesign the character. CRITICAL: Preserve the pixel art style of the reference. No anti-aliasing, no smooth gradients, no high-resolution rendering. Keep crisp pixel edges and the same pixel density.

[Crucial: Frame-by-Frame Physical Description]
The character is STANDING on ground in ALL 4 frames. Minimal movement—gentle breathing cycle only. Vertical order: Frame 1 (lowest) < Frame 2 (rising) < Frame 3 (highest) > Frame 4 (descending). Frame 4 must be LOWER than Frame 2 for smooth loop.
* Frame 1 (Top-left): Character standing, neutral pose. Chest contracted (exhale complete). Body at LOWEST point of breath cycle. Robes/clothing relaxed, hanging down.
* Frame 2 (Top-right): Character standing, same pose. Chest expanding (inhale). Body RISING. Robes/clothing beginning to lift slightly.
* Frame 3 (Bottom-left): Character standing, same pose. Chest fully expanded (inhale complete). Body at HIGHEST point. Robes/clothing lifted, fabric slightly puffed.
* Frame 4 (Bottom-right): Character standing, same pose. Chest contracting (exhale). Body DESCENDING. Robes/clothing relaxing. Body LOWER than Frame 2 for smooth loop.

[Liveliness and Material Detail]
The fabric of robes/clothing must have subtle different shapes in EVERY frame to convey gentle breathing. Very subtle difference between frames—no exaggerated movement. Pixel art style, crisp pixel edges, no anti-aliasing.
```

---

## Step 4：放入 assets 与命名

| 文件名 | 伙伴 |
|--------|------|
| `assets/partner_xuanxiao.png` | 玄霄 |
| `assets/partner_qingli.png` | 青璃 |
| `assets/partner_chiyuan.png` | 赤渊 |
| `assets/partner_biluo.png` | 碧落 |
| `assets/partner_moyu.png` | 墨羽 |

**验收**：文件存在、透明背景、像素风、尺寸适配村子房间。

---

## 与主角的差异

| 项目 | 主角 | 伙伴 |
|------|------|------|
| 状态数 | 待机、死亡（2 种） | 站立（1 种） |
| 帧数/状态 | 4 帧 | 1 帧或 4 帧 |
| 布局 | 2×2 网格 | 单张或 2×2 |
| 展示场景 | 战斗、村子 | 仅村子 |
| 动作 | 悬浮、倒地 | 站立、轻微呼吸 |

---

## 相关文档

| 文档 | 用途 |
|------|------|
| `docs/CHARACTER_ART_WORKFLOW.md` | 主角完整流程 |
| `docs/SPRITE_FRAME_PROMPT_TEMPLATE.md` | 通用模板结构 |
| `docs/PARTNER_VILLAGER_INITIAL.md` | 伙伴身份与设定 |
