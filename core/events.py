"""
事件常量 - 统一管理事件名，便于发现与扩展
"""
# 战斗
COMBAT_START = "combat_start"
PARTICLE_SPAWN = "particle_spawn"
REACTION_TRIGGERED = "reaction_triggered"
COMBAT_END = "combat_end"
ENEMY_KILLED = "enemy_killed"
PLAYER_HIT = "player_hit"
PLAYER_DEATH = "player_death"
LEVEL_CLEAR = "level_clear"
VICTORY = "victory"

# 节点与流程
NODE_COMPLETE = "node_complete"
SHOP_ENTER = "shop_enter"
ROUTE_SELECT = "route_select"
ACHIEVEMENT_UNLOCKED = "achievement_unlocked"

# 场景（可扩展）
SCENE_CHANGE = "scene_change"
