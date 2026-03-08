"""
批量生成图标 - Stable Diffusion API 自动化
使用本地 SD WebUI 批量生成所有游戏图标
"""

import argparse
import base64
import json
import os
import time

import requests

# SD WebUI API 地址
API_URL = "http://127.0.0.1:7860"


class IconGenerator:
    """图标生成器"""

    def __init__(self, api_url=API_URL):
        self.api_url = api_url
        self.session = requests.Session()

    def check_api(self):
        """检查 API 是否可用"""
        try:
            response = self.session.get(f"{self.api_url}/sdapi/v1/sd-models")
            if response.status_code == 200:
                models = response.json()
                print(f"[OK] API 连接成功，可用模型数：{len(models)}")
                if models:
                    print(f"[INFO] 当前模型：{models[0].get('title', 'Unknown')}")
                return True
            else:
                print(f"[ERROR] API 返回错误：{response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] 无法连接到 SD WebUI：{e!s}")
            print(f"[INFO] 请确保 SD WebUI 正在运行：{self.api_url}")
            return False

    def generate_image(self, prompt, negative_prompt, width, height, steps=25, cfg_scale=8, sampler="Euler a"):
        """生成单张图片"""
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "sampler_name": sampler,
            "batch_size": 1,
            "n_iter": 1,
            "seed": -1,  # 随机种子
        }

        try:
            response = self.session.post(
                f"{self.api_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=300,  # 5 分钟超时
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"[ERROR] 生成失败：{response.status_code}")
                return None
        except Exception as e:
            print(f"[ERROR] 请求失败：{e!s}")
            return None

    def save_image(self, image_data, output_path):
        """保存图片"""
        try:
            # 解码 base64
            img_bytes = base64.b64decode(image_data)

            # 创建目录
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 保存文件
            with open(output_path, "wb") as f:
                f.write(img_bytes)

            return True
        except Exception as e:
            print(f"[ERROR] 保存失败：{e!s}")
            return False

    def batch_generate(self, config_path, output_dir=None):
        """批量生成图标"""
        # 读取配置
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"[ERROR] 无法读取配置文件：{e!s}")
            return False

        prompts = config.get("prompts", [])
        if not prompts:
            print("[ERROR] 配置文件中没有提示词")
            return False

        # 输出目录
        if output_dir is None:
            output_dir = config.get("output_dir", "output")

        # 生成参数
        steps = config.get("steps", 25)
        cfg_scale = config.get("cfg_scale", 8)
        sampler = config.get("sampler", "Euler a")

        total = len(prompts)
        success = 0
        failed = []

        print(f"\n[INFO] 开始批量生成，共 {total} 个图标")
        print(f"[INFO] 输出目录：{output_dir}")
        print(f"[INFO] 参数：Steps={steps}, CFG={cfg_scale}, Sampler={sampler}")
        print("=" * 60)

        for i, prompt_data in enumerate(prompts, 1):
            name = prompt_data.get("name", f"icon_{i}")
            positive = prompt_data.get("positive", "")
            negative = prompt_data.get("negative", "")
            width = prompt_data.get("width", 48)
            height = prompt_data.get("height", 48)
            filename = prompt_data.get("filename", f"{name}.png")

            print(f"\n[{i}/{total}] 生成：{name}")
            print(f"  尺寸：{width}x{height}")

            # 生成图片
            start_time = time.time()
            result = self.generate_image(positive, negative, width, height, steps, cfg_scale, sampler)

            if result and "images" in result:
                # 保存图片
                output_path = os.path.join(output_dir, filename)
                if self.save_image(result["images"][0], output_path):
                    elapsed = time.time() - start_time
                    print(f"  [OK] 已保存：{output_path}")
                    print(f"  耗时：{elapsed:.1f}秒")
                    success += 1
                else:
                    print("  [FAIL] 保存失败")
                    failed.append(name)
            else:
                print("  [FAIL] 生成失败")
                failed.append(name)

            # 进度
            progress = (i / total) * 100
            print(f"  进度：{progress:.1f}% ({success}/{total} 成功)")

        # 总结
        print("\n" + "=" * 60)
        print("[DONE] 批量生成完成")
        print(f"  成功：{success}/{total}")
        print(f"  失败：{len(failed)}/{total}")

        if failed:
            print("\n失败的图标：")
            for name in failed:
                print(f"  - {name}")

        return success == total


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="批量生成游戏图标")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument(
        "--category", type=str, choices=["fabao", "accessory", "linggen", "all"], default="fabao", help="图标类别"
    )
    parser.add_argument("--output", type=str, help="输出目录")
    parser.add_argument("--api-url", type=str, default=API_URL, help="SD API 地址")

    args = parser.parse_args()

    # 创建生成器
    generator = IconGenerator(args.api_url)

    # 检查 API
    print("检查 SD WebUI API...")
    if not generator.check_api():
        print("\n[ERROR] 无法连接到 SD WebUI")
        print("\n请确保：")
        print("1. SD WebUI 正在运行")
        print("2. 启动时添加了 --api 参数")
        print("3. 访问 http://127.0.0.1:7860 确认 WebUI 可用")
        return False

    # 配置文件路径
    if args.config:
        config_path = args.config
    else:
        if args.category == "all":
            print("\n[INFO] 生成所有类别的图标")
            categories = ["fabao", "accessory", "linggen"]
        else:
            categories = [args.category]

        for category in categories:
            config_path = f"scripts/icon_configs/{category}_config.json"

            if not os.path.exists(config_path):
                print(f"\n[WARNING] 配置文件不存在：{config_path}")
                print(f"[INFO] 跳过 {category}")
                continue

            print(f"\n{'=' * 60}")
            print(f"生成 {category} 图标")
            print(f"{'=' * 60}")

            output_dir = args.output or f"assets/icons/{category}"
            generator.batch_generate(config_path, output_dir)

        return True

    # 单个配置文件
    if not os.path.exists(config_path):
        print(f"[ERROR] 配置文件不存在：{config_path}")
        return False

    return generator.batch_generate(config_path, args.output)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
