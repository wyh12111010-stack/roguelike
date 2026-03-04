# 所有角色提示词（最终简化版）

> 全部用 Nano Banana 生成。直接生成粗像素，所有角色 32-48px 高度，8-bit 风格。

---

## 📋 规格统一

- **主角/NPC/伙伴**：32-48 像素高度
- **敌人**：28-40 像素高度
- **Boss**：48-64 像素高度
- **像素块**：5-8 像素/块（超粗）
- **风格**：8-bit NES/Game Boy
- **背景**：透明 PNG
- **工具**：全部用 Nano Banana

---

## 📊 角色总览

| 类型 | 数量 | 美术需求 |
|------|------|----------|
| **主角** | 1 | 1 张静态图 |
| **NPC** | 3 | 待机动画（32 帧推荐） |
| **伙伴** | 5 | 待机动画（32 帧推荐） |
| **敌人** | 6 | 1 张立绘 |
| **Boss** | 4 | 1 张立绘 |
| **合计** | **19** | **19 张图** |

**说明**：
- 主角/敌人/Boss：只需 1 张静态图
- NPC/伙伴：需要待机动画（推荐 32 帧更流畅）
- 所有受击/死亡效果用程序化实现

---

## 🎯 主角（男性修士）

**静态图（单张）：**
```
A young Chinese male cultivator. 8-bit pixel art style. EXTREMELY LOW RESOLUTION. 32-48 pixels total height. Very chunky blocky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Light blue and white robes. Black hair topknot. Standing pose. Full body, facing front, centered. Transparent background. NES/Game Boy aesthetic. No anti-aliasing, no gradients, no smooth edges.
```

**效果**：
- 受击：抖动（程序化）
- 死亡：粒子消失（程序化）

---

## 👤 NPC（3 位）

### 栖霞（村中守护者）
**待机动画（32 帧推荐）：**

**静态图：**
```
A mysterious Chinese guardian figure. 8-bit pixel art. 32-48 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Ethereal white and light blue robes. Long flowing hair. Serene expression. Standing pose. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

**视频提示词：** `Subtle breathing motion, standing still, pixel art style`

---

### 玄真（灵根殿主）
**待机动画（32 帧推荐）：**

**静态图：**
```
An elderly Chinese cultivator master, spiritual root hall master. 8-bit pixel art. 32-48 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Sage green and white robes. Long white beard. Wise expression. Standing pose. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

**视频提示词：** `Subtle breathing motion, standing still, pixel art style`

---

### 铸心（炼器宗师）
**待机动画（32 帧推荐）：**

**静态图：**
```
A sturdy Chinese blacksmith master, weapon forging expert. 8-bit pixel art. 32-48 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Dark brown and grey robes with leather apron. Short hair. Strong build. Standing pose. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

**视频提示词：** `Subtle breathing motion, standing still, pixel art style`

---

## 👥 伙伴（5 位）

### 玄霄（雷宗掌门）
**待机动画（32 帧推荐）：**

**静态图：**
```
A mature Chinese male cultivator, sect leader, dignified. 8-bit pixel art. 32-48 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Dark blue and silver robes with thunder motifs. Black hair topknot. Standing pose. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

**视频提示词：** `Subtle breathing motion, standing still, pixel art style`

---

### 青璃（青丘狐族长老）
**待机动画（32 帧推荐）：**

**静态图：**
```
An elegant Chinese fox spirit elder, female. 8-bit pixel art. 32-48 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Green and jade robes. Fox ears visible. Long dark hair. Standing pose. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

**视频提示词：** `Subtle breathing motion, standing still, pixel art style`

---

### 赤渊（散修剑尊）
**待机动画（32 帧推荐）：**

**静态图：**
```
A weathered Chinese male swordsman, lone cultivator. 8-bit pixel art. 32-48 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Dark red and brown robes. Sword sheathed at side. Short beard. Standing pose. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

**视频提示词：** `Subtle breathing motion, standing still, pixel art style`

---

### 碧落（丹道宗师）
**待机动画（32 帧推荐）：**

**静态图：**
```
A gentle Chinese female alchemist. 8-bit pixel art. 32-48 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Soft blue and white robes. Hair in simple bun. Standing pose. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

**视频提示词：** `Subtle breathing motion, standing still, pixel art style`

---

### 墨羽（影宗宗主）
**待机动画（32 帧推荐）：**

**静态图：**
```
A mysterious Chinese male in dark grey and black robes, shadow sect master. 8-bit pixel art. 32-48 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Hood or cloak. Face partially obscured. Standing pose. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

**视频提示词：** `Subtle breathing motion, standing still, pixel art style`

---

## 👹 敌人（6 种）

