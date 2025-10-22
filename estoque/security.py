import os, hashlib, hmac, base64
ALGO = 'pbkdf2_sha256'
DEFAULT_ITERATIONS = 260000

def _pbkdf2_sha256(password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)

def hash_password(password: str, iterations: int = DEFAULT_ITERATIONS) -> str:
    salt = os.urandom(16)
    dk = _pbkdf2_sha256(password, salt, iterations)
    return f"{ALGO}${iterations}$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(dk).decode()

def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iter_s, b64_salt, b64_hash = stored.split('$', 3)
        if algo != ALGO:
            return False
        iterations = int(iter_s)
        salt = base64.b64decode(b64_salt)
        expected = base64.b64decode(b64_hash)
        dk = _pbkdf2_sha256(password, salt, iterations)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False
    
