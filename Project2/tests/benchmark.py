import time
import cv2
import numpy as np
from core.dwt import DWTWatermark
from core.lsb import LSBWatermark
from core.sift import SIFTWatermark
from attack_test import AttackTester


class PerformanceBenchmark:
    @staticmethod
    def test_all_algorithms(img_path, wm_path, test_rounds=5):
        """测试所有算法的性能和鲁棒性"""
        img = cv2.imread(img_path)
        wm = cv2.imread(wm_path, cv2.IMREAD_GRAYSCALE)

        algorithms = {
            "DWT": DWTWatermark(),
            "LSB": LSBWatermark(),
            "SIFT": SIFTWatermark()
        }

        results = []
        for name, algo in algorithms.items():
            # 性能测试
            time_embed = PerformanceBenchmark._timeit(
                lambda: algo.embed(img, wm) if name != "LSB" else
                algo.embed(Image.fromarray(img), Image.fromarray(wm)),
                test_rounds
            )

            # 内存测试
            mem_usage = PerformanceBenchmark._memory_usage(
                lambda: algo.embed(img.copy(), wm.copy())
            )

            # 鲁棒性测试
            if name == "LSB":
                wm_img = np.array(algo.embed(Image.fromarray(img), Image.fromarray(wm)))
            else:
                wm_img = algo.embed(img, wm)

            robustness = PerformanceBenchmark._test_robustness(wm_img, wm, algo)

            results.append({
                "Algorithm": name,
                "EmbedTime(ms)": f"{time_embed * 1000:.2f}",
                "Memory(MB)": f"{mem_usage:.2f}",
                **robustness
            })

        return results

    @staticmethod
    def _timeit(func, rounds):
        """执行时间测试"""
        times = []
        for _ in range(rounds):
            start = time.perf_counter()
            func()
            times.append(time.perf_counter() - start)
        return np.mean(times)

    @staticmethod
    def _memory_usage(func):
        """内存使用测试"""
        import tracemalloc
        tracemalloc.start()
        func()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return peak / 1024 ** 2  # 转换为MB

    @staticmethod
    def _test_robustness(wm_img, orig_wm, algo):
        """鲁棒性测试"""
        attacks = {
            "Rotation": lambda x: AttackTester.test_rotation(x, 30),
            "Cropping": lambda x: AttackTester.test_crop(x, 0.2),
            "Noise": lambda x: AttackTester.test_noise(x, 25),
            "Contrast": lambda x: AttackTester.test_contrast(x, 1.5),
            "JPEG": lambda x: PerformanceBenchmark._jpeg_compress(x, 70)
        }

        results = {}
        for name, attack in attacks.items():
            attacked = attack(wm_img.copy())

            try:
                if isinstance(algo, LSBWatermark):
                    extracted = algo.extract(Image.fromarray(attacked), orig_wm.shape)
                    extracted = np.array(extracted)
                else:
                    extracted = algo.extract(attacked, orig_wm.shape)

                # 计算NC（归一化相关系数）
                nc = cv2.matchTemplate(
                    extracted.astype(np.float32),
                    orig_wm.astype(np.float32),
                    cv2.TM_CCOEFF_NORMED
                )[0][0]
                results[name] = f"{max(0, nc):.2f}"
            except:
                results[name] = "FAIL"

        return results

    @staticmethod
    def _jpeg_compress(img, quality):
        """JPEG压缩模拟"""
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, encimg = cv2.imencode('.jpg', img, encode_param)
        return cv2.imdecode(encimg, 1)


if __name__ == "__main__":
    # 示例测试
    results = PerformanceBenchmark.test_all_algorithms(
        "samples/original/lena.jpg",
        "samples/original/wm_logo.png"
    )

    # 打印结果表格
    from tabulate import tabulate

    print(tabulate(results, headers="keys", tablefmt="github"))