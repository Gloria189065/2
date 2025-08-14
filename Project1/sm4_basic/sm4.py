class SM4:
    # S盒
    SBOX = [
        0xD6, 0x90, 0xE9, 0xFE, 0xCC, 0xE1, 0x3D, 0xB7, 0x16, 0xB6, 0x14, 0xC2, 0x28, 0xFB, 0x2C, 0x05,
        # ... 完整S盒数据
    ]

    # 系统参数FK
    FK = [0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc]

    # 固定参数CK
    CK = [
        0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269,
        # ... 完整CK数据
    ]

    def __init__(self, key):
        self.rk = self.expand_key(key)

    @staticmethod
    def rotate_left(x, n):
        return ((x << n) & 0xFFFFFFFF) | (x >> (32 - n))

    def tau(self, word):
        """S盒变换"""
        return (self.SBOX[word >> 24 & 0xFF] << 24 |
                self.SBOX[word >> 16 & 0xFF] << 16 |
                self.SBOX[word >> 8 & 0xFF] << 8 |
                self.SBOX[word & 0xFF])

    def l(self, word):
        """线性变换L"""
        return (word ^ self.rotate_left(word, 2) ^
                self.rotate_left(word, 10) ^
                self.rotate_left(word, 18) ^
                self.rotate_left(word, 24))

    def l_prime(self, word):
        """密钥扩展线性变换L'"""
        return (word ^ self.rotate_left(word, 13) ^
                self.rotate_left(word, 23))

    def t(self, word):
        """合成变换T"""
        return self.l(self.tau(word))

    def t_prime(self, word):
        """密钥扩展合成变换T'"""
        return self.l_prime(self.tau(word))

    def expand_key(self, key):
        """密钥扩展算法"""
        mk = [0] * 4
        rk = [0] * 32

        # 将密钥转换为4个字
        for i in range(4):
            mk[i] = ((key[4 * i] << 24) | (key[4 * i + 1] << 16) |
                     (key[4 * i + 2] << 8) | key[4 * i + 3])

        # 生成轮密钥
        for i in range(32):
            if i < 4:
                rk[i] = mk[i] ^ self.FK[i]
            else:
                rk[i] = rk[i - 4] ^ self.t_prime(rk[i - 3] ^ rk[i - 2] ^ rk[i - 1] ^ self.CK[i])

        return rk

    def encrypt_block(self, plaintext):
        """加密单个分组(128bit)"""
        x = [0] * 36
        # 将明文转换为4个字
        for i in range(4):
            x[i] = ((plaintext[4 * i] << 24) | (plaintext[4 * i + 1] << 16) |
                    (plaintext[4 * i + 2] << 8) | plaintext[4 * i + 3])

        # 32轮迭代
        for i in range(32):
            x[i + 4] = x[i] ^ self.t(x[i + 1] ^ x[i + 2] ^ x[i + 3] ^ self.rk[i])

        # 反序变换
        ciphertext = bytearray(16)
        for i in range(4):
            ciphertext[4 * i] = (x[35 - i] >> 24) & 0xFF
            ciphertext[4 * i + 1] = (x[35 - i] >> 16) & 0xFF
            ciphertext[4 * i + 2] = (x[35 - i] >> 8) & 0xFF
            ciphertext[4 * i + 3] = x[35 - i] & 0xFF

        return bytes(ciphertext)

    def decrypt_block(self, ciphertext):
        """解密单个分组(128bit)"""
        # SM4解密与加密相同，只是轮密钥逆序使用
        self.rk.reverse()
        result = self.encrypt_block(ciphertext)
        self.rk.reverse()  # 恢复密钥顺序
        return result