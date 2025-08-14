import timeit
from sm2.basic import SM2Basic
from sm2.optimized import SM2Optimized


def benchmark():
    # 测试数据
    test_msg = "SM2 performance benchmark" * 50
    iterations = 100

    # 测试基础实现
    basic = SM2Basic()
    basic_time = timeit.timeit(
        lambda: basic.sign(test_msg),
        number=iterations
    )

    # 测试优化实现
    optimized = SM2Optimized()
    optimized_time = timeit.timeit(
        lambda: optimized.sign(test_msg),
        number=iterations
    )

    # 结果输出
    print(f"Basic SM2 - Avg {basic_time / iterations * 1000:.2f}ms per sign")
    print(f"Optimized SM2 - Avg {optimized_time / iterations * 1000:.2f}ms per sign")
    print(f"Speedup: {basic_time / optimized_time:.2f}x")


if __name__ == "__main__":
    benchmark()