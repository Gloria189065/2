from sm2.basic import SM2Basic
import hashlib


def forge_satoshi_signature():
    """伪造类似比特币的签名（演示原理）"""
    # 中本聪公钥（示例）
    satoshi_pub = (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
                   0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5)

    # 要伪造的消息
    target_msg = "I am Satoshi Nakamoto"

    # 构造伪造签名（基于SM2特性）
    e = int.from_bytes(hashlib.sha256(target_msg.encode()).digest(), 'big')
    r = e % SM2_CURVE.order
    s = (r * pow(1 - r, -1, SM2_CURVE.order)) % SM2_CURVE.order

    print(f"Forged signature (r, s): ({hex(r)}, {hex(s)})")

    # 验证伪造签名
    verifier = SM2Basic(pub_key=satoshi_pub)
    print("Verification result:", verifier.verify(target_msg, (r, s)))