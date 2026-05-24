"""
IntelliJudge — Password Hashing Utilities

WHY BCRYPT?
  - One-way: you cannot reverse a hash back to the password
  - Salted: each hash is unique even for the same password (prevents rainbow tables)
  - Slow by design: bcrypt is intentionally slow, making brute-force attacks expensive
  - Industry standard: used by GitHub, Dropbox, and most major platforms

HOW IT WORKS:
  hash_password("mypassword")
    → "$2b$12$..." (a 60-char bcrypt hash stored in the database)

  verify_password("mypassword", "$2b$12$...")
    → True  (bcrypt re-hashes and compares internally)

  verify_password("wrongpassword", "$2b$12$...")
    → False
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    The result is a 60-character string safe to store in the database.
    Never store the original password — only this hash.
    """
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check whether a plain text password matches a stored bcrypt hash.

    Returns True if they match, False otherwise.
    Use this during login — never compare plain passwords directly.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
