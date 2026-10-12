"""AES experiments with PyCryptodome.

Install: pip install pycryptodome
Run:     python aes_lab.py
"""
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


def encrypt_decrypt_demo(message: bytes, key_size: int = 16):
    key = get_random_bytes(key_size)
    cipher = AES.new(key, AES.MODE_CBC)
    ct = cipher.encrypt(pad(message, AES.block_size))
    iv = cipher.iv
    pt = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), AES.block_size)
    return key, iv, ct, pt


def key_size_experiment():
    print("=== Experiment 1: key sizes ===")
    message = b"Meet me at the library at 5pm"
    for size in (16, 24, 32):
        key, iv, ct, pt = encrypt_decrypt_demo(message, size)
        print(f"AES-{size * 8}")
        print("  Key (hex):       ", key.hex())
        print("  IV (hex):        ", iv.hex())
        print("  Ciphertext (hex):", ct.hex())
        print("  Ciphertext bytes:", len(ct))
        print("  Decrypted OK:    ", pt == message)
    print()


def message_length_experiment():
    print("=== Experiment 2: message length vs ciphertext length ===")
    for n in (5, 15, 16, 17, 32, 100, 1000):
        key = get_random_bytes(16)
        ct = AES.new(key, AES.MODE_CBC).encrypt(pad(b"A" * n, AES.block_size))
        print(f"  Plaintext {n:>4} bytes -> Ciphertext {len(ct):>4} bytes")
    print()


def ecb_vs_cbc_experiment():
    print("=== Experiment 3: ECB vs CBC ===")
    key = get_random_bytes(16)
    msg = b"A" * 32  # two identical 16 byte blocks
    ecb = AES.new(key, AES.MODE_ECB).encrypt(msg)
    cbc = AES.new(key, AES.MODE_CBC).encrypt(msg)
    print("  ECB block 1:", ecb[:16].hex())
    print("  ECB block 2:", ecb[16:].hex(), "(identical, pattern leaks)")
    print("  CBC block 1:", cbc[:16].hex())
    print("  CBC block 2:", cbc[16:].hex(), "(different, pattern hidden)")
    print()


if __name__ == "__main__":
    key_size_experiment()
    message_length_experiment()
    ecb_vs_cbc_experiment()
