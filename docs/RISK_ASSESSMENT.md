# 架构风险评估报告

> 检查时间：2024-03-03
> 状态：进行中

---

## ✅ 已检查项目

### 1. 模块依赖关系 ✅
**状态**：正常
**发现**：
- 核心模块依赖清晰
- 无循环依赖
- 导入顺序合理

**已修复**：
- ✅ `village.py` 中 `NPC_ROOMS` 定义顺序问题

---

### 2. 异常处理 ⚠️
**状态**：需要改进
**发现**：
- 大部分资源加载有 try-except
- 部分数学运算缺少保护

**需要修复的风险点**：

#### 风险 2.1：除零错误
```python
# player.py - 可能的除零
scale = target_h / fh if fh > 0 else 1  # ✅ 已有保护

# enemy.py - 需要检查
scale = target_h / fh if fh > 0 else 1  # 需要确认
```

#### 风险 2.2：空列表访问
```python
# player.py
if not self.fabao_list:  # ✅ 已有检查
    return None
```

---

### 3. 边界情况 ⚠️
**状态**：需要改进

#### 风险 3.1：血量/蓝量边界
```python
# player.py
self.health = max(0, self.health - amount)  # ✅ 已有保护
self.mana = max(0, self.mana - cost)  # 需要确认
```

#### 风险 3.2：索引越界
```python
# player.py
idx = play_animation(frames, anim_timer, fps=8)  # 需要确认返回值范围
```

---

### 4. 资源加载 ⚠️
**状态**：需要改进

#### 风险 4.1：图片加载失败
```python
# player.py
def _load_player_sprites():
    try:
        img = pygame.image.load(PLAYER_IDLE_PATH).convert_alpha()
        # ✅ 有 try-except
    except Exception as e:
        print(f"加载主角精灵图失败: {e}")
    return None  # ✅ 有回退
```

#### 风险 4.2：字体加载失败
```python
# config.py
def get_font(size):
    return pygame.font.SysFont("Microsoft YaHei", size)
    # ❌ 无异常处理，如果字体不存在会崩溃
```

---

### 5. 数据一致性 ⚠️
**状态**：需要检查

#### 风险 5.1：状态同步
- 需要检查 `_last_health` 是否总是同步
- 需要检查 `_flash_timer` 是否正确更新

#### 风险 5.2：存档数据
- 需要检查存档加载时的数据验证

---

### 6. 性能风险 ⚠️
**状态**：需要检查

#### 风险 6.1：缓存未清理
```python
# village.py
_PARTNER_SPRITES = {}  # 全局缓存
_NPC_SPRITES = {}  # 全局缓存
# ❌ 无清理机制，可能导致内存泄漏
```

#### 风险 6.2：频繁加载
```python
# enemy.py
def _load_enemy_sprite(enemy_type):
    if enemy_type in _ENEMY_SPRITES:
        return _ENEMY_SPRITES[enemy_type]  # ✅ 有缓存
```

---

## 🔥 高优先级风险（需要立即修复）

### P0 - 致命风险

#### 1. 字体加载无保护 ⭐⭐⭐⭐⭐
**位置**：`config.py:get_font()`
**风险**：如果系统没有"Microsoft YaHei"字体，游戏崩溃
**修复**：
```python
def get_font(size):
    try:
        return pygame.font.SysFont("Microsoft YaHei", size)
    except:
        return pygame.font.Font(None, size)  # 回退到默认字体
```

#### 2. 动画索引越界 ⭐⭐⭐⭐
**位置**：`player.py:draw()`, `village.py:draw_village()`
**风险**：如果 `play_animation` 返回超出范围的索引
**修复**：
```python
idx = play_animation(frames, anim_timer, fps=8)
idx = min(idx, len(frames) - 1)  # 确保不越界
```

#### 3. 空帧列表 ⭐⭐⭐⭐
**位置**：`player.py:draw()`, `village.py`
**风险**：如果 `frames` 为空列表
**修复**：
```python
if spr and spr["frames"] and len(spr["frames"]) > 0:
    # 使用帧
```

---

### P1 - 重要风险

#### 4. 缓存无清理 ⭐⭐⭐
**位置**：`village.py`, `enemy.py`
**风险**：长时间运行可能内存泄漏
**修复**：
```python
def clear_sprite_cache():
    global _PARTNER_SPRITES, _NPC_SPRITES, _ENEMY_SPRITES
    _PARTNER_SPRITES.clear()
    _NPC_SPRITES.clear()
    _ENEMY_SPRITES.clear()
```

#### 5. 除零保护不完整 ⭐⭐⭐
**位置**：多处
**风险**：某些计算可能除零
**修复**：统一检查所有除法运算

---

### P2 - 一般风险

#### 6. 错误日志不完整 ⭐⭐
**位置**：多处
**风险**：调试困难
**修复**：添加更详细的错误信息

---

## 🚀 修复计划

### 立即修复（30 分钟）
1. ✅ 字体加载保护
2. ✅ 动画索引保护
3. ✅ 空帧列表保护

### 短期修复（1 小时）
4. 缓存清理机制
5. 除零保护完善
6. 错误日志增强

### 长期优化（2-3 小时）
7. 单元测试
8. 压力测试
9. 性能优化

---

## 📊 风险评分

| 类别 | 风险等级 | 数量 | 状态 |
|------|----------|------|------|
| 致命风险 | P0 | 3 | 🔄 修复中 |
| 重要风险 | P1 | 2 | ⏸️ 待修复 |
| 一般风险 | P2 | 1 | ⏸️ 待修复 |
| **总计** | | **6** | |

---

**下一步：立即修复 P0 致命风险** 🔥
