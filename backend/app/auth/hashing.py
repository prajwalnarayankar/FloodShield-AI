from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    print("Password value:", password)
    print("Password type:", type(password))
    print("Password length:", len(str(password)))

    return pwd_context.hash(str(password))


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)