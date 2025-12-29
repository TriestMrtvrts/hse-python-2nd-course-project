import re

COMMON_PASSWORDS = {
    "123456",
    "password",
    "qwerty",
    "12345678",
    "111111",
    "abc123",
    "123123",
}

def validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValueError("Пароль должен быть не короче 8 символов")

    if password.lower() in COMMON_PASSWORDS:
        raise ValueError("Пароль слишком простой")

    if not re.search(r"[a-zA-Z]", password):
        raise ValueError("Пароль должен содержать буквы")

    if not re.search(r"\d", password):
        raise ValueError("Пароль должен содержать цифры")