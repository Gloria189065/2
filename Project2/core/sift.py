import cv2
import numpy as np
from skimage.feature import match_descriptors
from skimage.measure import ransac
from skimage.transform import SimilarityTransform


class SIFTWatermark:
    def __init__(self, n_features=500):
        self.sift = cv2.SIFT_create(n_features)
        self.bf = cv2.BFMatcher(cv2.NORM_L2)

    def embed(self, host_img, watermark, scale=0.03):
        """
        基于SIFT特征点的水印嵌入
        :param host_img: 宿主图像(BGR)
        :param watermark: 二值水印图像(0-255)
        :param scale: 水印强度系数
        :return: 含水印图像
        """
        # 转换为YUV空间并在Y通道操作
        img_yuv = cv2.cvtColor(host_img, cv2.COLOR_BGR2YUV)
        kp, des = self.sift.detectAndCompute(img_yuv[:, :, 0], None)

        # 在特征点位置嵌入水印
        watermark = cv2.resize(watermark, (host_img.shape[1], host_img.shape[0]))
        for p in kp:
            x, y = map(int, p.pt)
            radius = int(p.size * 0.2)  # 根据特征点尺度确定嵌入区域大小
            if radius < 3:
                radius = 3

            # 在特征点周围圆形区域嵌入
            mask = np.zeros_like(img_yuv[:, :, 0])
            cv2.circle(mask, (x, y), radius, 1, -1)
            img_yuv[:, :, 0] = np.where(mask,
                                        img_yuv[:, :, 0] * (1 - scale) + watermark * scale * 255,
                                        img_yuv[:, :, 0])

        return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR), kp

    def extract(self, watermarked_img, original_kp=None, original_des=None):
        """
        基于特征匹配的水印提取
        :param watermarked_img: 可能遭受攻击的图像
        :param original_kp: 原图特征点(可选)
        :param original_des: 原图描述子(可选)
        :return: 提取的水印图像
        """
        # 检测当前图像特征点
        img_yuv = cv2.cvtColor(watermarked_img, cv2.COLOR_BGR2YUV)
        kp_wm, des_wm = self.sift.detectAndCompute(img_yuv[:, :, 0], None)

        # 如果没有提供原图特征，则直接提取
        if original_kp is None or original_des is None:
            return self._blind_extract(img_yuv[:, :, 0], kp_wm)

        # 特征匹配
        matches = self.bf.knnMatch(original_des, des_wm, k=2)
        good = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good.append(m)

        # RANSAC几何验证
        src_pts = np.float32([original_kp[m.queryIdx].pt for m in good]).reshape(-1, 2)
        dst_pts = np.float32([kp_wm[m.trainIdx].pt for m in good]).reshape(-1, 2)

        model, inliers = ransac(
            (src_pts, dst_pts),
            SimilarityTransform, min_samples=3,
            residual_threshold=2, max_trials=100
        )

        # 根据匹配结果提取水印
        if model is None:
            return self._blind_extract(img_yuv[:, :, 0], kp_wm)

        # 变换水印区域
        extracted = np.zeros_like(img_yuv[:, :, 0], dtype=np.float32)
        for i, m in enumerate(good):
            if inliers[i]:
                x_src, y_src = src_pts[i]
                x_dst, y_dst = dst_pts[i]
                radius = int(original_kp[m.queryIdx].size * 0.2)

                # 累积水印信号
                patch = img_yuv[int(y_dst) - radius:int(y_dst) + radius,
                        int(x_dst) - radius:int(x_dst) + radius, 0]
                if patch.size > 0:
                    extracted[int(y_src) - radius:int(y_src) + radius,
                    int(x_src) - radius:int(x_src) + radius] += patch

        # 归一化处理
        extracted = cv2.normalize(extracted, None, 0, 255, cv2.NORM_MINMAX)
        return extracted.astype(np.uint8)

    def _blind_extract(self, img, kp):
        """盲提取（无原图特征时使用）"""
        extracted = np.zeros_like(img, dtype=np.float32)
        for p in kp:
            x, y = map(int, p.pt)
            radius = int(p.size * 0.2)
            extracted[y - radius:y + radius, x - radius:x + radius] += \
                img[y - radius:y + radius, x - radius:x + radius]

        extracted = cv2.normalize(extracted, None, 0, 255, cv2.NORM_MINMAX)
        return cv2.threshold(extracted, 127, 255, cv2.THRESH_BINARY)[1]