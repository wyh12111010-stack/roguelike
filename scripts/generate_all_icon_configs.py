"""
完整图标提示词配置生成器
生成所有 99 个图标的 AI 优化提示词
"""
import json
import os

# 完整的法宝图标提示词（21 个）
FABAO_PROMPTS = {
    # 基础法宝（7 个）
    "赤炎剑": {
        "positive": "pixel art icon, 48x48 pixels, straight sword with fire element, diagonal placement from bottom-left to top-right at 45 degrees, blade: bright red (255,69,0) to orange-red (255,100,50) gradient in pixel steps, length 36px width 6px, sharp triangular tip with white (255,255,255) highlight 3px, hilt: deep red (150,10,10) with small guard 3x5px, 3 orange-red (255,100,50) flame particles around blade 2-3px each, chunky pixel style 6-8px per block, high contrast, vibrant red, transparent background, FC/NES aesthetic, retro pixel art, sharp edges, no anti-aliasing, no smooth gradients",
        "negative": "blurry, smooth, anti-aliased, gradient, realistic, 3D, shading, modern style, high resolution, detailed, photorealistic, small pixels, fine details, complex patterns",
        "size": "48x48",
        "filename": "fabao_chiyanjian.png"
    },
    "玄水符": {
        "positive": "pixel art icon, 48x48 pixels, rectangular yellow talisman paper, vertical placement, paper: light yellow (240,220,180) 12x32px, blue (30,144,255) water wave symbols in center, 3 horizontal wavy lines 1px each, red (220,20,60) seal stamp 4x4px at top, 3 blue (100,180,255) water droplets floating around 2-3px each, chunky pixel style 5-7px per block, paper texture with vertical lines, transparent background, FC/NES aesthetic, retro pixel art, sharp edges, no anti-aliasing",
        "negative": "blurry, smooth, realistic, 3D, modern, high-res, detailed, anti-aliased, gradient, photorealistic, complex",
        "size": "48x48",
        "filename": "fabao_xuanshuifu.png"
    },
    "青木杖": {
        "positive": "pixel art icon, 48x48 pixels, wooden staff with leaves on top, vertical placement, staff: brown (139,90,43) 4x34px with wood grain, leaf cluster: green (34,139,34) cross or diamond shape 8x8px at top, 2-3 green (50,160,50) vine wraps around staff 3-4px each, 2 light green (100,200,100) leaf particles 2px each, chunky pixel style 6-8px per block, natural brown and green contrast, transparent background, FC/NES aesthetic, retro pixel art, sharp edges, no anti-aliasing",
        "negative": "blurry, smooth, realistic, modern, detailed, anti-aliased, 3D, photorealistic, high-res, complex patterns",
        "size": "48x48",
        "filename": "fabao_qingmuzhang.png"
    },
    "庚金刃": {
        "positive": "pixel art icon, 48x48 pixels, short dagger with golden blade, diagonal placement from bottom-left to top-right at 45 degrees, blade: gold (218,165,32) triangular sharp, length 28px width 8px, sharp tip with white (255,255,255) highlight 2px, blade edge with white (240,240,240) reflection line 1px, hilt: dark gray (80,80,80) with guard 4x3px, 3 golden light points bright gold (255,223,0) 2px each, chunky pixel style 6-8px per block, bright gold with white highlights, transparent background, FC/NES aesthetic, sharp edges, no anti-aliasing",
        "negative": "blurry, smooth, anti-aliased, realistic, 3D, modern, detailed, photorealistic, complex",
        "size": "48x48",
        "filename": "fabao_gengjinren.png"
    },
    "厚土印": {
        "positive": "pixel art icon, 48x48 pixels, square stone seal, front view, seal face: brown (139,90,43) 20x20px square, seal symbol: dark brown (80,50,25) mountain or earth character simplified to 3-5px geometric pattern, seal handle: dark brown (90,55,28) at bottom 6x8px rectangle, 3 stone particles light brown (160,120,80) 2-3px each around seal, chunky pixel style 6-8px per block, heavy brown tones with layers, transparent background, FC/NES aesthetic, sharp edges, no anti-aliasing",
        "negative": "blurry, smooth, realistic, modern, detailed, anti-aliased, 3D, photorealistic, complex",
        "size": "48x48",
        "filename": "fabao_houtouyin.png"
    },
    "离火针": {
        "positive": "pixel art icon, 48x48 pixels, thin flying needle, horizontal placement, needle body: red (255,69,0) straight thin, length 32px width 2px, sharp tip: white (255,255,255) right side 2px sharp angle, needle highlight: orange (255,140,0) thin line along top 1px, needle tail flame: red-orange (255,100,50) 3-4px flame shape, 3 orange (255,140,0) spark particles 1-2px each around needle, chunky pixel style 5-7px per block, vibrant red with thin needle, transparent background, FC/NES aesthetic, sharp edges, no anti-aliasing",
        "negative": "blurry, smooth, realistic, 3D, modern, detailed, anti-aliased, photorealistic, complex",
        "size": "48x48",
        "filename": "fabao_lihuozhen.png"
    },
    "玄坤鼎": {
        "positive": "pixel art icon, 48x48 pixels, three-legged round cauldron, front view, cauldron body: deep purple (75,0,130) round shape diameter 20px height 16px, cauldron mouth: elliptical opening dark (50,0,90) showing depth, 3 short thick legs: deep purple (60,0,100) each 4px wide 6px tall at bottom in triangle formation, cauldron patterns: dark (50,0,90) horizontal lines 2-3, purple smoke rising from mouth light purple (138,43,226) 3-4px wavy shape, chunky pixel style 6-8px per block, mysterious deep purple with ethereal smoke, transparent background, FC/NES aesthetic, sharp edges, no anti-aliasing",
        "negative": "blurry, smooth, realistic, modern, detailed, anti-aliased, 3D, photorealistic, complex",
        "size": "48x48",
        "filename": "fabao_xuankunding.png"
    },
    
    # 极速流（3 个）
    "流光鞭": {
        "positive": "pixel art icon, 48x48 pixels, long whip in S-curve shape, whip body: red (220,20,60) to orange (255,140,0) gradient S-curve, width 3px length 36px from bottom-left to top-right, whip handle: deep red (150,10,10) at bottom-left 4x6px block, whip segments: dark red (180,20,20) 3-4 nodes each 2px, whip tip: orange-red (255,100,50) at top-right tapering to 1px, 4 orange (255,140,0) flame particles along whip showing speed, chunky pixel style 5-7px per block, vibrant red-orange gradient, transparent background, FC/NES aesthetic, sharp edges, no anti-aliasing",
        "negative": "blurry, smooth, realistic, 3D, modern, detailed, anti-aliased, photorealistic, complex",
        "size": "48x48",
        "filename": "fabao_liuguangbian.png"
    },
    "暗影镖": {
        "positive": "pixel art icon, 48x48 pixels, cross-shaped shuriken in rotation, shuriken body: dark gray (60,60,60) and black (30,30,30) cross shape with 4 sharp points, each point 8px long 4px wide, center circle: dark gray (70,70,70) diameter 6px, sharp tips: white (200,200,200) highlight 1px at each point end, blade edges: light gray (120,120,120) reflection line 1px, 45-degree rotation (X-shape) showing spin, 2-3 gray (100,100,100) motion trail arcs 2px each, chunky pixel style 6-8px per block, dark cold tones with sharp highlights, transparent background, FC/NES aesthetic, sharp edges, no anti-aliasing",
        "negative": "blurry, smooth, realistic, 3D, modern, detailed, anti-aliased, photorealistic, complex",
        "size": "48x48",
        "filename": "fabao_anyingbiao.png"
    },
    "疾风爪": {
        "positive": "pixel art icon, 48x48 pixels, three-claw gauntlet with claws pointing right, gauntlet: green (34,139,34) at left side 8x12px, 3 claws: light green (50,205,50) each 2px wide 10px long parallel with 2px spacing, claw tips: white (255,255,255) each tip 2px extremely sharp, gauntlet texture: dark green (20,100,20) 2-3 horizontal lines, 3-4 cyan (0,255,255) wind lines horizontal short lines 3-4px long 1px wide at right side showing speed, chunky pixel style 6-8px per block, vibrant green with light wind lines, transparent background, FC/NES aesthetic, sharp edges, no anti-aliasing",
        "negative": "blurry, smooth, realistic, 3D, modern, detailed, anti-aliased, photorealistic, complex",
        "size": "48x48",
        "filename": "fabao_jifengzhua.png"
    },
    
    # 重压流（3 个）
    "巨灵锤": {
        "positive": "pixel art icon, 48x48 pixels, large war hammer, vertical placement, hammer head: dark gray (80,80,80) rectangular 16x12px at top, hammer surface: light gray (150,150,150) highlight 2-3px showing metal, handle: brown (139,90,43) 4px wide 24px long, handle grip: dark brown (90,55,28) 2-3 horizontal lines, 2-3 gray (120,120,120) impact particles at bottom 2px each, chunky pixel style 6-8px per block, heavy metallic feel, transparent background, FC/NES aesthetic, sharp edges, no anti-aliasing",
        "negative": "blurry, smooth, realistic, 3D, modern, detailed, anti-aliased, photorealistic, complex",
        "size": "48x48",
        "filename": "fabao_julingchui.png"
    },
    "玄铁斧": {
        "positive": "pixel art icon, 48x48 pixels, heavy battle axe, diagonal placement from bottom-left to top-right, axe blade: dark gray (60,60,60) crescent shape 18x14px, blade edge: white (240,240,240) sharp line 1-2px, axe handle: brown (139,90,43) 4px wide 26px long, handle end: dark brown (90,55,28) 6x4px block, 2 metallic shine spots light gray (180,180,180) 2px each on blade, chunky pixel style 6-8px per block, heavy dark metal, transparent background, FC/NES aesthetic, sharp edges, no anti-aliasing",
        "negative": "blurry, smooth, realistic, 3D, modern, detailed, anti-aliased, photorealistic, complex",
        "size": "48x48",
        "filename": "fabao_xuantiefu.png"
    },
    "碎星杵": {
        "positive": "pixel art icon, 48x48 pixels, spiked mace, vertical placement, mace head: dark gray (70,70,70) round 14x14px with 6 spikes each 3-4px protruding, spikes: light gray (150,150,150) sharp tips, handle: brown (139,90,43) 4px wide 22px long, handle wrap: dark brown (90,55,28) diagonal lines, 2-3 yellow (255,223,0) star particles 2px each around head showing power, chunky pixel style 6-8px per block, brutal heavy weapon, transparent background, FC/NES aesthetic, sharp edges, no anti-aliasing",
        "negative": "blurry, smooth, realistic, 3D, modern, detailed, anti-aliased, photorealistic, complex",
        "size": "48x48",
        "filename": "fabao_suixingchu.png"
    },
}

