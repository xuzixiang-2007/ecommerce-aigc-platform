"""AIGC 生成服务 - 生成商品图"""
import httpx
import json
import hashlib
import io
import time
import asyncio
from PIL import Image
import imagehash
from app.config import settings


async def generate_product_image(product_name: str, category: str, prompt: str = None) -> dict:
    """
    生成商品图

    返回:
        dict: {
            "image_bytes": bytes,    # 图片二进制数据
            "image_hash": str,      # SHA-256 哈希
            "phash": str,           # 感知哈希
            "model_version": str,   # 模型版本
            "params": str,          # 生成参数 JSON
        }
    """
    # 自动生成提示词
    if not prompt:
        prompt = _build_prompt(product_name, category)

    provider = settings.AIGC_PROVIDER.lower()

    if provider == "mock":
        return await _generate_mock(product_name, category, prompt)
    elif provider == "wanx":
        return await _generate_wanx(product_name, category, prompt)
    elif provider == "stability":
        return await _generate_stability(prompt)
    else:
        return await _generate_mock(product_name, category, prompt)


def _build_prompt(product_name: str, category: str) -> str:
    """根据商品信息自动构建中文提示词（通义万相支持中文）"""
    return (
        f"专业商品摄影，{product_name}，{category}类别，"
        f"白色背景，影棚灯光，高分辨率，锐利对焦，商业级品质，"
        f"居中构图，无文字"
    )


async def _generate_mock(product_name: str, category: str, prompt: str) -> dict:
    """模拟生成（不需要 GPU，先用占位图演示流程）"""
    # 生成一张占位图片：白色背景 + 商品名文字
    img = Image.new("RGB", (512, 512), color=(255, 255, 255))

    # 用 PIL 在图片上写商品名
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
    draw.text((100, 240), product_name, fill=(50, 50, 50), font=font)
    draw.text((100, 280), f"[{category}]", fill=(150, 150, 150), font=font)
    draw.text((100, 320), "AIGC Generated", fill=(200, 200, 200), font=font)

    # 转二进制
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    image_bytes = buf.getvalue()

    # 计算哈希
    image_hash = hashlib.sha256(image_bytes).hexdigest()
    phash = str(imagehash.phash(img))

    return {
        "image_bytes": image_bytes,
        "image_hash": image_hash,
        "phash": phash,
        "model_version": "mock-v1.0",
        "params": json.dumps({"prompt": prompt, "size": "512x512"}, ensure_ascii=False),
    }


async def _generate_wanx(product_name: str, category: str, prompt: str) -> dict:
    """
    调用通义万相（DashScope）API 生成商品图

    流程：创建任务 → 轮询任务状态 → 下载图片
    API文档：https://help.aliyun.com/zh/model-studio/text-to-image-api-reference
    """
    api_key = settings.DASHSCOPE_API_KEY
    if not api_key:
        raise ValueError("未配置 DASHSCOPE_API_KEY，请在 .env 文件中设置")

    base_url = "https://dashscope.aliyuncs.com/api/v1"

    # 步骤1：创建任务
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }
    payload = {
        "model": "wanx-v1",
        "input": {
            "prompt": prompt,
        },
        "parameters": {
            "style": "<auto>",
            "size": "1024*1024",
            "n": 1,
        },
    }

    async with httpx.AsyncClient(timeout=60) as client:
        # 创建任务
        resp = await client.post(
            f"{base_url}/services/aigc/text2image/image-synthesis",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

        task_id = data["output"]["task_id"]

        # 步骤2：轮询任务状态（最多等待60秒）
        max_retries = 30
        for i in range(max_retries):
            await asyncio.sleep(2)  # 每2秒查询一次

            poll_resp = await client.get(
                f"{base_url}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            poll_resp.raise_for_status()
            poll_data = poll_resp.json()

            status = poll_data["output"]["task_status"]

            if status == "SUCCEEDED":
                # 成功，获取图片URL
                results = poll_data["output"]["results"]
                if not results:
                    raise ValueError("任务成功但未返回图片")
                image_url = results[0]["url"]

                # 步骤3：下载图片
                img_resp = await client.get(image_url)
                img_resp.raise_for_status()
                image_bytes = img_resp.content

                # 计算哈希
                img = Image.open(io.BytesIO(image_bytes))
                image_hash = hashlib.sha256(image_bytes).hexdigest()
                phash = str(imagehash.phash(img))

                return {
                    "image_bytes": image_bytes,
                    "image_hash": image_hash,
                    "phash": phash,
                    "model_version": "wanx-v1",
                    "params": json.dumps(
                        {"prompt": prompt, "size": "1024x1024", "style": "<auto>"},
                        ensure_ascii=False,
                    ),
                }

            elif status == "FAILED":
                error_msg = poll_data["output"].get("message", "生成失败")
                raise ValueError(f"通义万相生成失败：{error_msg}")

            # PENDING 或 RUNNING，继续等待

        # 超时
        raise TimeoutError("通义万相生成超时，请稍后重试")


async def _generate_stability(prompt: str) -> dict:
    """调用 Stability AI API 生成（需要 API Key）"""
    headers = {
        "Authorization": f"Bearer {settings.STABILITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    # 解析返回的图片
    import base64
    image_b64 = data["artifacts"][0]["base64"]
    image_bytes = base64.b64decode(image_b64)
    img = Image.open(io.BytesIO(image_bytes))

    image_hash = hashlib.sha256(image_bytes).hexdigest()
    phash = str(imagehash.phash(img))

    return {
        "image_bytes": image_bytes,
        "image_hash": image_hash,
        "phash": phash,
        "model_version": "stable-diffusion-v1.6",
        "params": json.dumps({"prompt": prompt, "size": "512x512"}, ensure_ascii=False),
    }
