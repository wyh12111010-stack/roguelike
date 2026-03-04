# Agent 快速上手指南

> 新 Agent 接手本项目时，优先阅读本文以快速建立上下文。

---

## 一、项目是什么

**修仙肉鸽**：俯视角动作 Roguelike，五行属性 + 法宝/饰品构筑。对标 Tiny Rogues（爽点、节奏、正负并存饰品）。

- **局内**：村子选灵根/法宝 → 战斗关 → 路线选择 → 商店/休息/事件 → 三章 Boss → 终局 Boss
- **局外**：道韵解锁灵根/法宝/饰品、伙伴羁绊、饰品槽/商店刷新/开局饰品等成长

---

## 二、目录与关键文件

```
f:\游戏\
├── main.py              # 入口，事件循环、设置、分辨率
├── game.py              # 主逻辑：场景切换、关卡加载、商店、存档（~700 行）
├── config.py            # 屏幕、战斗区、颜色、字体
├── setting.py           # 世界观、货币、道韵/灵石规则
│
├── player.py            # 玩家：移动、攻击、灵根/法宝、饰品、受击（~550 行）
├── enemy.py             # 敌人：6 类型 + 变体 + 4 Boss（~1835 行，最复杂）
├── projectile.py        # 投射物、近战挥砍、抛物线、FlameBeam、SlowZone、EarthWall
├── attribute.py         # 五行枚举、相合/反应
├── reaction_effects.py  # 五行反应效果（蒸发、感电、超载等）
├── attribute_effects.py # 基础属性效果（DOT、减速、虚弱）
│
├── fabao.py             # 法宝列表（7 把：arc/pierce/fan/heavy/parabolic）
├── accessory.py         # 饰品列表（含正负并存：碎心核、风债符、焚灵坠、镇岳甲）
├── linggen.py           # 灵根列表
├── shop.py              # 商店 UI、法宝强化、饰品购买、刷新
├── unlock.py            # 解锁配置、局外成长阶梯
│
├── levels.py            # 关卡加载、路线树
├── data/
│   ├── levels.json     # 关卡配置、敌群、Boss 配置
│   ├── demo.json       # 演示关卡
│   └── enemies.json    # 敌人类型颜色/标签
│
├── village.py           # 村子 UI、地图、NPC 区域
├── partner.py           # 伙伴配置、羁绊、解锁映射
├── partner_skills.py   # 伙伴充能技能
├── event_events.py      # 事件节点（灵泉、修士、商人等）
│
├── meta.py              # 局外数据（道韵、解锁、伙伴、成就）
├── save.py              # 存档持久化
├── spell_effects.py     # 法宝独有法术（烈焰冲击、水牢、藤蔓、剑气、土墙）
├── particles.py         # 粒子效果（五行、反应、Boss 读招）
├── fx_audio.py          # 合成音效（Boss/敌人读招、玩家普攻）
│
├── core/                # EventBus、GameState、SceneManager
├── nodes/               # 节点注册、combat/shop Handler
├── scenes/              # VillageScene、场景基类
├── systems/
│   ├── combat.py       # 战斗 update/draw、路线选择、过关结算
│   └── route.py        # 路线树、奖励权重、稀有奖励限 1
├── ui/                  # input_handler、CombatLogUI
│
└── tools/               # 回归与验证
    ├── smoke_test.py       # 核心模块 + Game 初始化
    ├── fairness_gate.py    # 读招窗口 >= 0.22s、Boss windup >= 0.3s
    ├── phase2_gate.py      # 经济/数值封板
    ├── balance_test.py     # DPS/TTK 模拟
    └── regression_gate.py  # 统一入口（quick/nightly/audit）
```

---

## 三、核心流程

```
main.py → Game
  scene: village | combat
  village: 选灵根、选法宝、解锁、外出
  combat: 关卡战斗 → 路线选择 → 商店/休息/事件 → 身陨/凯旋 → 回村
```

**战斗内**：`game.player.update` + `enemy.update` + `CombatSystem.update_combat`；投射物/AOE 在 `projectile`、`enemy` 中创建；`ctx` 含 `enemies`、`enemy_projectiles`、`aoe_zones`。

---

## 四、常见改动入口

| 要改什么 | 主要文件 |
|----------|----------|
| 敌人/ Boss 行为、技能、读招 | `enemy.py` |
| 关卡配置、敌群编组 | `data/levels.json` |
| 玩家攻击、法宝手感 | `player.py` |
| 法宝/饰品 | `fabao.py`、`accessory.py` |
| 商店、解锁、价格 | `shop.py`、`unlock.py` |
| 路线、奖励权重 | `systems/route.py` |
| 五行反应 | `attribute.py`、`reaction_effects.py` |
| 村子、伙伴 | `village.py`、`partner.py` |

---

## 五、硬约束（必须遵守）

1. **读招窗口**：所有危险结算 >= 0.22s（`MIN_TELEGRAPH_WINDOW`、`MIN_BOSS_PREVIEW_WINDOW`）
2. **Boss 技能前摇**：>= 0.3s（由 `fairness_gate` 校验）
3. **主角移速**：始终高于敌人（`PLAYER_BASE_SPEED` > `ENEMY_MAX_SPEED`）
4. **法宝强化上限**：伤害 +50%、攻速 +25%（`shop.FABAO_UPGRADE_RULES`）
5. **奖励稀有度**：同一批次选路最多 1 个法宝/道韵（`route.assign_combat_rewards_for_options`）

详见 `docs/COMBAT_DESIGN.md`。

---

## 六、验证命令

```bash
# 快速回归（开发中）
python -m tools.regression_gate --preset quick

# 全量回归（收工前）
python -m tools.regression_gate --preset nightly

# 封板审计（含经济快照、gate 历史）
python -m tools.regression_gate --preset audit

# 仅烟测
python -m tools.smoke_test

# 平衡测试（指定关卡）
python -m tools.balance_test --runs 5 --level 10
```

详见 `docs/GATE_QUICK_CARD.md`、`docs/REGRESSION_GATE.md`。

---

## 七、设计原则（对标 Tiny Rogues）

- **爽点优先**：高频小反馈、低门槛决策、稳定节奏
- **正负并存**：饰品可有代价，代价可被特定流派转化
- **无流派羁绊**：不做套装/羁绊，自由搭配
- **无软引导**：饰品描述纯数值，不写「适合 XX 流」

---

## 八、延伸阅读

- `docs/CODEBASE_OVERVIEW.md` - 代码库概览
- `docs/TECH_ARCHITECTURE.md` - 技术架构
- `docs/BOSS_DESIGN.md` - Boss 设计
- `docs/PROJECT_ROADMAP.md` - 路线图
