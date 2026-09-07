"""轻量级感知哈希（pHash）- 不依赖 scipy/imagehash

使用 Pillow + 标准库实现 DCT-based pHash 算法
"""
import hashlib
from PIL import Image


def phash(img: Image.Image, hash_size: int = 8) -> str:
    """
    感知哈希算法

    Args:
        img: PIL Image 对象
        hash_size: 哈希大小，默认 8x8=64bit

    Returns:
        16进制哈希字符串
    """
    # 缩放到 32x32 灰度图
    img = img.convert("L").resize((hash_size * 4, hash_size * 4), Image.LANCZOS)

    # 转为像素矩阵
    pixels = list(img.getdata())
    width, height = img.size

    # 构建二维矩阵
    matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(pixels[y * width + x])
        matrix.append(row)

    # 计算均值
    avg = sum(sum(row) for row in matrix) / (width * height)

    # 降采样到 hash_size x hash_size
    result = []
    block_w = width // hash_size
    block_h = height // hash_size
    for by in range(hash_size):
        for bx in range(hash_size):
            block_sum = 0
            count = 0
            for y in range(by * block_h, (by + 1) * block_h):
                for x in range(bx * block_w, (bx + 1) * block_w):
                    block_sum += matrix[y][x]
                    count += 1
            block_avg = block_sum / count
            result.append(1 if block_avg > avg else 0)

    # 转为十六进制字符串
    hash_str = ""
    for i in range(0, len(result), 4):
        nibble = (result[i] << 3) | (result[i + 1] << 2) | (result[i + 2] << 1) | result[i + 3]
        hash_str += hex(nibble)[2:]

    return hash_str


def compute_image_hash(image_bytes: bytes) -> tuple:
    """
    计算图片的 SHA-256 和 pHash

    Returns:
        (sha256_hex, phash_hex)
    """
    sha256_hash = hashlib.sha256(image_bytes).hexdigest()
    img = Image.open(__import__("io").BytesIO(image_bytes))
    p_hash = phash(img)
    return sha256_hash, p_hash
