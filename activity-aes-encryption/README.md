# AES Encryption Lab

Hands-on AES experiments in Python using PyCryptodome, done for Cryptography and Security Fundamentals (MEng Cyber Security, University of Limerick).

## What it covers

1. Encrypt and decrypt a message with AES in CBC mode (random key, random IV, PKCS7 padding).
2. Compare key sizes: 128, 192 and 256 bit.
3. Compare plaintext length against ciphertext length.
4. Compare ECB and CBC on repeated blocks.

## Run it

```
pip install pycryptodome
python aes_lab.py
```

Works locally or in Google Colab (use `!pip install pycryptodome`).

## Findings

| Experiment | Observation | Why |
|---|---|---|
| Key sizes 16, 24, 32 bytes | Ciphertext length is identical for all three | Key size sets strength and number of rounds (10, 12, 14), not block size |
| Same message, repeated runs | Ciphertext differs every time | Random key and random IV |
| Message length 5 to 1000 bytes | Ciphertext is always a multiple of 16 | AES works on 16 byte blocks, so padding fills the last block |
| Exactly 16 byte message | Ciphertext grows to 32 bytes | Padding always adds at least one byte, so a full padding block is added |
| ECB vs CBC | ECB gives identical ciphertext for identical blocks, CBC does not | ECB encrypts each block independently, CBC chains blocks together |

## Takeaways

- AES is symmetric, so the key must be shared securely.
- The mode of operation matters as much as the algorithm. Avoid ECB.
- The IV is not secret but must be unique per message.
- CBC gives confidentiality only. Modern systems use authenticated modes such as GCM.

## Related

The same AES is used for VPN traffic in IPsec (`encr aes`, `esp-aes`).
