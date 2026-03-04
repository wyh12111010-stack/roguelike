"""
安全模块加载器
确保可选模块加载失败时游戏不会崩溃
"""


class SafeModuleLoader:
    """安全的模块加载器"""
    
    @staticmethod
    def load_optional_system(module_name, init_func_name, fallback=None, silent=False):
        """
        安全加载可选系统
        
        Args:
            module_name: 模块名
            init_func_name: 初始化函数名
            fallback: 失败时的回退对象
            silent: 是否静默失败（不打印警告）
        
        Returns:
            初始化的对象或fallback
        """
        try:
            module = __import__(module_name)
            init_func = getattr(module, init_func_name)
            result = init_func()
            if not silent:
                print(f"✅ {module_name} 加载成功")
            return result
        except Exception as e:
            if not silent:
                print(f"⚠️  {module_name} 加载失败: {e}")
                print(f"   游戏将继续运行，但没有此功能")
            return fallback
    
    @staticmethod
    def safe_call(obj, method_name, *args, **kwargs):
        """
        安全调用对象方法
        
        Args:
            obj: 对象（可能为None）
            method_name: 方法名
            *args, **kwargs: 方法参数
        
        Returns:
            方法返回值或None
        """
        if obj is None:
            return None
        
        try:
            method = getattr(obj, method_name, None)
            if method and callable(method):
                return method(*args, **kwargs)
        except Exception as e:
            print(f"⚠️  调用 {method_name} 失败: {e}")
        
        return None


# 空对象实现（Null Object Pattern）

class NullDamageText:
    """空伤害飘字对象"""
    def show_damage(self, *args, **kwargs):
        pass
    
    def show_heal(self, *args, **kwargs):
        pass
    
    def show_text(self, *args, **kwargs):
        pass
    
    def update(self, dt):
        pass
    
    def draw(self, screen):
        pass


class NullScreenShake:
    """空屏幕震动对象"""
    def add_shake(self, duration, intensity):
        pass
    
    def update(self, dt):
        pass
    
    def get_offset(self):
        return (0, 0)
    
    def is_shaking(self):
        return False


class NullAudio:
    """空音频对象"""
    def play_music(self, *args, **kwargs):
        pass
    
    def stop_music(self, *args, **kwargs):
        pass
    
    def play_sfx(self, *args, **kwargs):
        pass
    
    def set_music_volume(self, volume):
        pass
    
    def set_sfx_volume(self, volume):
        pass


class NullTutorial:
    """空教程对象"""
    active = False
    
    def start(self):
        pass
    
    def skip(self):
        pass
    
    def check_action(self, action):
        pass
    
    def update(self, dt):
        pass
    
    def draw(self, screen):
        pass
    
    def handle_input(self, event):
        return False


class NullHelpPanel:
    """空帮助面板对象"""
    visible = False
    
    def toggle(self):
        pass
    
    def draw(self, screen):
        pass
    
    def handle_input(self, event):
        return False


# 便捷函数

def safe_update(obj, dt):
    """安全更新对象"""
    if obj and hasattr(obj, 'update'):
        try:
            obj.update(dt)
        except Exception as e:
            print(f"⚠️  更新失败: {e}")


def safe_draw(obj, screen):
    """安全绘制对象"""
    if obj and hasattr(obj, 'draw'):
        try:
            obj.draw(screen)
        except Exception as e:
            print(f"⚠️  绘制失败: {e}")
