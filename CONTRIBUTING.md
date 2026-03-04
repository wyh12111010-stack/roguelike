# 贡献指南

感谢你对修仙肉鸽项目的关注！本文档将帮助你快速参与项目开发。

---

## 开发环境设置

### 1. 克隆项目

```bash
git clone <repository-url>
cd 修仙肉鸽
```

### 2. 安装依赖

```bash
# 运行时依赖
pip install -r requirements.txt

# 开发依赖（打包工具）
pip install -r requirements-dev.txt
```

### 3. 运行游戏

```bash
python main.py
```

---

## 开发流程

### 分支策略

- `main` - 主分支，稳定版本
- `develop` - 开发分支，最新功能
- `feature/*` - 功能分支
- `bugfix/*` - 修复分支

### 提交规范

使用语义化提交信息：

```
<类型>: <简短描述>

<详细描述>（可选）
```

**类型**：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**：
```
feat: 新增火属性法宝「烈焰鞭」

- 攻速 0.25s，伤害 10
- 攻击形态为弧线挥砍
- 法术为火焰冲击波
```

---

## 代码规范

### Python 风格

- 遵循 PEP 8
- 使用 4 空格缩进
- 函数和变量使用 snake_case
- 类使用 PascalCase
- 常量使用 UPPER_CASE

### 文档字符串

```python
def create_enemy(enemy_type, pos, health=25):
    """
    创建敌人实例
    
    Args:
        enemy_type: 敌人类型（melee/ranged/charge 等）
        pos: 位置元组 (x, y)
        health: 生命值，默认 25
    
    Returns:
        Enemy: 敌人实例
    """
    pass
```

### 注释规范

- 复杂逻辑必须注释
- 魔法数字必须解释
- TODO/FIXME 标记待办事项

```python
# TODO: 优化敌人寻路算法
# FIXME: 修复 Boss 技能冷却问题
```

---

## 测试

### 运行测试

```bash
# 冒烟测试
python -m tools.smoke_test

# 数值平衡测试
python -m tools.balance_test --runs 10

# 快速验收（运行所有检查）
python quick_check.py
```

### 添加测试

在 `tests/` 目录下添加测试文件：

```python
# tests/test_attribute.py
import unittest
from attribute import Attr, get_reaction_for_hit

class TestAttribute(unittest.TestCase):
    def test_fire_vs_metal(self):
        reaction = get_reaction_for_hit(Attr.FIRE, Attr.METAL)
        self.assertEqual(reaction.id, "huo_jin")
```

---

## 添加新内容

### 添加新法宝

1. 在 `fabao.py` 的 `FABAO_LIST` 中添加：

```python
Fabao("whip", "流光鞭", Attr.FIRE, True, 10, 0.25, 70, 0, ATTACK_ARC, "flame_wave", 12, 5.0)
```

2. 在 `unlock.py` 中配置解锁条件（如需要）

3. 更新 `docs/FABAO_ACCESSORY_DESIGN.md`

### 添加新饰品

1. 在 `accessory.py` 的 `ACCESSORY_LIST` 中添加：

```python
Accessory("fire_core", "烈焰之心", "火属性伤害+18%", 30, 3, fire_damage_pct=18)
```

2. 如果有特殊效果，在 `player.py` 中实现逻辑

3. 更新文档

### 添加新敌人类型

1. 在 `enemy.py` 中添加新类型逻辑
2. 在 `data/enemies.json` 中配置数据
3. 在 `data/levels.json` 中使用
4. 更新 `docs/ENEMY_DESIGN.md`

### 添加新成就

1. 在 `achievement.py` 的 `ACHIEVEMENTS` 中添加：

```python
Achievement("first_boss", "初战告捷", "首次击败 Boss", 5)
```

2. 在相应位置调用 `unlock_achievement()`

3. 更新 `docs/ACHIEVEMENT_TODO.md`

---

## 文档更新

### 设计文档

修改游戏设计时，同步更新 `docs/` 下的相关文档：

- 新增系统 → 创建新文档
- 修改机制 → 更新对应文档
- 重大变更 → 更新 `PROJECT_ROADMAP.md`

### 用户文档

修改玩法时，更新 `docs/USER_GUIDE.md`

---

## 发布流程

### 1. 更新版本号

编辑 `VERSION` 文件：

```
1.0.0
```

### 2. 更新 CHANGELOG

在 `CHANGELOG.md` 中记录变更：

```markdown
## [1.0.0] - 2026-03-01

### 新增
- 新增 10 个法宝
- 新增 20 个饰品

### 修复
- 修复 Boss 技能冷却问题
```

### 3. 打包

```bash
python build.py
```

### 4. 测试

运行完整测试：

```bash
python quick_check.py
```

手动游玩 3-5 局，确保无阻塞性 BUG

### 5. 发布

- 创建 Git tag
- 上传发布包
- 更新 README

---

## 常见问题

### Q: 如何调试？

使用 Python 调试器：

```python
import pdb; pdb.set_trace()
```

或使用 IDE 的调试功能。

### Q: 如何查看日志？

游戏运行时会输出日志到控制台。

### Q: 如何添加新的配置项？

1. 在 `config.py` 中添加常量
2. 在 `setting.py` 中添加游戏设定
3. 在代码中使用

### Q: 如何修改数值？

1. 修改 `config.py` 或 `setting.py` 中的常量
2. 或修改 `data/*.json` 中的配置
3. 运行 `python -m tools.balance_test` 验证
4. 运行 `python -m tools.phase2_gate` 检查是否通过验收

---

## 获取帮助

- 查看 `docs/` 目录下的设计文档
- 查看 `docs/CODEBASE_OVERVIEW.md` 了解代码结构
- 提交 Issue 描述问题
- 加入开发讨论

---

## 行为准则

- 尊重他人
- 建设性反馈
- 保持友善和专业

---

感谢你的贡献！




