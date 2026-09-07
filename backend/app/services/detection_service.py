"""AIGC 图片识别服务 - 检测图片是否为AI生成"""
import io
import hashlib
import json
import numpy as np
from PIL import Image, ImageFilter
from datetime import datetime


async def detect_aigc_image(image_bytes: bytes) -> dict:
    """
    分析图片是否为 AI 生成

    检测维度:
    1. 频域能量分析 (FFT) - AI图片高频细节分布异常
    2. 噪声模式分析 - AI图片噪声过于均匀
    3. 色彩分布分析 - AI图片色彩分布偏理想化
    4. 边缘锐度分析 - AI图片边缘过于清晰或过于模糊
    5. 纹理复杂度分析 - AI图片纹理过于规律
    6. 伪影检测 - AI图片特有的生成伪影

    返回:
        dict: {
            "is_aigc": bool,           # 是否为AI生成
            "confidence": float,       # 置信度 0-100
            "label": str,              # 标签: AI生成/人工拍摄/不确定
            "indicators": list,        # 6项指标详情
            "image_hash": str,         # 图片哈希
            "details": str,            # 详细分析
        }
    """
    # 打开图片
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")

    # 计算图片哈希
    image_hash = hashlib.sha256(image_bytes).hexdigest()

    # 缩放图片到统一尺寸（加速分析）
    if img.size[0] > 512 or img.size[1] > 512:
        img = img.resize((512, 512), Image.LANCZOS)

    # 转numpy数组
    arr = np.array(img)

    # ===== 1. 频域能量分析 (FFT) =====
    freq_score = _analyze_frequency(arr)

    # ===== 2. 噪声模式分析 (拉普拉斯方差) =====
    noise_score = _analyze_noise(arr)

    # ===== 3. 色彩分布分析 =====
    color_score = _analyze_color_distribution(arr)

    # ===== 4. 边缘锐度分析 =====
    edge_score = _analyze_edge_sharpness(arr)

    # ===== 5. 纹理复杂度分析 =====
    texture_score = _analyze_texture(arr)

    # ===== 6. 伪影检测 =====
    artifact_score = _analyze_artifacts(arr)

    # ===== 综合评分 =====
    scores = [freq_score, noise_score, color_score, edge_score, texture_score, artifact_score]
    avg_score = sum(scores) / len(scores)

    # 置信度 (越高越可能是AI生成)
    confidence = round(avg_score, 1)

    # 判定
    if confidence >= 65:
        is_aigc = True
        label = "AI 生成"
    elif confidence <= 35:
        is_aigc = False
        label = "人工拍摄"
    else:
        is_aigc = confidence >= 50
        label = "AI 生成" if is_aigc else "人工拍摄"

    # 指标列表
    indicators = [
        {"name": "频域能量", "score": round(freq_score, 1), "desc": _score_desc(freq_score, "高频能量分布异常，疑似AI生成")},
        {"name": "噪声模式", "score": round(noise_score, 1), "desc": _score_desc(noise_score, "噪声分布过于均匀，疑似AI生成")},
        {"name": "色彩分布", "score": round(color_score, 1), "desc": _score_desc(color_score, "色彩分布偏理想化，疑似AI生成")},
        {"name": "边缘锐度", "score": round(edge_score, 1), "desc": _score_desc(edge_score, "边缘特征异常，疑似AI生成")},
        {"name": "纹理复杂度", "score": round(texture_score, 1), "desc": _score_desc(texture_score, "纹理过于规律，疑似AI生成")},
        {"name": "伪影检测", "score": round(artifact_score, 1), "desc": _score_desc(artifact_score, "检测到AI生成伪影")},
    ]

    # 详细说明
    details = _build_details(confidence, label, indicators, img.size)

    return {
        "is_aigc": is_aigc,
        "confidence": confidence,
        "label": label,
        "indicators": indicators,
        "image_hash": image_hash,
        "image_size": f"{img.size[0]}x{img.size[1]}",
        "details": details,
        "detected_at": datetime.now().isoformat(),
    }


