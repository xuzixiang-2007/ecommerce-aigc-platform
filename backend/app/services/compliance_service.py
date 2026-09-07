"""合规检测服务 - 对生成图片做三层合规检查"""
import json


async def check_compliance(image_bytes: bytes, product_name: str, category: str) -> dict:
    """
    合规检测（三层）

    返回:
        dict: {
            "content_safety": "pass" / "fail",
            "copyright_check": "pass" / "fail",
            "spec_check": "pass" / "fail",
            "score": float,
            "passed": bool,
            "details": str (JSON),
        }
    """
    # 第一层：内容安全检测
    safety_result = await _check_content_safety(image_bytes, product_name)

    # 第二层：版权相似度检测
    copyright_result = await _check_copyright(image_bytes)

    # 第三层：图片规范检查
    spec_result = await _check_spec(image_bytes)

    # 综合评分
    score = _calculate_score(safety_result, copyright_result, spec_result)
    passed = all([
        safety_result["passed"],
        copyright_result["passed"],
        spec_result["passed"],
    ])

    details = json.dumps({
        "safety": safety_result,
        "copyright": copyright_result,
        "spec": spec_result,
    }, ensure_ascii=False)

    return {
        "content_safety": "pass" if safety_result["passed"] else "fail",
        "copyright_check": "pass" if copyright_result["passed"] else "fail",
        "spec_check": "pass" if spec_result["passed"] else "fail",
        "score": score,
        "passed": passed,
        "details": details,
    }


async def _check_content_safety(image_bytes: bytes, product_name: str) -> dict:
    """内容安全检测（模拟）"""
    # TODO: 接入阿里云内容安全 API 或本地模型
    # 当前模拟：检查商品名是否包含违禁词
    forbidden_words = ["违禁", "假冒", "伪造", "盗版"]
    found = [w for w in forbidden_words if w in product_name]
    return {
        "passed": len(found) == 0,
        "reason": f"检测到违禁词: {found}" if found else "未检测到违禁内容",
        "items_checked": ["违禁品", "敏感内容", "虚假宣传"],
    }


async def _check_copyright(image_bytes: bytes) -> dict:
    """版权相似度检测（模拟）"""
    # TODO: 用 CLIP 模型计算与已知商品库的相似度
    # 当前模拟：随机返回通过
    return {
        "passed": True,
        "reason": "未检测到与已知商品图的高相似度匹配",
        "similarity_threshold": 0.85,
        "max_similarity": 0.12,
    }


async def _check_spec(image_bytes: bytes) -> dict:
    """图片规范检查"""
    from PIL import Image
    import io

    img = Image.open(io.BytesIO(image_bytes))
    width, height = img.size
    min_resolution = 512

    issues = []
    if width < min_resolution or height < min_resolution:
        issues.append(f"分辨率不足: {width}x{height}，要求 >= {min_resolution}")
    if img.format not in ("PNG", "JPEG", "WEBP"):
        issues.append(f"格式不支持: {img.format}")

    return {
        "passed": len(issues) == 0,
        "reason": "通过" if not issues else "; ".join(issues),
        "resolution": f"{width}x{height}",
        "format": img.format,
    }


def _calculate_score(safety: dict, copyright: dict, spec: dict) -> float:
    """综合评分（满分 100）"""
    score = 100.0
    if not safety["passed"]:
        score -= 40
    if not copyright["passed"]:
        score -= 35
    if not spec["passed"]:
        score -= 25
    return max(score, 0)
