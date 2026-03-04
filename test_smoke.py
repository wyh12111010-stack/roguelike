"""
完整冒烟测试 - 测试所有核心功能
"""
import sys
import traceback

def test_imports():
    """测试所有模块导入"""
    print("\n[1/10] 测试模块导入...")
    errors = []
    
    modules = [
        'pygame',
        'config',
        'attribute',
        'player',
        'enemy',
        'fabao',
        'linggen',
        'accessory',
        'game',
        'village',
        'ui',
        'ui.components',
        'ui.hud',
        'ui.fabao_display',
        'ui.character_panel',
        'ui.ui_manager',
        'systems.combat',
        'core',
        'meta',
        'save',
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"  [OK] {module}")
        except Exception as e:
            errors.append(f"{module}: {str(e)}")
            print(f"  [ERROR] {module}: {str(e)}")
    
    return errors

def test_game_init():
    """测试游戏初始化"""
    print("\n[2/10] 测试游戏初始化...")
    try:
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        
        from game import Game
        game = Game(screen)
        
        print("  [OK] 游戏初始化成功")
        return game, None
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        traceback.print_exc()
        return None, str(e)

def test_ui_system(game):
    """测试 UI 系统"""
    print("\n[3/10] 测试 UI 系统...")
    errors = []
    
    try:
        # 检查 UI 管理器
        if not hasattr(game, 'ui_manager'):
            errors.append("游戏缺少 ui_manager")
        else:
            print("  [OK] UI 管理器存在")
        
        # 检查 UI 组件
        if hasattr(game, 'ui_manager'):
            ui = game.ui_manager
            if not hasattr(ui, 'hud'):
                errors.append("UI 管理器缺少 HUD")
            else:
                print("  [OK] HUD 组件存在")
            
            if not hasattr(ui, 'fabao_display'):
                errors.append("UI 管理器缺少法宝显示")
            else:
                print("  [OK] 法宝显示组件存在")
            
            if not hasattr(ui, 'character_panel'):
                errors.append("UI 管理器缺少角色面板")
            else:
                print("  [OK] 角色面板组件存在")
    
    except Exception as e:
        errors.append(f"UI 系统测试失败: {str(e)}")
        traceback.print_exc()
    
    return errors

