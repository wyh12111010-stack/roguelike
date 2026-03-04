# 角色美术制作索引

> 所有角色美术流程的快速导航

---

## 📋 总览

| 角色类型 | 数量 | 状态 | 文档 |
|----------|------|------|------|
| **主角** | 1 | 待机（4 帧）+ 死亡（4 帧） | [CHARACTER_ART_PLAYER.md](CHARACTER_ART_PLAYER.md) |
| **伙伴** | 5 | 站立呼吸（4 帧） | [CHARACTER_ART_PARTNERS.md](CHARACTER_ART_PARTNERS.md) |
| **敌人** | 6 | 待机（1 帧）+ 死亡（4 帧） | [CHARACTER_ART_ENEMIES.md](CHARACTER_ART_ENEMIES.md) |
| **Boss** | 4 | 待机（1 帧）+ 死亡（4 帧） | [CHARACTER_ART_BOSSES.md](CHARACTER_ART_BOSSES.md) |
| **合计** | 16 | 主角 8 帧 + 伙伴 20 帧 + 敌人 30 帧 + Boss 20 帧 = **78 帧** | - |

---

## 🎯 统一流程

所有角色遵循相同流程：

```
Step 1: MJ 生成原图（含参考图 URL）
  ↓
Step 2: Nano Banana 转像素图
  ↓
Step 3: Nano Banana 生成各状态帧（2×2 精灵图）
  ↓
Step 4: 预览与对齐（tools/sprite_preview.py）
  ↓
Step 5: 放入 assets 目录
```

---

## 📚 详细文档

### 1. 主角（1 位）

**文档**：[CHARACTER_ART_PLAYER.md](CHARACTER_ART_PLAYER.md)

**角色**：
- 男性修士（主角）

**状态**：
- 待机：4 帧悬浮 bobbing
- 死亡：4 帧倒地序列

**输出文件**：
- `assets/player_idle.png`
- `assets/player_death.png`

---

### 2. 伙伴（5 位）

**文档**：[CHARACTER_ART_PARTNERS.md](CHARACTER_ART_PARTNERS.md)

**角色**：
- 玄霄（雷宗掌门）
- 青璃（青丘狐族长老）
- 赤渊（散修剑尊）
- 碧落（丹道宗师）
- 墨羽（影宗宗主）

**状态**：
- 站立呼吸：4 帧轻微呼吸循环

**输出文件**：
- `assets/partner_xuanxiao.png`
- `assets/partner_qingli.png`
- `assets/partner_chiyuan.png`
- `assets/partner_biluo.png`
- `assets/partner_moyu.png`

---

### 3. 敌人（6 种）

**文档**：[CHARACTER_ART_ENEMIES.md](CHARACTER_ART_ENEMIES.md)

**类型**：
- melee（近战）：被污染持剑修士
- ranged（远程）：被污染持弓修士
- charge（突进）：被污染妖兽
- aoe（范围）：被污染施法修士
- homing（追踪）：秽妖/邪灵
- summon（召唤）：召唤型邪妖

**状态**：
- 待机：1 帧静态
- 死亡：4 帧倒地序列

**输出文件**：
- `assets/enemy_melee_idle.png` / `enemy_melee_death.png`
- `assets/enemy_ranged_idle.png` / `enemy_ranged_death.png`
- `assets/enemy_charge_idle.png` / `enemy_charge_death.png`
- `assets/enemy_aoe_idle.png` / `enemy_aoe_death.png`
- `assets/enemy_homing_idle.png` / `enemy_homing_death.png`
- `assets/enemy_summon_idle.png` / `enemy_summon_death.png`

---

### 4. Boss（4 个）

**文档**：[CHARACTER_ART_BOSSES.md](CHARACTER_ART_BOSSES.md)

**Boss**：
- 妖王（segment_boss_1）：被污染妖兽王者（虎形），火属性
- 剑魔（segment_boss_2）：被污染剑修
- 丹魔（segment_boss_3）：被污染丹修/毒修
- 秽源（final_boss）：污染源本体

**状态**：
- 待机：1 帧静态
- 死亡：4 帧倒地序列

**输出文件**：
- `assets/boss_yaowang_idle.png` / `boss_yaowang_death.png`
- `assets/boss_jianmo_idle.png` / `boss_jianmo_death.png`
- `assets/boss_danmo_idle.png` / `boss_danmo_death.png`
- `assets/boss_huiyuan_idle.png` / `boss_huiyuan_death.png`

---

## 🎨 风格统一