### 近战（melee）
**立绘（单张）：**
```
A corrupted Chinese cultivator warrior. 8-bit pixel art. 28-40 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Tattered dark grey and black robes with corruption marks. Holding sword. Aggressive stance. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

---

### 远程（ranged）
**立绘（单张）：**
```
A corrupted Chinese cultivator archer. 8-bit pixel art. 28-40 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Tattered dark blue and grey robes with corruption marks. Holding bow or talisman. Cautious stance. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

---

### 突进（charge）
**立绘（单张）：**
```
A corrupted beast creature. 8-bit pixel art. 28-40 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Dark red and black fur with corruption marks. Sharp claws. Quadruped or bipedal. Aggressive charging pose. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

---

### 范围（aoe）
**立绘（单张）：**
```
A corrupted Chinese cultivator mage. 8-bit pixel art. 28-40 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Tattered dark purple and black robes with corruption marks. Holding staff or talisman. Casting pose with arms raised. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

---

### 追踪（homing）
**立绘（单张）：**
```
A corrupted spirit creature. 8-bit pixel art. 28-40 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Dark purple and black wisps. Semi-transparent ghostly form. Elongated limbs. Floating pose. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

---

### 召唤（summon）
**立绘（单张）：**
```
A corrupted summoner creature. 8-bit pixel art. 28-40 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Dark green and black body with corruption marks. Small demonic form. Holding summoning talisman. Mystical pose. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

**所有敌人效果**：
- 移动：直接平移立绘
- 受击：抖动（程序化）
- 死亡：粒子消失（程序化）

---

## 👑 Boss（4 个）

### 妖王（segment_boss_1）
**立绘（单张）：**
```
A corrupted tiger beast king. 8-bit pixel art. 48-64 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Massive muscular quadruped. Dark red and black fur with corruption marks and fire motifs. Sharp fangs and claws. Fierce aggressive stance. Imposing presence. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

---

### 剑魔（segment_boss_2）
**立绘（单张）：**
```
A corrupted sword master. 8-bit pixel art. 48-64 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Tattered dark grey and crimson robes with corruption marks. Holding large corrupted sword. Menacing battle stance. Imposing presence. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

---

### 丹魔（segment_boss_3）
**立绘（单张）：**
```
A corrupted alchemist master. 8-bit pixel art. 48-64 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Tattered dark purple and green robes with corruption marks and poison motifs. Holding corrupted pill or vial. Casting pose with one hand raised. Imposing presence. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

---

### 秽源（final_boss）
**立绘（单张）：**
```
A corrupted source entity. 8-bit pixel art. 48-64 pixels height. Very chunky pixels, 5-8 pixels per block. Minimal detail, simple shapes. Massive imposing figure. Dark purple and black body with corruption energy forming its essence. Humanoid or semi-humanoid form. Menacing stance. Ultimate evil presence. Full body, facing front, centered. Transparent background. NES style. No anti-aliasing, no gradients.
```

**所有 Boss 效果**：
- 移动：直接平移立绘
- 受击：抖动（程序化）
- 死亡：粒子消失（程序化）

---

## 📝 制作流程

### NPC/伙伴（需要动画）

```
Step 1: Nano Banana 生成静态图
  ↓
Step 2: 上传到视频工具（Runway / Pika / Kling AI）
  ↓
Step 3: 用视频提示词生成 32 帧动画
  ↓
Step 4: 提取 32 帧，拼成 6×6 网格（前 32 格）
  ↓
Step 5: 去背景 → 放入 assets
```

### 主角/敌人/Boss（只需静态图）

```
Step 1: Nano Banana 生成静态图
  ↓
Step 2: 去背景
  ↓
Step 3: 放入 assets
```

---

## 📊 制作清单

- **主角**：1 张静态图
- **NPC**：3 个待机动画（32 帧）
- **伙伴**：5 个待机动画（32 帧）
- **敌人**：6 张立绘
- **Boss**：4 张立绘
- **合计**：**19 张图**

**程序化效果**（无需美术）：
- ✅ 受击：抖动效果
- ✅ 死亡：粒子消失效果
- ✅ 移动：平移（敌人/Boss）

**优势**：
- 制作量极少（19 张图）
- 符合像素 Roguelike 惯例
- 性能最优

---

**现在可以开始制作了！建议从主角开始测试流程。** 😊
;/怕[-怕很难避免Hilo.怕vbghnmujik,o9lk8ujhyngbfv从v方便给你会遇见米宽改还要给他补发v调查小厨房v不过他还有奴家一会给他人妇v底层实现csdfvergbt5hy6tr4fed3wsazxDCSXEFR4T53EW2SQAz按顺序对策无法让袜子A是星期五2` zAquarium`1