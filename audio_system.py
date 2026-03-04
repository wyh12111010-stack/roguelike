"""
音频系统
管理背景音乐和音效
"""
import pygame
import os
from pathlib import Path


class AudioManager:
    """音频管理器"""
    def __init__(self):
        # 初始化pygame音频
        pygame.mixer.init()
        
        # 音量设置
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        
        # 音效缓存
        self.sfx_cache = {}
        
        # 当前播放的音乐
        self.current_music = None
        
        # 音频文件路径
        self.audio_dir = Path("assets/audio")
        self.music_dir = self.audio_dir / "music"
        self.sfx_dir = self.audio_dir / "sfx"
        
        # 确保目录存在
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.sfx_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== 音乐控制 ====================
    
    def play_music(self, music_name, loop=-1, fade_ms=1000):
        """播放背景音乐
        
        music_name: 音乐文件名（不含扩展名）
        loop: 循环次数（-1为无限循环）
        fade_ms: 淡入时间（毫秒）
        """
        if self.current_music == music_name:
            return
        
        music_path = self.music_dir / f"{music_name}.ogg"
        
        # 如果文件不存在，使用占位符
        if not music_path.exists():
            music_path = self.music_dir / f"{music_name}.mp3"
        
        if not music_path.exists():
            print(f"音乐文件不存在: {music_name}")
            return
        
        try:
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loop, fade_ms=fade_ms)
            self.current_music = music_name
        except Exception as e:
            print(f"播放音乐失败: {music_name} - {e}")
    
    def stop_music(self, fade_ms=1000):
        """停止音乐"""
        pygame.mixer.music.fadeout(fade_ms)
        self.current_music = None
    
    def pause_music(self):
        """暂停音乐"""
        pygame.mixer.music.pause()
    
    def resume_music(self):
        """恢复音乐"""
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume):
        """设置音乐音量（0.0-1.0）"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    # ==================== 音效控制 ====================
    
    def play_sfx(self, sfx_name, volume=None):
        """播放音效
        
        sfx_name: 音效文件名（不含扩展名）
        volume: 音量（None使用默认音量）
        """
        # 从缓存加载
        if sfx_name not in self.sfx_cache:
            sfx_path = self.sfx_dir / f"{sfx_name}.wav"
            
            # 如果文件不存在，使用占位符
            if not sfx_path.exists():
                sfx_path = self.sfx_dir / f"{sfx_name}.ogg"
            
            if not sfx_path.exists():
                # 不打印错误，避免刷屏
                return
            
            try:
                sound = pygame.mixer.Sound(str(sfx_path))
                self.sfx_cache[sfx_name] = sound
            except Exception as e:
                print(f"加载音效失败: {sfx_name} - {e}")
                return
        
        sound = self.sfx_cache[sfx_name]
        vol = volume if volume is not None else self.sfx_volume
        sound.set_volume(vol)
        sound.play()
    
    def set_sfx_volume(self, volume):
        """设置音效音量（0.0-1.0）"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    # ==================== 便捷方法 ====================
    
    def play_village_music(self):
        """播放村子音乐"""
        self.play_music("village", loop=-1)
    
    def play_combat_music(self):
        """播放战斗音乐"""
        self.play_music("combat", loop=-1)
    
    def play_boss_music(self):
        """播放Boss音乐"""
        self.play_music("boss", loop=-1)
    
    def play_attack_sfx(self):
        """播放攻击音效"""
        self.play_sfx("attack")
    
    def play_hit_sfx(self):
        """播放受击音效"""
        self.play_sfx("hit")
    
    def play_skill_sfx(self):
        """播放技能音效"""
        self.play_sfx("skill")
    
    def play_dash_sfx(self):
        """播放闪避音效"""
        self.play_sfx("dash")
    
    def play_ui_click_sfx(self):
        """播放UI点击音效"""
        self.play_sfx("ui_click", volume=0.5)
    
    def play_buy_sfx(self):
        """播放购买音效"""
        self.play_sfx("buy")
    
    def play_levelup_sfx(self):
        """播放升级音效"""
        self.play_sfx("levelup")
    
    def play_death_sfx(self):
        """播放死亡音效"""
        self.play_sfx("death")
    
    def play_victory_sfx(self):
        """播放胜利音效"""
        self.play_sfx("victory")


# ==================== 全局实例 ====================

_audio_manager = None


def init_audio():
    """初始化音频系统"""
    global _audio_manager
    _audio_manager = AudioManager()
    return _audio_manager


def get_audio():
    """获取音频管理器"""
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioManager()
    return _audio_manager


# ==================== 便捷函数 ====================

def play_music(music_name, **kwargs):
    """播放音乐"""
    audio = get_audio()
    audio.play_music(music_name, **kwargs)


def stop_music(**kwargs):
    """停止音乐"""
    audio = get_audio()
    audio.stop_music(**kwargs)


def play_sfx(sfx_name, **kwargs):
    """播放音效"""
    audio = get_audio()
    audio.play_sfx(sfx_name, **kwargs)


def set_music_volume(volume):
    """设置音乐音量"""
    audio = get_audio()
    audio.set_music_volume(volume)


def set_sfx_volume(volume):
    """设置音效音量"""
    audio = get_audio()
    audio.set_sfx_volume(volume)


# ==================== 音频文件说明 ====================

AUDIO_FILES_NEEDED = """
需要的音频文件：

音乐文件（放在 assets/audio/music/）：
- village.ogg - 村子音乐（悠扬、平静）
- combat.ogg - 战斗音乐（紧张、快节奏）
- boss.ogg - Boss音乐（史诗、激烈）

音效文件（放在 assets/audio/sfx/）：
- attack.wav - 攻击音效
- hit.wav - 受击音效
- skill.wav - 技能释放音效
- dash.wav - 闪避音效
- ui_click.wav - UI点击音效
- buy.wav - 购买音效
- levelup.wav - 升级音效
- death.wav - 死亡音效
- victory.wav - 胜利音效

推荐来源：
1. freesound.org - 免费音效库
2. incompetech.com - 免费音乐（Kevin MacLeod）
3. opengameart.org - 开源游戏素材
4. zapsplat.com - 免费音效

或者使用AI生成：
- Suno AI - 生成音乐
- ElevenLabs - 生成音效
"""


def print_audio_guide():
    """打印音频文件指南"""
    print(AUDIO_FILES_NEEDED)


# ==================== 占位符音频生成 ====================

def create_placeholder_audio():
    """创建占位符音频文件（静音）
    
    用于测试，避免因缺少音频文件而报错
    """
    import numpy as np
    from scipy.io import wavfile
    
    # 创建目录
    audio_dir = Path("assets/audio")
    music_dir = audio_dir / "music"
    sfx_dir = audio_dir / "sfx"
    
    music_dir.mkdir(parents=True, exist_ok=True)
    sfx_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成静音音效（0.1秒）
    sample_rate = 44100
    duration = 0.1
    samples = int(sample_rate * duration)
    silence = np.zeros(samples, dtype=np.int16)
    
    sfx_files = ["attack", "hit", "skill", "dash", "ui_click", "buy", "levelup", "death", "victory"]
    
    for sfx in sfx_files:
        path = sfx_dir / f"{sfx}.wav"
        if not path.exists():
            try:
                wavfile.write(str(path), sample_rate, silence)
                print(f"创建占位符音效: {sfx}.wav")
            except:
                pass
    
    print("占位符音频文件创建完成")
    print("建议替换为真实的音频文件以获得更好的体验")
