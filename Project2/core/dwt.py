import cv2
import numpy as np


class DWTWatermark:
    def __init__(self, scale=0.1):
        self.scale = scale  # 水印强度系数

    def embed(self, host_img, watermark):
        """嵌入水印"""
        # 转换为YUV颜色空间
        img_yuv = cv2.cvtColor(host_img, cv2.COLOR_BGR2YUV)
        # 对Y通道进行DWT
        coeffs = self._dwt2(img_yuv[:, :, 0])

        # 在HL和LH子带嵌入水印
        watermark = cv2.resize(watermark, (coeffs[1][0].shape[1], coeffs[1][0].shape[0]))
        for i in [0, 1]:  # HL和LH子带
            coeffs[1][i] += self.scale * watermark * 255

        # 逆变换
        img_yuv[:, :, 0] = self._idwt2(coeffs)
        return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

    def extract(self, watermarked_img, orig_size):
        """提取水印"""
        img_yuv = cv2.cvtColor(watermarked_img, cv2.COLOR_BGR2YUV)
        coeffs = self._dwt2(img_yuv[:, :, 0])

        # 从子带中提取水印
        watermark = np.zeros_like(coeffs[1][0])
        for i in [0, 1]:
            watermark += coeffs[1][i] / (2 * self.scale * 255)

        return cv2.resize(watermark, orig_size)

    def _dwt2(self, img):
        """二维离散小波变换"""
        return pywt.dwt2(img, 'haar')

    def _idwt2(self, coeffs):
        """逆变换"""
        return pywt.idwt2(coeffs, 'haar')