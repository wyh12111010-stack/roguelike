"""轻量战斗提示音：无外部资源，运行时合成短音。"""

import contextlib
import math
import time
from array import array

import pygame

from meta import meta

_SOUND_CACHE = {}
_LAST_PLAY_AT = {}
_LAST_GLOBAL_AT = 0.0
_LAST_ENEMY_CUE_AT = 0.0
_LAST_PLAYER_AT = 0.0

# 参考动作 roguelite 常见做法：
# - 关键读招音 > 普通提示音
# - 同类音效限频，防止高密度刷屏
# - 全局最小间隔，避免混音泥化
_STAGE_CONFIG = {
    "warn": {"priority": 2, "min_interval": 0.12, "freq_shift": 0, "ms": 105, "volume": 0.18},
    "cast": {"priority": 4, "min_interval": 0.08, "freq_shift": 120, "ms": 85, "volume": 0.25},
}
_GLOBAL_MIN_INTERVAL = 0.03
_ENEMY_CUE_MIN_INTERVAL = 0.18
_PLAYER_ATTACK_MIN_INTERVAL = 0.06


def _ensure_mixer():
    try:
        if pygame.mixer.get_init():
            return True
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=256)
        return True
    except Exception:
        return False


def _effective_sfx_volume():
    master = max(0.0, min(1.0, float(getattr(meta, "master_volume", 1.0))))
    sfx = max(0.0, min(1.0, float(getattr(meta, "sfx_volume", 1.0))))
    return master * sfx


def _build_tone(freq_hz=440, ms=90, volume=0.22, sample_rate=22050):
    total = max(1, int(sample_rate * (ms / 1000.0)))
    attack = max(1, int(total * 0.08))
    release = max(1, int(total * 0.2))
    data = array("h")
    for i in range(total):
        t = i / sample_rate
        amp = math.sin(2 * math.pi * freq_hz * t)
        if i < attack:
            env = i / attack
        elif i > total - release:
            env = max(0.0, (total - i) / release)
        else:
            env = 1.0
        s = int(32767 * volume * amp * env)
        data.append(s)
    return data.tobytes()


def _get_tone(freq_hz, ms, volume):
    key = (int(freq_hz), int(ms), round(float(volume), 3))
    if key in _SOUND_CACHE:
        return _SOUND_CACHE[key]
    if not _ensure_mixer():
        return None
    snd = pygame.mixer.Sound(buffer=_build_tone(freq_hz=freq_hz, ms=ms, volume=volume))
    with contextlib.suppress(Exception):
        snd.set_volume(_effective_sfx_volume())
    _SOUND_CACHE[key] = snd
    return snd


def _freq_by_attr(attr):
    name = getattr(attr, "name", "") or ""
    if name == "FIRE":
        return 560
    if name == "WOOD":
        return 500
    if name == "EARTH":
        return 430
    return 470


def _now():
    return time.perf_counter()


def _can_play(stage, priority, now):
    global _LAST_GLOBAL_AT
    last = _LAST_PLAY_AT.get(stage)
    stage_cfg = _STAGE_CONFIG.get(stage, _STAGE_CONFIG["warn"])
    min_stage = stage_cfg["min_interval"]
    if last and (now - last["t"] < min_stage):
        # 同类音效太近：只有更高优先级才允许抢占
        if priority <= last["priority"]:
            return False
    if now - _LAST_GLOBAL_AT < _GLOBAL_MIN_INTERVAL:
        # 全局太密：只有高优先级 cast 允许越过
        if priority < _STAGE_CONFIG["cast"]["priority"]:
            return False
    return True


def play_boss_cue(stage="warn", attr=None, priority=None):
    """Boss 读招提示音。stage=warn/cast，带优先级与节流。"""
    mode = getattr(meta, "boss_cue_mode", 1)
    if mode <= 0:
        return
    stage_cfg = _STAGE_CONFIG.get(stage, _STAGE_CONFIG["warn"])
    prio = int(priority if priority is not None else stage_cfg["priority"])
    if mode >= 2:
        # 强化模式：允许更密集且略高优先级
        prio += 1
    now = _now()
    if not _can_play(stage, prio, now):
        return
    base = _freq_by_attr(attr)
    ms = stage_cfg["ms"]
    volume = stage_cfg["volume"]
    if mode >= 2:
        ms = max(60, int(ms * 0.9))
        volume = min(0.35, volume * 1.1)
    snd = _get_tone(
        base + stage_cfg["freq_shift"],
        ms,
        volume,
    )
    if snd:
        try:
            snd.set_volume(_effective_sfx_volume())
            snd.play()
            _LAST_PLAY_AT[stage] = {"t": now, "priority": prio}
            global _LAST_GLOBAL_AT
            _LAST_GLOBAL_AT = now
        except Exception:
            pass


