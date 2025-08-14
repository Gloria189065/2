import hashlib
import random
from fastecdsa import curve, keys, point
from phe import paillier  # 需要安装phe库

# 使用NIST P-256椭圆曲线
CURVE = curve.P256
ORDER = CURVE.q
G = CURVE.G  # 生成元


def hash_to_point(s: str) -> point.Point:
    """将字符串哈希到椭圆曲线点（简化版）"""
    h = hashlib.sha256(s.encode()).digest()
    k = int.from_bytes(h, 'big') % ORDER
    return k * G


class Party1:
    """协议中的第一方（持有标识集合）"""

    def __init__(self, identifiers: list):
        self.ids = identifiers
        self.k1 = random.randint(1, ORDER - 1)  # 私钥k1

    def round1(self) -> list:
        """第一轮：发送加密后的标识集合"""
        self.A = [self.k1 * hash_to_point(v) for v in self.ids]
        random.shuffle(self.A)  # 随机重排
        return self.A

    def round3(self, B: list, C: list, pk: paillier.PaillierPublicKey) -> tuple:
        """第三轮：计算交集并返回加密的和与基数"""
        # 计算 B' = B^{k1}
        B_prime = [self.k1 * b for b in B]

        # 使用集合加速交集计算
        A_prime_set = {(p.x, p.y) for p in self.A_prime}
        matched_indices = [j for j, bp in enumerate(B_prime)
                           if (bp.x, bp.y) in A_prime_set]

        # 如果没有交集直接返回
        if not matched_indices:
            return pk.encrypt(0), 0

        # 同态求和（Paillier加法）
        c_sum = C[matched_indices[0]]
        for j in matched_indices[1:]:
            c_sum += C[j]

        return c_sum, len(matched_indices)


class Party2:
    """协议中的第二方（持有标识和关联值）"""

    def __init__(self, pairs: list):
        self.pairs = pairs
        self.k2 = random.randint(1, ORDER - 1)  # 私钥k2
        self.pub_key, self.priv_key = paillier.generate_paillier_keypair()

    def round2(self, A: list) -> tuple:
        """第二轮：发送二次加密标识和关联值密文"""
        # 计算 A' = A^{k2}
        self.A_prime = [self.k2 * a for a in A]

        # 预计算B和C
        B = []
        C = []
        encrypt = self.pub_key.encrypt  # 缓存加密函数

        for w, t in self.pairs:
            B.append(self.k2 * hash_to_point(w))
            C.append(encrypt(t))

        # 随机重排B和C（保持对应关系）
        combined = list(zip(B, C))
        random.shuffle(combined)
        B_shuf, C_shuf = zip(*combined)

        return self.A_prime, list(B_shuf), list(C_shuf)

    def output(self, c_sum: paillier.EncryptedNumber, count: int) -> tuple:
        """解密获得交集和"""
        return count, self.priv_key.decrypt(c_sum)


# 测试协议
if __name__ == "__main__":
    # 测试数据
    P1_ids = ["user1", "user2", "user3"]
    P2_pairs = [("user1", 100), ("user2", 200), ("user4", 300)]

    # 初始化参与方
    p1 = Party1(P1_ids)
    p2 = Party2(P2_pairs)

    # 协议执行流程
    A = p1.round1()  # 第一轮
    A_prime, B, C = p2.round2(A)  # 第二轮
    p1.A_prime = A_prime  # 缓存A'
    c_sum, count = p1.round3(B, C, p2.pub_key)  # 第三轮
    result = p2.output(c_sum, count)  # 输出结果

    print(f"交集大小: {result[0]}, 值和: {result[1]}")
    # 预期输出: 大小=2 (user1,user2), 和=300 (100+200)