def _analyze_frequency(arr: np.ndarray) -> float:
    """频域能量分析 - FFT高频能量占比"""
    gray = np.mean(arr, axis=2)
    # 二维FFT
    fft = np.fft.fft2(gray)
    fft_shift = np.fft.fftshift(fft)
    magnitude = np.abs(fft_shift)

    # 总能量
    total_energy = magnitude.sum()
    if total_energy == 0:
        return 50.0

    # 高频区域能量（中心以外）
    h, w = magnitude.shape
    center_h, center_w = h // 2, w // 2
    radius = min(h, w) // 8

    y, x = np.ogrid[:h, :w]
    dist = np.sqrt((y - center_h) ** 2 + (x - center_w) ** 2)
    high_freq_mask = dist > radius
    high_freq_energy = magnitude[high_freq_mask].sum()
    high_freq_ratio = float(high_freq_energy / total_energy)

    # AI图片通常高频能量占比偏低（过度平滑）或偏高（过度细节）
    if high_freq_ratio < 0.3:
        score = 30 + (0.3 - high_freq_ratio) * 200
    elif high_freq_ratio > 0.7:
        score = 70 + (high_freq_ratio - 0.7) * 100
    else:
        score = 50 + (high_freq_ratio - 0.5) * 50

    return min(max(score, 0), 100)


def _analyze_noise(arr: np.ndarray) -> float:
    """噪声模式分析 - 拉普拉斯方差（纯numpy实现）"""
    gray = np.mean(arr, axis=2).astype(np.float64)

    # 拉普拉斯卷积（手动实现，不依赖scipy）
    kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
    h, w = gray.shape
    laplacian = np.zeros_like(gray)

    # 简化版拉普拉斯（只取中心区域计算加速）
    lap = (gray[2:, 1:-1] + gray[:-2, 1:-1] + gray[1:-1, 2:] + gray[1:-1, :-2] - 4 * gray[1:-1, 1:-1])
    laplacian[1:-1, 1:-1] = lap

    # 方差
    var = float(laplacian.var())

    # 真实照片噪声方差通常在 5-50 之间
    # AI图片噪声方差通常偏低（<5）或偏高（>50）
    if var < 5:
        score = 80 + (5 - var) * 4
    elif var > 50:
        score = 60 + min((var - 50) * 0.5, 30)
    elif 10 <= var <= 30:
        score = 30
    else:
        score = 50

    return min(max(score, 0), 100)


def _analyze_color_distribution(arr: np.ndarray) -> float:
    """色彩分布分析"""
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    r_mean, g_mean, b_mean = float(r.mean()), float(g.mean()), float(b.mean())
    r_std, g_std, b_std = float(r.std()), float(g.std()), float(b.std())

    # 色彩饱和度
    max_rgb = np.maximum(np.maximum(arr[:, :, 0], arr[:, :, 1]), arr[:, :, 2]).astype(np.float64)
    min_rgb = np.minimum(np.minimum(arr[:, :, 0], arr[:, :, 1]), arr[:, :, 2]).astype(np.float64)
    saturation = float(np.mean((max_rgb - min_rgb) / (max_rgb + 1e-6)))

    # 色彩丰富度
    unique_colors = len(np.unique(arr.reshape(-1, 3), axis=0))
    total_pixels = arr.shape[0] * arr.shape[1]
    color_richness = unique_colors / total_pixels

    score = 50.0
    if saturation > 0.5:
        score += 15
    if color_richness < 0.1:
        score += 20
    elif color_richness > 0.5:
        score -= 10

    if abs(r_mean - g_mean) < 10 and abs(g_mean - b_mean) < 10:
        score += 5

    return min(max(score, 0), 100)


