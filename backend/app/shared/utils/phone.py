import re


def normalize_us_phone(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Phone number must be a string.")

    value = value.strip()
    if not re.fullmatch(r"\+?[0-9\s().-]+", value):
        raise ValueError("Phone number contains unsupported characters.")

    digits = re.sub(r"[^0-9]", "", value)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        raise ValueError("Phone number must contain 10 digits, optionally preceded by +1.")

    return digits