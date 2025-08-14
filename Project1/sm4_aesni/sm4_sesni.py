import ctypes
import os
from Project1.sm4_basic.sm4 import SM4 as BasicSM4

# 加载AESNI指令集库
try:
    if os.name == 'nt':
        aesni_lib = ctypes.cdll.LoadLibrary('aesni.dll')
    else:
        aesni_lib = ctypes.cdll.LoadLibrary('libaesni.so')
except:
    aesni_lib = None


class SM4_AESNI(BasicSM4):
    def __init__(self, key):
        super().__init__(key)
        if aesni_lib is None:
            raise RuntimeError("AESNI library not available")

        # 初始化AESNI加密上下文
        self.ctx = ctypes.create_string_buffer(256)
        key_bytes = bytes(key)
        aesni_lib.sm4_set_key(ctypes.byref(self.ctx),
                              ctypes.c_char_p(key_bytes))

    def encrypt_block(self, plaintext):
        """使用AESNI指令集加速的加密"""
        ciphertext = ctypes.create_string_buffer(16)
        aesni_lib.sm4_encrypt(ctypes.byref(self.ctx),
                              ctypes.c_char_p(plaintext),
                              ctypes.byref(ciphertext))
        return bytes(ciphertext)

    def decrypt_block(self, ciphertext):
        """使用AESNI指令集加速的解密"""
        plaintext = ctypes.create_string_buffer(16)
        aesni_lib.sm4_decrypt(ctypes.byref(self.ctx),
                              ctypes.c_char_p(ciphertext),
                              ctypes.byref(plaintext))
        return bytes(plaintext)