def _analyze_edge_sharpness(arr: np.ndarray) -> float:
    """边缘锐度分析（纯numpy Sobel实现）"""
    gray = np.mean(arr, axis=2).astype(np.float64)

    # Sobel算子（手动实现）
    # Sobel X: [-1,0,1; -2,0,2; -1,0,1]
    sx = (gray[2:, 2:] + 2 * gray[1:-1, 2:] + gray[:-2, 2:] -
          gray[2:, :-2] - 2 * gray[1:-1, :-2] - gray[:-2, :-2])
    # Sobel Y: [-1,-2,-1; 0,0,0; 1,2,1]
    sy = (gray[2:, 2:] + 2 * gray[2:, 1:-1] + gray[2:, :-2] -
          gray[:-2, 2:] - 2 * gray[:-2, 1:-1] - gray[:-2, :-2])

    edge_magnitude = np.sqrt(sx ** 2 + sy ** 2)
    avg_edge = float(edge_magnitude.mean())
    edge_var = float(edge_magnitude.var())

    score = 50.0
    if avg_edge > 30:
        score += 20
    elif avg_edge < 5:
        score += 15

    if edge_var > 500:
        score += 15

    return min(max(score, 0), 100)


def _analyze_texture(arr: np.ndarray) -> float:
    """纹理复杂度分析（纯numpy实现）"""
    gray = np.mean(arr, axis=2).astype(np.float64)
    h, w = gray.shape

    # 局部方差（用滑动窗口均值近似）
    k = 8
    # 简化：采样计算
    local_vars = []
    for i in range(0, h - k, k):
        for j in range(0, w - k, k):
            block = gray[i:i + k, j:j + k]
            local_vars.append(float(block.var()))

    local_vars = np.array(local_vars)
    avg_local_var = float(local_vars.mean())
    std_local_var = float(local_vars.std())

    score = 50.0
    if std_local_var < 5:
        score += 25
    elif avg_local_var > 100:
        score += 15

    uniformity = 1 - (std_local_var / (avg_local_var + 1e-6))
    if uniformity > 0.8:
        score += 10

    return min(max(score, 0), 100)


def _analyze_artifacts(arr: np.ndarray) -> float:
    """伪影检测"""
    gray = np.mean(arr, axis=2)
    h, w = gray.shape

    score = 40.0

    # 1. 检测块状伪影
    block_size = 8
    blocks = []
    for i in range(0, h - block_size, block_size):
        for j in range(0, w - block_size, block_size):
            block = gray[i:i + block_size, j:j + block_size]
            blocks.append(float(block.mean()))

    block_arr = np.array(blocks)
    block_var = float(block_arr.var())
    if block_var < 5:
        score += 20

    # 2. 检测色彩突变
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    color_diff = np.abs(r.astype(int) - g.astype(int)) + np.abs(g.astype(int) - b.astype(int))
    sudden_changes = float(np.sum(color_diff > 100)) / (h * w)
    if sudden_changes < 0.01:
        score += 15

    # 3. 检测重复模式
    q1 = gray[:h // 4, :w // 4]
    q4 = gray[h // 2:, w // 2:]
    if q1.shape == q4.shape:
        q1_flat = q1.flatten().astype(np.float64)
        q4_flat = q4.flatten().astype(np.float64)
        if q1_flat.std() > 0 and q4_flat.std() > 0:
            correlation = float(np.corrcoef(q1_flat, q4_flat)[0, 1])
            if not np.isnan(correlation) and correlation > 0.7:
                score += 15

    return min(max(score, 0), 100)


def _score_desc(score: float, desc: str) -> str:
    """根据分数生成描述"""
    if score >= 65:
        return desc
    elif score <= 35:
        return "特征正常，疑似真实照片"
    else:
        return "特征介于AI生成和真实照片之间，难以确定"


def _build_details(confidence: float, label: str, indicators: list, size: tuple) -> str:
    """构建详细分析文本"""
    lines = []
    lines.append(f"图片尺寸: {size[0]}x{size[1]}")
    lines.append(f"综合判定: {label}")
    lines.append(f"置信度: {confidence}%")
    lines.append("")
    lines.append("各维度分析:")
    for ind in indicators:
        lines.append(f"  - {ind['name']}: {ind['score']}分 - {ind['desc']}")
    lines.append("")
    if confidence >= 65:
        lines.append("结论: 该图片高度疑似AI生成内容，建议标记为AIGC内容。")
    elif confidence <= 35:
        lines.append("结论: 该图片特征符合真实拍摄照片，AI生成可能性较低。")
    else:
        lines.append("结论: 该图片部分特征介于AI生成和真实拍摄之间，建议人工复核。")

    return "\n".join(lines)
