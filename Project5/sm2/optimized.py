import gmpy2
from .basic import SM2Basic


class SM2Optimized(SM2Basic):
    def __init__(self, priv_key=None, pub_key=None):
        super().__init__(priv_key, pub_key)
        # 预计算固定点乘法表
        self._precompute_table()

    def _precompute_table(self):
        """预计算窗口乘法表（4-bit窗口）"""
        self.window_table = []
        P = SM2_CURVE.generator
        for i in range(16):
            self.window_table.append(P)
            P = SM2_CURVE.add_point(P, P)

    def _window_mul(self, k, window_size=4):
        """窗口法优化点乘"""
        q = SM2_CURVE.infinity
        k_bin = bin(k)[2:]
        chunks = [k_bin[i:i + window_size] for i in range(0, len(k_bin), window_size)]

        for i, chunk in enumerate(chunks):
            q = SM2_CURVE.add_point(q, q)  # 加倍
            if chunk:
                idx = int(chunk, 2)
                if idx > 0:
                    q = SM2_CURVE.add_point(q, self.window_table[idx - 1])
        return q

    def sign(self, msg, k=None):
        """优化后的签名（使用gmpy2加速大数运算）"""
        e = int.from_bytes(self.hash_msg(msg), 'big')
        d = self.priv_key

        while True:
            k = k or secrets.randbelow(SM2_CURVE.order - 1) + 1
            x1, _ = self._window_mul(k)
            r = gmpy2.f_mod(e + x1, SM2_CURVE.order)
            if r == 0 or r + k == SM2_CURVE.order:
                continue

            s = gmpy2.f_mod(
                gmpy2.mul(
                    gmpy2.invert(1 + d, SM2_CURVE.order),
                    (k - r * d)
                ),
                SM2_CURVE.order
            )
            if s != 0:
                return (int(r), int(s))