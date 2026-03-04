"""
战斗系统集成优化
将所有新系统集成到战斗中
"""

# ==================== 使用说明 ====================

"""
这个文件包含了所有需要集成到现有代码中的修改。

由于直接修改可能会有编码问题，这里提供完整的集成代码。

请按照以下步骤手动集成：

1. 在 player.py 的攻击方法中：
   - 应用暴击判定
   - 应用伤害计算
   - 显示伤害飘字

2. 在 enemy.py 的受伤方法中：
   - 显示伤害飘字
   - 暴击时显示特效

3. 在击杀敌人时：
   - 显示击杀粒子特效
   - 播放音效
   - 触发屏幕震动

4. 在 game.py 中：
   - 初始化所有新系统
   - 场景切换时播放音乐

5. 在关卡生成时：
   - 使用波次系统生成敌人
"""

# ==================== 1. Player攻击集成 ====================

"""
在 player.py 的攻击方法中添加：

from accessory_effects import calculate_final_damage, roll_crit
from damage_text import show_damage
from screen_shake import shake_screen
from audio_system import play_sfx

# 在造成伤害时：
base_damage = self.fabao.damage
is_crit = roll_crit(self)
final_damage = calculate_final_damage(self, base_damage, target=enemy, is_reaction=False)

enemy.health -= final_damage

# 显示伤害飘字
show_damage(enemy.x, enemy.y, final_damage, is_crit=is_crit)

# 暴击特效
if is_crit:
    from enhanced_particles import spawn_crit_effect
    if hasattr(game, 'particle_mgr'):
        spawn_crit_effect(enemy.x, enemy.y, game.particle_mgr)
    shake_screen(0.15, 8)

# 播放音效
play_sfx("attack")
"""

# ==================== 2. Enemy受伤集成 ====================

"""
在 enemy.py 中添加 take_damage 方法：

def take_damage(self, damage, is_crit=False):
    self.health -= damage
    
    # 显示伤害飘字
    from damage_text import show_damage
    show_damage(self.x, self.y, damage, is_crit=is_crit)
    
    return self.health <= 0  # 返回是否死亡
"""

# ==================== 3. 击杀敌人集成 ====================

"""
在击杀敌人时（game.py 或 combat.py）：

from enhanced_particles import spawn_kill_effect
from screen_shake import shake_screen
from audio_system import play_sfx

# 击杀时
is_elite = getattr(enemy, 'is_elite', False)
spawn_kill_effect(enemy.x, enemy.y, enemy.color, is_elite, game.particle_mgr)

# 音效
play_sfx("death")

# 震动
if is_elite:
    shake_screen(0.3, 15)
else:
    shake_screen(0.1, 5)
"""

# ==================== 4. Game初始化集成 ====================

"""
在 game.py 的 __init__ 中添加：

# 音频系统
from audio_system import init_audio
self.audio = init_audio()

# 教程系统
from tutorial import init_tutorial
self.tutorial = init_tutorial()

# 帮助系统
from help_system import init_help_system
self.help_panel, self.quick_tips_hud = init_help_system()
"""

# ==================== 5. 场景切换音乐 ====================

"""
在场景切换时（game.py）：

# 进入村子
if self.scene == "village":
    self.audio.play_village_music()

# 进入战斗
if self.scene == "combat":
    self.audio.play_combat_music()

# Boss战
if is_boss_level:
    self.audio.play_boss_music()
"""

# ==================== 6. 波次系统集成 ====================

"""
在生成敌人时（game.py 或 combat.py）：

from enemy_waves import spawn_level_enemies

# 替换原有的敌人生成
enemy_waves = spawn_level_enemies(
    level_index=self.current_level,
    arena_x=ARENA_X,
    arena_y=ARENA_Y,
    arena_w=ARENA_W,
    arena_h=ARENA_H
)

# 存储波次
self.enemy_waves = enemy_waves
self.wave_timer = 0.0

# 在 update 中：
self.wave_timer += dt
for wave_data in self.enemy_waves:
    if not wave_data['spawned'] and self.wave_timer >= wave_data['delay']:
        self.enemies.extend(wave_data['enemies'])
        wave_data['spawned'] = True
"""

# ==================== 7. 精英怪能力集成 ====================

"""
在生成精英怪时：

from elite_abilities import assign_elite_ability

# 创建精英怪后
if enemy.is_elite:
    modifier_name = enemy.elite_modifier
    assign_elite_ability(enemy, modifier_name)

# 在敌人 update 中：
if hasattr(enemy, 'elite_ability') and enemy.elite_ability:
    enemy.elite_ability.update(dt, player, game)
"""

# ==================== 8. 奇遇事件集成 ====================

"""
在关卡完成时：

from random_events import trigger_event_for_level

# 检查是否触发事件
event = trigger_event_for_level(self.current_level, self.player, self)
if event:
    self.current_event = event
    self.event_pending = True
"""

# ==================== 9. 教程集成 ====================

"""
在游戏开始时：

from tutorial import should_show_tutorial, start_tutorial

if should_show_tutorial():
    start_tutorial()

# 在 update 中检测玩家操作：
if self.tutorial.active:
    # 检测移动
    if keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]:
        self.tutorial.check_action("move")
    
    # 检测攻击
    if pygame.mouse.get_pressed()[0]:
        self.tutorial.check_action("attack")
    
    # 检测技能
    if keys[pygame.K_e]:
        self.tutorial.check_action("skill")
    
    # 检测闪避
    if keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT]:
        self.tutorial.check_action("dash")

# 在 draw 中：
if self.tutorial.active:
    self.tutorial.draw(screen)
"""

# ==================== 10. 帮助系统集成 ====================

"""
在 update 中：

# 检测 H 键
if keys[pygame.K_h]:
    self.help_panel.toggle()

# 在 draw 中：
self.help_panel.draw(screen)
self.quick_tips_hud.draw(screen)
"""

# ==================== 完整集成检查清单 ====================

INTEGRATION_CHECKLIST = """
集成检查清单：

[ ] 1. player.py - 攻击时应用暴击和伤害计算
[ ] 2. player.py - 攻击时显示伤害飘字
[ ] 3. enemy.py - 添加 take_damage 方法
[ ] 4. 击杀时显示粒子特效
[ ] 5. 击杀时播放音效和震动
[ ] 6. game.py - 初始化所有新系统
[ ] 7. 场景切换时播放音乐
[ ] 8. 使用波次系统生成敌人
[ ] 9. 精英怪分配能力
[ ] 10. 关卡完成时触发事件
[ ] 11. 教程系统集成
[ ] 12. 帮助系统集成（H键）

完成后测试：
[ ] 伤害飘字显示
[ ] 暴击特效
[ ] 击杀粒子
[ ] 屏幕震动
[ ] 音效播放
[ ] 帮助面板
[ ] 教程流程
"""

print(INTEGRATION_CHECKLIST)
