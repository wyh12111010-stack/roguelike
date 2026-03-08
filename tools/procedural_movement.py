#!/usr/bin/env python3
"""程序化移动效果 - 无需额外帧"""

import math

import pygame


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.anim_timer = 0.0
        self.move_timer = 0.0  # 移动节奏计时器
        self.is_moving = False

    def update(self, dt, target_x, target_y):
        self.anim_timer += dt

        # 移动逻辑
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 5:
            self.is_moving = True
            self.move_timer += dt
            # 移动
            speed = 100
            self.x += (dx / dist) * speed * dt
            self.y += (dy / dist) * speed * dt
        else:
            self.is_moving = False
            self.move_timer = 0

    def draw(self, screen, idle_frames):
        from tools.sprite_loader import play_animation

        # 始终播放待机动画
        idx = play_animation(idle_frames, self.anim_timer, fps=8)
        frame = idle_frames[idx]

        # 移动时添加效果
        if self.is_moving:
            # 效果 1：上下轻微晃动（模拟走路）
            bob_offset = math.sin(self.move_timer * 10) * 2

            # 效果 2：轻微倾斜（朝移动方向）
            # angle = math.atan2(dy, dx)
            # frame = pygame.transform.rotate(frame, math.degrees(angle))

            # 效果 3：拉伸（模拟步伐）
            stretch = 1 + abs(math.sin(self.move_timer * 10)) * 0.05
            w, h = frame.get_size()
            frame = pygame.transform.scale(frame, (int(w * stretch), h))
        else:
            bob_offset = 0

        # 绘制
        screen.blit(frame, (self.x, self.y + bob_offset))


# 使用示例
def demo():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # 加载待机帧
    from tools.sprite_loader import load_sprite_sheet_grid

    idle_frames = load_sprite_sheet_grid("assets/enemy_melee_anim.png", cols=2, rows=2)

    enemy = Enemy(100, 100)
    target_x, target_y = 400, 300

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                target_x, target_y = event.pos

        enemy.update(dt, target_x, target_y)

        screen.fill((50, 50, 50))
        enemy.draw(screen, idle_frames)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    demo()