# 生成完整配置
def generate_all_configs():
    """生成所有图标配置"""
    configs = {
        "fabao": FABAO_PROMPTS,
        # TODO: 添加饰品和灵根配置
    }
    
    # 保存配置
    output_dir = "f:/游戏/scripts/icon_configs"
    os.makedirs(output_dir, exist_ok=True)
    
    for category, prompts in configs.items():
        output_path = f"{output_dir}/{category}_config.json"
        
        config = {
            "model": "pixel-art-xl",
            "batch_size": 1,
            "num_images": 1,
            "steps": 25,
            "cfg_scale": 8,
            "sampler": "Euler a",
            "seed": -1,
            "output_dir": f"f:/游戏/assets/icons/{category}",
            "prompts": []
        }
        
        for name, prompt_data in prompts.items():
            config["prompts"].append({
                "name": name,
                "positive": prompt_data["positive"],
                "negative": prompt_data["negative"],
                "width": int(prompt_data["size"].split('x')[0]),
                "height": int(prompt_data["size"].split('x')[1]),
                "filename": prompt_data["filename"]
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] Generated: {output_path} ({len(prompts)} icons)")
    
    print(f"\n[DONE] Total configs generated: {len(configs)}")
    print(f"[INFO] Total icons: {sum(len(p) for p in configs.values())}")

if __name__ == "__main__":
    generate_all_configs()
