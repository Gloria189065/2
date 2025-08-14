from ecpy.curves import Curve
import secrets

# 国密SM2标准曲线参数
SM2_CURVE = Curve(
    name='SM2',
    a=0x787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498,
    b=0x63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A,
    p=0x8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3,
    n=0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7,
    Gx=0x421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D,
    Gy=0x0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2
)


class SM2ECC:
    @staticmethod
    def key_gen():
        """生成SM2密钥对"""
        priv_key = secrets.randbelow(SM2_CURVE.order - 1) + 1
        pub_key = SM2_CURVE.mul_point(priv_key, SM2_CURVE.generator)
        return priv_key, pub_key

    @staticmethod
    def kG(k):
        """计算kG点（用于签名）"""
        return SM2_CURVE.mul_point(k, SM2_CURVE.generator)

    @staticmethod
    def add_points(P, Q):
        """椭圆曲线点加"""
        return SM2_CURVE.add_point(P, Q)

    @staticmethod
    def mod_inv(a, n):
        """模逆运算"""
        return pow(a, -1, n)