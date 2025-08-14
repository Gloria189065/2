import cv2
import numpy as np
from core.dwt import DWTWatermark


class AttackTester:
    @staticmethod
    def test_rotation(img, watermark, degrees=30):
        """旋转攻击测试"""
        rows, cols = img.shape[:2]
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), degrees, 1)
        rotated = cv2.warpAffine(img, M, (cols, rows))
        return rotated

    @staticmethod
    def test_crop(img, ratio=0.2):
        """裁剪攻击测试"""
        h, w = img.shape[:2]
        cropped = img[int(h * ratio):h - int(h * ratio),
                  int(w * ratio):w - int(w * ratio)]
        return cv2.resize(cropped, (w, h))

    @staticmethod
    def test_noise(img, sigma=25):
        """高斯噪声测试"""
        noise = np.random.normal(0, sigma, img.shape)
        noisy = np.clip(img + noise, 0, 255).astype(np.uint8)
        return noisy

    @staticmethod
    def test_contrast(img, alpha=1.5):
        """对比度调整测试"""
        return cv2.convertScaleAbs(img, alpha=alpha, beta=0)


def benchmark(original_img, watermarked_img, watermark):
    """鲁棒性测试流水线"""
    attacks = {
        'Rotation': AttackTester.test_rotation,
        'Cropping': AttackTester.test_crop,
        'Gaussian Noise': AttackTester.test_noise,
        'Contrast Change': AttackTester.test_contrast
    }

    dwt = DWTWatermark()
    results = {}

    for name, attack in attacks.items():
        attacked = attack(watermarked_img)
        extracted = dwt.extract(attacked, watermark.shape[:2])

        # 计算相似度（归一化互相关）
        similarity = cv2.matchTemplate(
            watermark.astype(np.float32),
            extracted.astype(np.float32),
            cv2.TM_CCOEFF_NORMED
        )[0][0]

        results[name] = similarity

    return results