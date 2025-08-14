import struct
from Project1.sm4_basic.sm4 import SM4 as BasicSM4


class SM4_TTable(BasicSM4):
    def __init__(self, key):
        super().__init__(key)
        self._prepare_ttable()

    def _prepare_ttable(self):
        """预计算T-table"""
        self.T0 = [0] * 256
        self.T1 = [0] * 256
        self.T2 = [0] * 256
        self.T3 = [0] * 256

        for i in range(256):
            b = self.SBOX[i]
            t = (b ^ (b << 2) ^ (b << 10) ^ (b << 18) ^ (b << 24)) & 0xFFFFFFFF
            self.T0[i] = t
            self.T1[i] = self.rotate_left(t, 8)
            self.T2[i] = self.rotate_left(t, 16)
            self.T3[i] = self.rotate_left(t, 24)

    def t(self, word):
        """使用T-table优化的T变换"""
        return (self.T0[word >> 24 & 0xFF] ^
                self.T1[word >> 16 & 0xFF] ^
                self.T2[word >> 8 & 0xFF] ^
                self.T3[word & 0xFF])

    def encrypt_block(self, plaintext):
        """T-table优化的加密"""
        x = [0] * 36
        # 将明文转换为4个字
        for i in range(4):
            x[i] = struct.unpack('>I', plaintext[4 * i:4 * i + 4])[0]

        # 32轮迭代
        for i in range(32):
            x[i + 4] = x[i] ^ self.t(x[i + 1] ^ x[i + 2] ^ x[i + 3] ^ self.rk[i])

        # 反序变换
        ciphertext = b''
        for i in range(4):
            ciphertext += struct.pack('>I', x[35 - i])

        return ciphertext