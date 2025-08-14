from sm2.basic import SM2Basic


def nonce_reuse_attack():
    """演示随机数重用导致的私钥泄露"""
    # 受害者密钥
    victim = SM2Basic()

    # 固定k值（实际攻击中通过侧信道获取）
    k = 0x1234567890ABCDEF

    # 签名两条不同消息
    msg1 = "Transfer $100 to Alice"
    msg2 = "Transfer $1000 to Attacker"
    r1, s1 = victim.sign(msg1, k)
    r2, s2 = victim.sign(msg2, k)

    # 计算私钥
    e1 = int.from_bytes(victim.hash_msg(msg1), 'big')
    e2 = int.from_bytes(victim.hash_msg(msg2), 'big')

    d = (s2 - s1) * pow(s1 - s2 + r1 - r2, -1, SM2_CURVE.order) % SM2_CURVE.order
    print(f"Recovered private key: {hex(d)}")
    print(f"Actual private key:   {hex(victim.priv_key)}")
    print(f"Attack success: {d == victim.priv_key}")