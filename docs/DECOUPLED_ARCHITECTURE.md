# 🏗️ 解耦架构设计 - 避免改动导致崩溃

## 🎯 核心原则

### 1. 可选依赖（Optional Dependencies）
新功能应该是**可选的**，不应该影响核心功能。

### 2. 优雅降级（Graceful Degradation）
如果某个模块加载失败，游戏应该继续运行，只是没有那个功能。

### 3. 延迟加载（Lazy Loading）
只在需要时才加载模块，而不是在初始化时全部加载。

---

## 🔧 改进方案

### 当前问题
```python
# game.py - 当前的做法（不好）
from damage_text import init_damage_text_manager
self.damage_text_mgr = init_damage_text_manager()  # 如果失败，游戏崩溃
```

### 改进后
```python
# game.py - 改进的做法（好）
try:
    from damage_text import init_damage_text_manager
    self.damage_text_mgr = init_damage_text_manager()
except Exception as e:
    print(f"警告：伤害飘字系统加载失败: {e}")
    self.damage_text_mgr = None  # 优雅降级
```

---

## 📦 模块化设计

### 核心模块（必须）
- game.py
- player.py
- enemy.py
- config.py
- main.py

### 可选模块（增强功能）
- damage_text.py - 伤害飘字
- screen_shake.py - 屏幕震动
- enhanced_particles.py - 增强粒子
- audio_system.py - 音频系统
- tutorial.py - 新手教程
- help_system.py - 帮助系统

---

## 🛡️ 安全加载模式

### 模式1：Try-Except包装
```python
def safe_import(module_name, class_name=None):
    """安全导入模块"""
    try:
        module = __import__(module_name)
        if class_name:
            return getattr(module, class_name)
        return module
    except Exception as e:
        print(f"警告：{module_name} 加载失败: {e}")
        return None
```

### 模式2：功能开关
```python
# config.py
ENABLE_DAMAGE_TEXT = True
ENABLE_SCREEN_SHAKE = True
ENABLE_ENHANCED_PARTICLES = True
ENABLE_AUDIO = True
ENABLE_TUTORIAL = True
```

### 模式3：空对象模式（Null Object Pattern）
```python
class NullDamageText:
    """空对象，提供相同接口但不做任何事"""
    def show_damage(self, *args, **kwargs):
        pass
    
    def update(self, dt):
        pass
    
    def draw(self, screen):
        pass

# 使用
if damage_text_mgr is None:
    damage_text_mgr = NullDamageText()
```

---

## 🔨 实际实现

### 创建一个安全的模块加载器

```python
# utils/safe_loader.py

class SafeModuleLoader:
    """安全的模块加载器"""
    
    @staticmethod
    def load_optional_system(module_name, init_func_name, fallback=None):
        """
        安全加载可选系统
        
        Args:
            module_name: 模块名
            init_func_name: 初始化函数名
            fallback: 失败时的回退对象
        
        Returns:
            初始化的对象或fallback
        """
        try:
            module = __import__(module_name)
            init_func = getattr(module, init_func_name)
            return init_func()
        except Exception as e:
            print(f"⚠️  {module_name} 加载失败: {e}")
            print(f"   游戏将继续运行，但没有此功能")
            return fallback
```

### 在game.py中使用

```python
# game.py

from utils.safe_loader import SafeModuleLoader

class Game:
    def __init__(self, screen):
        self.screen = screen
        
        # 核心系统（必须）
        self.scene = "village"
        self.combat_log = CombatLogUI()
        
        # 可选系统（安全加载）
        self.damage_text_mgr = SafeModuleLoader.load_optional_system(
            'damage_text', 
            'init_damage_text_manager',
            fallback=None
        )
        
        self.screen_shake = SafeModuleLoader.load_optional_system(
            'screen_shake',
            'init_screen_shake',
            fallback=None
        )
        
        self.audio = SafeModuleLoader.load_optional_system(
            'audio_system',
            'init_audio',
            fallback=None
        )
        
        # ... 其他初始化
```

### 在使用时检查

```python
# 使用伤害飘字
if self.damage_text_mgr:
    self.damage_text_mgr.show_damage(x, y, damage)

# 使用屏幕震动
if self.screen_shake:
    self.screen_shake.add_shake(0.2, 10)

# 使用音频
if self.audio:
    self.audio.play_sfx("attack")
```

---

## 🎯 好处

### 1. 稳定性
- 某个模块出错不会导致整个游戏崩溃
- 可以逐步添加功能

### 2. 可维护性
- 每个模块独立
- 修改一个模块不影响其他

### 3. 可测试性
- 可以单独测试每个模块
- 可以禁用某些功能进行测试

### 4. 灵活性
- 可以通过配置开关功能
- 可以动态加载/卸载模块

---

## 📝 实施计划

### 第1步：创建安全加载器
创建 `utils/safe_loader.py`

### 第2步：修改game.py
使用安全加载器加载所有可选系统

### 第3步：添加空对象
为每个可选系统创建空对象实现

### 第4步：添加配置开关
在config.py中添加功能开关

### 第5步：测试
确保禁用任何功能都不会崩溃

---

## 🚀 立即实施

我现在就创建这个安全加载系统！
