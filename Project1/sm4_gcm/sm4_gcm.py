from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives.ciphers.algorithms import SM4
from cryptography.hazmat.backends import default_backend
import os


class SM4_GCM:
    def __init__(self, key):
        self.key = key

    def encrypt(self, plaintext, associated_data=None):
        # 生成随机nonce
        nonce = os.urandom(12)

        # 创建加密器
        cipher = Cipher(
            SM4(self.key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # 关联数据
        if associated_data:
            encryptor.authenticate_additional_data(associated_data)

        # 加密
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return nonce, ciphertext, encryptor.tag

    def decrypt(self, nonce, ciphertext, tag, associated_data=None):
        # 创建解密器
        cipher = Cipher(
            SM4(self.key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # 关联数据
        if associated_data:
            decryptor.authenticate_additional_data(associated_data)

        # 解密
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext