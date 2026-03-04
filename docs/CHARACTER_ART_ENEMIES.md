# 敌人美术流程（6 种）

> melee、ranged、charge、aoe、homing、summon 完整美术流程

---

## 目标

为 6 种敌人各制作 2 种状态：
- **待机**：1 帧静态（或 2 帧轻微晃动）
- **死亡**：4 帧倒地序列

---

## 约束

| 项目 | 约束 |
|------|------|
| 状态数量 | 每种 2 种（待机、死亡） |
| 帧数 | 待机 1 帧，死亡 4 帧 |
| 输出格式 | 待机单张 PNG，死亡 2×2 网格精灵图 |
| 风格 | 像素风，粗像素（约 64×64 效果） |
| 身份 | 被污染的修士/妖兽 |

---

## 流程总览

```
Step 1: MJ 生成原图（每种 1 张）
  → Step 2: 转像素图
  → Step 3: 生成待机图（1 帧）
  → Step 4: 生成死亡帧（2×2 精灵图）
  → Step 5: 放入 assets
```

---

## Step 1：MJ 生成原图（每种 1 张）

**目标**：得到每种敌人的 1 张基础图，用于转像素和生成各状态。

**操作**：在 MJ 中 `/imagine` 后，先粘贴参考图 URL（主角图，用于保持风格一致），再粘贴下方对应敌人的完整提示词。

**主角参考图 URL**（每个敌人提示词前都要加）：
```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc&
```

---

### 近战敌人（melee）MJ 提示词

**身份**：被污染持剑修士

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A corrupted Chinese cultivator warrior, male, wearing tattered dark grey and black daoist robes with corruption marks, holding a sword, menacing stance, dark red and black corruption veins visible on clothing, disheveled hair, aggressive expression, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

---

### 远程敌人（ranged）MJ 提示词

**身份**：被污染持弓修士

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A corrupted Chinese cultivator archer, male or female, wearing tattered dark blue and grey robes with corruption marks, holding a bow or talisman, cautious stance, dark purple and black corruption veins visible on clothing, disheveled hair, focused expression, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

---

### 突进敌人（charge）MJ 提示词

**身份**：被污染妖兽

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A corrupted beast creature, quadruped or bipedal, muscular build, dark red and black fur or scales with corruption marks, sharp claws, aggressive charging pose, fierce expression, corruption energy visible on body, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

---

### 范围敌人（aoe）MJ 提示词

**身份**：被污染施法修士

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A corrupted Chinese cultivator mage, male or female, wearing tattered dark purple and black robes with corruption marks, holding a staff or talisman, casting pose with arms raised, corruption veins visible on clothing and hands, disheveled hair, intense expression, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

---

### 追踪敌人（homing）MJ 提示词

**身份**：秽妖/邪灵

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A corrupted spirit creature, semi-transparent ghostly form, dark purple and black wisps, elongated limbs, floating pose, eerie expression, corruption energy forming its body, ethereal and menacing, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

---

### 召唤敌人（summon）MJ 提示词

**身份**：召唤型邪妖

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A corrupted summoner creature, small demonic form, dark green and black body with corruption marks, holding summoning talisman or ritual object, mystical pose, corruption symbols visible, sinister expression, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

---

**验收**：全身、正面、居中、纯色背景、颜色饱满、无特效、与主角风格一致。

---

## Step 2：转像素图（每种 1 张）

**目标**：把 Step 1 的 MJ 原图转成像素风格，作为 Step 3/4 的参考图。

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

**验收**：主体清晰、像素风、透明背景、与主角风格一致。

---

## Step 3：生成待机图（1 帧）

**目标**：用参考图生成待机静态图。

**操作**：直接使用 Step 2 的像素图，无需再生成。重命名为对应文件名即可。

**验收**：单张 PNG、透明背景、像素风。

---

## Step 4：生成死亡帧（2×2 精灵图）

**目标**：用参考图 + 提示词，生成死亡 4 帧（倒地序列）。

**操作**：上传 Step 2 的像素图到 Nano Banana，粘贴下方提示词。

### 死亡帧提示词（完整，6 种敌人通用）

```
[Overall Format]
A 2D game sprite sheet layout, arranged in a 2×2 grid (4 distinct frames: top-left, top-right, bottom-left, bottom-right). Pure transparent background (PNG alpha channel). Pixel art style.

[Character Reference]
Use the provided reference image for the character design. Match the character's appearance, clothing, hair, and style exactly from the reference. Do not alter or redesign the character. CRITICAL: Preserve the pixel art style of the reference. No anti-aliasing, no smooth gradients, no high-resolution rendering. Keep crisp pixel edges and the same pixel density.

[Crucial: Frame-by-Frame Physical Description]
Each of the 4 frames MUST show the character in a DIFFERENT pose to create a collapse sequence. They must NOT be identical.
* Frame 1 (Top-left): Character standing upright, intact. Calm or aggressive pose, clothing/body hanging normally.
* Frame 2 (Top-right): Beginning to collapse. Body leaning backward or sideways. Arms starting to fall. Clothing and hair beginning to scatter.
* Frame 3 (Bottom-left): Mid-fall. Body tilting sharply. Clothing and hair disheveled, flying outward from the impact.
* Frame 4 (Bottom-right): Fully collapsed. Body on ground or dissipating. Clothing and hair fully scattered, corruption energy fading.

[Liveliness and Material Detail]
The fabric and hair (if any) must show progressive disruption in EVERY frame. For beast/spirit types, show body disintegration or fading. Pixel art style, crisp pixel edges, no anti-aliasing.
```

**验收**：2×2 网格、4 帧、PNG 透明背景、像素风、每帧有明显差异（站立→后仰→下落→倒地）。

---

## Step 5：放入 assets 与命名

| 文件名 | 敌人类型 |
|--------|----------|
| `assets/enemy_melee_idle.png` | 近战待机 |
| `assets/enemy_melee_death.png` | 近战死亡 |
| `assets/enemy_ranged_idle.png` | 远程待机 |
| `assets/enemy_ranged_death.png` | 远程死亡 |
| `assets/enemy_charge_idle.png` | 突进待机 |
| `assets/enemy_charge_death.png` | 突进死亡 |
| `assets/enemy_aoe_idle.png` | 范围待机 |
| `assets/enemy_aoe_death.png` | 范围死亡 |
| `assets/enemy_homing_idle.png` | 追踪待机 |
| `assets/enemy_homing_death.png` | 追踪死亡 |
| `assets/enemy_summon_idle.png` | 召唤待机 |
| `assets/enemy_summon_death.png` | 召唤死亡 |

**验收**：文件存在、透明背景、像素风。

---

## 制作顺序建议

1. **melee**（近战）— 最常见，先验证流程
2. **ranged**（远程）— 第二常见
3. **charge**（突进）— 妖王、秽源共用
4. 其余类型按需逐步补充

---

## 相关文档

| 文档 | 用途 |
|------|------|
| `docs/ENEMY_DESIGN.md` | 敌人类型与身份设定 |
| `docs/SPRITE_FRAME_PROMPT_TEMPLATE.md` | 通用模板结构 |