### MJ 参考图 URL（所有角色通用）

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc&
```

### MJ 参数（所有角色通用）

```
--ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

### 转像素提示词（所有角色通用）

见各文档 Step 2，使用粗像素风格（约 64×64 效果）。

---

## 🛠️ 工具与脚本

| 工具 | 用途 | 命令 |
|------|------|------|
| **预览工具** | 预览精灵图动画 | `python tools/sprite_preview.py` |
| **对齐工具** | 对齐各帧质心 | `python tools/align_sprites.py nanobanana_in/` |
| **批量对齐** | 批量对齐所有精灵图 | 双击 `align_all_sprites.bat` |

---

## 📝 制作顺序建议

### 阶段 1：核心角色（优先）

1. **主角**（必须）
2. **melee 敌人**（最常见）
3. **ranged 敌人**（第二常见）

### 阶段 2：Boss 与伙伴

4. **妖王 Boss**（首个 Boss）
5. **玄霄伙伴**（首个伙伴）

### 阶段 3：补充敌人

6. **charge 敌人**（妖王、秽源共用）
7. **aoe 敌人**
8. **homing 敌人**
9. **summon 敌人**

### 阶段 4：剩余 Boss 与伙伴

10. **剑魔 Boss**
11. **丹魔 Boss**
12. **秽源 Boss**
13. **青璃、赤渊、碧落、墨羽伙伴**

---

## 📊 进度追踪

### 主角（1/1）

- [ ] 主角待机
- [ ] 主角死亡

### 伙伴（0/5）

- [ ] 玄霄
- [ ] 青璃
- [ ] 赤渊
- [ ] 碧落
- [ ] 墨羽

### 敌人（0/6）

- [ ] melee（近战）
- [ ] ranged（远程）
- [ ] charge（突进）
- [ ] aoe（范围）
- [ ] homing（追踪）
- [ ] summon（召唤）

### Boss（0/4）

- [ ] 妖王
- [ ] 剑魔
- [ ] 丹魔
- [ ] 秽源

---

## 🔗 相关文档

| 文档 | 用途 |
|------|------|
| [SPRITE_FRAME_PROMPT_TEMPLATE.md](SPRITE_FRAME_PROMPT_TEMPLATE.md) | 通用模板结构 |
| [NANOBANANA_PROMPTS.md](NANOBANANA_PROMPTS.md) | 完整提示词与参数说明 |
| [SPRITE_ALIGNMENT_GUIDE.md](SPRITE_ALIGNMENT_GUIDE.md) | 质心对齐指南 |
| [PARTNER_VILLAGER_INITIAL.md](PARTNER_VILLAGER_INITIAL.md) | 伙伴身份与设定 |
| [ENEMY_DESIGN.md](ENEMY_DESIGN.md) | 敌人类型与身份设定 |
| [BOSS_DESIGN.md](BOSS_DESIGN.md) | Boss 身份与战斗设计 |

---

## 🚀 快速开始

### 1. 制作主角

```bash
# 打开文档
docs/CHARACTER_ART_PLAYER.md

# 按步骤执行：
# Step 1: MJ 生成原图
# Step 2: Nano Banana 转像素
# Step 3: Nano Banana 生成待机帧
# Step 4: Nano Banana 生成死亡帧
# Step 5: 预览与接入游戏
```

### 2. 制作伙伴

```bash
# 打开文档
docs/CHARACTER_ART_PARTNERS.md

# 按步骤执行（每位伙伴重复）：
# Step 1: MJ 生成原图
# Step 2: Nano Banana 转像素
# Step 3: Nano Banana 生成站立呼吸帧
# Step 4: 放入 assets
```

### 3. 制作敌人

```bash
# 打开文档
docs/CHARACTER_ART_ENEMIES.md

# 按步骤执行（每种敌人重复）：
# Step 1: MJ 生成原图
# Step 2: Nano Banana 转像素
# Step 3: 生成待机图（直接用像素图）
# Step 4: Nano Banana 生成死亡帧
# Step 5: 放入 assets
```

### 4. 制作 Boss

```bash
# 打开文档
docs/CHARACTER_ART_BOSSES.md

# 按步骤执行（每个 Boss 重复）：
# Step 1: MJ 生成原图
# Step 2: Nano Banana 转像素
# Step 3: 生成待机图（直接用像素图）
# Step 4: Nano Banana 生成死亡帧
# Step 5: 放入 assets
```

---

**现在请从主角开始，按照 [CHARACTER_ART_PLAYER.md](CHARACTER_ART_PLAYER.md) 制作！** 😊
