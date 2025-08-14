import hashlib
from .ecc import SM2ECC, SM2_CURVE


class SM2Basic:
    def __init__(self, priv_key=None, pub_key=None):
        if priv_key is None and pub_key is None:
            self.priv_key, self.pub_key = SM2ECC.key_gen()
        else:
            self.priv_key, self.pub_key = priv_key, pub_key

    def hash_msg(self, msg, ZA=None):
        """SM3哈希计算"""
        if ZA is None:
            ZA = self._compute_ZA()

        m = ZA + msg if isinstance(msg, bytes) else ZA + msg.encode()
        return hashlib.sm3(m).digest()

    def _compute_ZA(self):
        """计算ZA（用户身份哈希）"""
        # 简化实现：实际应包含用户ID等
        x, y = self.pub_key
        return (x.to_bytes(32, 'big') + y.to_bytes(32, 'big'))

    def sign(self, msg, k=None):
        """SM2签名"""
        e = int.from_bytes(self.hash_msg(msg), 'big')
        d = self.priv_key

        while True:
            k = k or secrets.randbelow(SM2_CURVE.order - 1) + 1
            x1, _ = SM2ECC.kG(k)
            r = (e + x1) % SM2_CURVE.order
            if r == 0 or r + k == SM2_CURVE.order:
                continue

            s = (SM2ECC.mod_inv(1 + d, SM2_CURVE.order) * (k - r * d)) % SM2_CURVE.order
            if s != 0:
                return (r, s)

    def verify(self, msg, signature):
        """SM2验签"""
        r, s = signature
        if not (0 < r < SM2_CURVE.order and 0 < s < SM2_CURVE.order):
            return False

        e = int.from_bytes(self.hash_msg(msg), 'big')
        t = (r + s) % SM2_CURVE.order
        if t == 0:
            return False

        x1, y1 = SM2ECC.add_points(
            SM2ECC.kG(s),
            SM2_CURVE.mul_point(t, self.pub_key)
        )
        R = (e + x1) % SM2_CURVE.order
        return R == r