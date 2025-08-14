import unittest
from Project1.sm4_basic.sm4 import SM4 as BasicSM4
from Project1.sm4_ttable.sm4_ttable import SM4_TTable
from Project1.sm4_gcm.sm4_gcm import SM4_GCM


class TestSM4(unittest.TestCase):
    def setUp(self):
        self.key = bytes.fromhex('0123456789abcdeffedcba9876543210')
        self.plaintext = bytes.fromhex('0123456789abcdeffedcba9876543210')
        self.expected_cipher = bytes.fromhex('681edf34d206965e86b3e94f536e4246')

    def test_basic_encrypt(self):
        sm4 = BasicSM4(self.key)
        cipher = sm4.encrypt_block(self.plaintext)
        self.assertEqual(cipher, self.expected_cipher)

    def test_ttable_encrypt(self):
        sm4 = SM4_TTable(self.key)
        cipher = sm4.encrypt_block(self.plaintext)
        self.assertEqual(cipher, self.expected_cipher)

    def test_gcm_mode(self):
        sm4 = SM4_GCM(self.key)
        nonce, ciphertext, tag = sm4.encrypt(self.plaintext)
        plaintext = sm4.decrypt(nonce, ciphertext, tag)
        self.assertEqual(plaintext, self.plaintext)


if __name__ == '__main__':
    unittest.main()