def test_player_creation(game):
    """测试玩家创建"""
    print("\n[4/10] 测试玩家创建...")
    errors = []
    
    try:
        from player import Player
        from config import ARENA_X, ARENA_Y, ARENA_W, ARENA_H
        
        player = Player(ARENA_X + ARENA_W // 2, ARENA_Y + ARENA_H // 2)
        
        # 检查基础属性
        if not hasattr(player, 'health'):
            errors.append("玩家缺少 health 属性")
        if not hasattr(player, 'mana'):
            errors.append("玩家缺少 mana 属性")
        if not hasattr(player, 'lingshi'):
            errors.append("玩家缺少 lingshi 属性")
        
        print("  [OK] 玩家创建成功")
        
        # 测试 UI 设置玩家
        if hasattr(game, 'ui_manager'):
            game.ui_manager.set_player(player)
            print("  [OK] UI 管理器设置玩家成功")
        
    except Exception as e:
        errors.append(f"玩家创建失败: {str(e)}")
        traceback.print_exc()
    
    return errors

def test_combat_system():
    """测试战斗系统"""
    print("\n[5/10] 测试战斗系统...")
    errors = []
    
    try:
        from systems.combat import CombatSystem
        
        # 检查关键方法
        if not hasattr(CombatSystem, 'update_combat'):
            errors.append("CombatSystem 缺少 update_combat 方法")
        if not hasattr(CombatSystem, 'draw_combat'):
            errors.append("CombatSystem 缺少 draw_combat 方法")
        
        print("  [OK] 战斗系统完整")
    
    except Exception as e:
        errors.append(f"战斗系统测试失败: {str(e)}")
        traceback.print_exc()
    
    return errors

def test_event_system():
    """测试事件系统"""
    print("\n[6/10] 测试事件系统...")
    errors = []
    
    try:
        from core import EventBus
        from core.events import PLAYER_HIT, ENEMY_KILLED, LEVEL_CLEAR
        
        # 测试事件订阅和触发
        test_called = [False]
        
        def test_handler(**kwargs):
            test_called[0] = True
        
        EventBus.on(PLAYER_HIT, test_handler)
        EventBus.emit(PLAYER_HIT, damage=10)
        
        if not test_called[0]:
            errors.append("事件系统未正确触发")
        else:
            print("  [OK] 事件系统正常")
        
        EventBus.off(PLAYER_HIT, test_handler)
    
    except Exception as e:
        errors.append(f"事件系统测试失败: {str(e)}")
        traceback.print_exc()
    
    return errors

def test_save_system():
    """测试存档系统"""
    print("\n[7/10] 测试存档系统...")
    errors = []
    
    try:
        from save import RunSaveData, PlayerSaveData
        from meta import meta
        
        # 检查 meta 对象
        if not hasattr(meta, 'daoyun'):
            errors.append("meta 缺少 daoyun 属性")
        if not hasattr(meta, 'unlocked_linggen'):
            errors.append("meta 缺少 unlocked_linggen 属性")
        
        print("  [OK] 存档系统完整")
    
    except Exception as e:
        errors.append(f"存档系统测试失败: {str(e)}")
        traceback.print_exc()
    
    return errors

def test_resource_loading():
    """测试资源加载"""
    print("\n[8/10] 测试资源加载...")
    errors = []
    
    try:
        from linggen import LINGGEN_LIST
        from fabao import FABAO_LIST
        from accessory import ACCESSORY_LIST
        
        if len(LINGGEN_LIST) == 0:
            errors.append("灵根列表为空")
        else:
            print(f"  [OK] 灵根列表: {len(LINGGEN_LIST)} 个")
        
        if len(FABAO_LIST) == 0:
            errors.append("法宝列表为空")
        else:
            print(f"  [OK] 法宝列表: {len(FABAO_LIST)} 个")
        
        if len(ACCESSORY_LIST) == 0:
            errors.append("饰品列表为空")
        else:
            print(f"  [OK] 饰品列表: {len(ACCESSORY_LIST)} 个")
    
    except Exception as e:
        errors.append(f"资源加载测试失败: {str(e)}")
        traceback.print_exc()
    
    return errors

def test_game_loop(game):
    """测试游戏循环"""
    print("\n[9/10] 测试游戏循环...")
    errors = []
    
    try:
        import pygame
        
        # 模拟几帧更新
        for i in range(5):
            game.update(0.016)  # 60 FPS
        
        print("  [OK] 游戏循环正常")
        
        # 测试绘制
        screen = pygame.display.get_surface()
        game.draw()
        
        print("  [OK] 游戏绘制正常")
    
    except Exception as e:
        errors.append(f"游戏循环测试失败: {str(e)}")
        traceback.print_exc()
    
    return errors

def test_circular_dependencies():
    """测试循环依赖"""
    print("\n[10/10] 测试循环依赖...")
    errors = []
    
    try:
        import sys
        import importlib
        
        # 重新导入所有模块，检查循环依赖
        modules_to_test = [
            'game',
            'player',
            'enemy',
            'ui.ui_manager',
            'systems.combat',
        ]
        
        for module_name in modules_to_test:
            if module_name in sys.modules:
                del sys.modules[module_name]
        
        for module_name in modules_to_test:
            try:
                importlib.import_module(module_name)
                print(f"  [OK] {module_name} 无循环依赖")
            except ImportError as e:
                if "circular" in str(e).lower():
                    errors.append(f"{module_name} 存在循环依赖")
    
    except Exception as e:
        errors.append(f"循环依赖测试失败: {str(e)}")
        traceback.print_exc()
    
    return errors

def main():
    """运行所有测试"""
    print("=" * 60)
    print("完整冒烟测试")
    print("=" * 60)
    
    all_errors = []
    
    # 1. 测试导入
    errors = test_imports()
    all_errors.extend(errors)
    
    # 2. 测试游戏初始化
    game, error = test_game_init()
    if error:
        all_errors.append(error)
        print("\n[CRITICAL] 游戏初始化失败，后续测试跳过")
        print_summary(all_errors)
        return
    
    # 3. 测试 UI 系统
    errors = test_ui_system(game)
    all_errors.extend(errors)
    
    # 4. 测试玩家创建
    errors = test_player_creation(game)
    all_errors.extend(errors)
    
    # 5. 测试战斗系统
    errors = test_combat_system()
    all_errors.extend(errors)
    
    # 6. 测试事件系统
    errors = test_event_system()
    all_errors.extend(errors)
    
    # 7. 测试存档系统
    errors = test_save_system()
    all_errors.extend(errors)
    
    # 8. 测试资源加载
    errors = test_resource_loading()
    all_errors.extend(errors)
    
    # 9. 测试游戏循环
    errors = test_game_loop(game)
    all_errors.extend(errors)
    
    # 10. 测试循环依赖
    errors = test_circular_dependencies()
    all_errors.extend(errors)
    
    # 打印总结
    print_summary(all_errors)

def print_summary(errors):
    """打印测试总结"""
    print("\n" + "=" * 60)
    if len(errors) == 0:
        print("[SUCCESS] 所有测试通过！游戏架构健康！")
    else:
        print(f"[FAILED] 发现 {len(errors)} 个问题：")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
    print("=" * 60)

if __name__ == "__main__":
    main()
