"""
测试游戏中的中文显示
"""
import pygame
from config import get_font, SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("中文字体测试")
clock = pygame.time.Clock()

# 测试文本
test_texts = [
    ("道韵: 100", 24),
    ("灵石: 50", 24),
    ("药水: 3 [R]", 24),
    ("当前: 第1层", 24),
    ("剩余敌人: 5", 24),
    ("测试中文显示", 36),
]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    screen.fill((30, 30, 40))
    
    # 绘制测试文本
    y = 50
    for text, size in test_texts:
        font = get_font(size)
        surface = font.render(text, True, (255, 255, 255))
        screen.blit(surface, (50, y))
        y += size + 20
    
    # 提示
    hint_font = get_font(18)
    hint = hint_font.render("按ESC退出", True, (150, 150, 150))
    screen.blit(hint, (50, SCREEN_HEIGHT - 50))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("测试完成")
