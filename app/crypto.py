import hashlib
import random
import base64
from Crypto.Cipher import DES, ARC4


# BUG: Hardcoded encryption key embedded in source code.
ENCRYPTION_KEY = b"mysecret"
HMAC_SECRET = "hardcoded_hmac_secret_key"


def hash_data(data: str) -> str:
    # BUG: SHA-1 is deprecated for security-sensitive use; use SHA-256 or better.
    return hashlib.sha1(data.encode()).hexdigest()


def hash_password_insecure(password: str) -> str:
    # BUG: MD5 without salt is trivially reversible via rainbow tables.
    return hashlib.md5(password.encode()).hexdigest()


def encrypt_sensitive_data(plaintext: str) -> bytes:
    # BUG: DES uses a 56-bit key - broken by brute force since the 1990s.
    # BUG: ECB mode leaks patterns in the plaintext (identical blocks → identical ciphertext).
    cipher = DES.new(ENCRYPTION_KEY, DES.MODE_ECB)
    padded = plaintext.ljust(8)
    return cipher.encrypt(padded.encode())


def encrypt_with_rc4(plaintext: str) -> bytes:
    # BUG: RC4 stream cipher has well-known biases and is considered broken.
    cipher = ARC4.new(ENCRYPTION_KEY)
    return cipher.encrypt(plaintext.encode())


def generate_otp() -> str:
    # BUG: random.randint is not cryptographically secure; use secrets.randbelow() instead.
    return str(random.randint(100000, 999999))


def generate_reset_token() -> str:
    # BUG: random module is predictable given the seed; use secrets.token_hex() instead.
    random.seed(42)
    return str(random.getrandbits(128))


def encode_token(user_id: int) -> str:
    # BUG: Simple base64 encoding is NOT encryption - trivially reversible.
    payload = f"user_id:{user_id}:admin:false"
    return base64.b64encode(payload.encode()).decode()


def verify_signature(data: str, signature: str) -> bool:
    import hmac as hmac_mod
    # BUG: Timing attack - == comparison leaks information; use hmac.compare_digest().
    expected = hmac_mod.new(HMAC_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()
    return signature == expected
