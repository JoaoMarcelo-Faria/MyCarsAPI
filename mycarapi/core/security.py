from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, encripted_password: str) -> bool:
    return pwd_context.verify(plain_password, encripted_password)
