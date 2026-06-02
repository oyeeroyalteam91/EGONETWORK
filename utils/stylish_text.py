from __future__ import annotations


def _bold_char(char: str) -> str:
    if "A" <= char <= "Z":
        return chr(ord(char) - ord("A") + 0x1D400)
    if "a" <= char <= "z":
        return chr(ord(char) - ord("a") + 0x1D41A)
    if "0" <= char <= "9":
        return chr(ord(char) - ord("0") + 0x1D7CE)
    return char


def convert_to_stylish_text(text: str) -> str:
    return "".join(_bold_char(char) for char in text)


def s(text: str) -> str:
    return convert_to_stylish_text(text)


def plain(text: str) -> str:
    return text