def play_enemy_cue(attr=None, cue_type="warn"):
    """普通怪读招轻提示，强度低于 Boss。"""
    global _LAST_ENEMY_CUE_AT
    mode = getattr(meta, "boss_cue_mode", 1)
    if mode <= 0:
        return
    now = _now()
    if now - _LAST_ENEMY_CUE_AT < _ENEMY_CUE_MIN_INTERVAL:
        return
    base = _freq_by_attr(attr)
    if cue_type == "cast":
        freq, ms, vol = base + 60, 60, 0.12
    else:
        freq, ms, vol = base - 40, 75, 0.10
    snd = _get_tone(freq, ms, vol)
    if snd:
        try:
            snd.set_volume(_effective_sfx_volume())
            snd.play()
            _LAST_ENEMY_CUE_AT = now
        except Exception:
            pass


def play_player_attack(form="arc", attr=None):
    """玩家普攻轻提示，按法宝攻形区分音色。"""
    global _LAST_PLAYER_AT
    now = _now()
    if now - _LAST_PLAYER_AT < _PLAYER_ATTACK_MIN_INTERVAL:
        return
    base = _freq_by_attr(attr)
    form_cfg = {
        "arc": (base + 40, 52, 0.085),
        "pierce": (base + 130, 48, 0.08),
        "fan": (base + 75, 55, 0.08),
        "heavy": (base - 30, 72, 0.10),
        "parabolic": (base - 10, 64, 0.09),
    }
    freq, ms, vol = form_cfg.get(form, (base + 30, 52, 0.08))
    snd = _get_tone(freq, ms, vol)
    if snd:
        try:
            snd.set_volume(_effective_sfx_volume())
            snd.play()
            _LAST_PLAYER_AT = now
        except Exception:
            pass


# ─── 额外反馈音效（P3a 接线） ───

_LAST_HIT_AT = 0.0
_LAST_KILL_AT = 0.0
_LAST_DASH_AT = 0.0


def play_hit_sfx():
    """玩家受击短音：低频重击感。"""
    global _LAST_HIT_AT
    now = _now()
    if now - _LAST_HIT_AT < 0.15:
        return
    snd = _get_tone(220, 80, 0.18)
    if snd:
        try:
            snd.set_volume(_effective_sfx_volume())
            snd.play()
            _LAST_HIT_AT = now
        except Exception:
            pass


def play_kill_sfx():
    """敌人死亡短音：上升音调。"""
    global _LAST_KILL_AT
    now = _now()
    if now - _LAST_KILL_AT < 0.08:
        return
    snd = _get_tone(680, 55, 0.12)
    if snd:
        try:
            snd.set_volume(_effective_sfx_volume())
            snd.play()
            _LAST_KILL_AT = now
        except Exception:
            pass


def play_dash_sfx():
    """冲刺/闪避短音：快速刷风感。"""
    global _LAST_DASH_AT
    now = _now()
    if now - _LAST_DASH_AT < 0.3:
        return
    snd = _get_tone(350, 45, 0.10)
    if snd:
        try:
            snd.set_volume(_effective_sfx_volume())
            snd.play()
            _LAST_DASH_AT = now
        except Exception:
            pass


def play_levelup_sfx():
    """过关音效：升调和弦。"""
    snd = _get_tone(520, 120, 0.15)
    if snd:
        try:
            snd.set_volume(_effective_sfx_volume())
            snd.play()
        except Exception:
            pass
    snd2 = _get_tone(780, 100, 0.12)
    if snd2:
        try:
            snd2.set_volume(_effective_sfx_volume())
            snd2.play()
        except Exception:
            pass


def play_death_sfx():
    """玩家死亡音效：下降低音。"""
    snd = _get_tone(180, 200, 0.20)
    if snd:
        try:
            snd.set_volume(_effective_sfx_volume())
            snd.play()
        except Exception:
            pass
