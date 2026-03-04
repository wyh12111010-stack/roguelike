"""测试游戏能否正常初始化"""
import sys
import os

# 设置工作目录
os.chdir(r"f:\游戏")

try:
    print("初始化 pygame...")
    import pygame
    pygame.init()
    
    print("创建屏幕...")
    screen = pygame.display.set_mode((800, 600))
    
    print("导入 Game 类...")
    from game import Game
    
    print("创建 Game 实例...")
    game = Game(screen)
    
    print("检查初始场景...")
    assert game.scene == "village", f"初始场景应该是 village，实际是 {game.scene}"
    
    print("\n游戏初始化成功！")
    print(f"- 场景: {game.scene}")
    print(f"- 村子玩家位置: {game.village_player}")
    
    pygame.quit()
    print("\n测试通过！游戏可以正常启动。")
    sys.exit(0)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
