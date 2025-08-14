from PIL import Image
import numpy as np


class LSBWatermark:
    @staticmethod
    def embed(host_img, watermark, bits=2):
        """最低有效位嵌入"""
        host = np.array(host_img)
        watermark = np.array(watermark.convert('1'))  # 二值化

        # 确保水印能嵌入
        assert host.shape[0] >= watermark.shape[0]
        assert host.shape[1] >= watermark.shape[1]

        # 在每个通道的LSB嵌入
        for c in range(3):
            channel = host[:, :, c]
            mask = 0xFF << bits  # 清除低位
            channel &= mask
            channel[:watermark.shape[0], :watermark.shape[1]] |= \
                (watermark * (2 ** bits - 1)).astype(np.uint8)

        return Image.fromarray(host)

    @staticmethod
    def extract(watermarked_img, watermark_size, bits=2):
        """从LSB提取"""
        wm_img = np.array(watermarked_img)
        extracted = np.zeros(watermark_size, dtype=np.uint8)

        # 从所有通道提取并平均
        for c in range(3):
            bits_data = (wm_img[:watermark_size[0], :watermark_size[1], c] & (2 ** bits - 1))
            extracted += bits_data

        # 二值化
        extracted = (extracted / 3 > (2 ** bits - 1) / 2).astype(np.uint8) * 255
        return Image.fromarray(extracted)