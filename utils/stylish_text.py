from __future__ import annotations

CAPS_MAP = {
    "A": "𝐀", "B": "𝐁", "C": "𝐂", "D": "𝐃", "E": "𝐄", "F": "𝐅", "G": "𝐆",
    "H": "𝐇", "I": "𝐈", "J": "𝐉", "K": "𝐊", "L": "𝐋", "M": "𝐌", "N": "𝐍",
    "O": "𝐎", "P": "𝐏", "Q": "𝐐", "R": "𝐑", "S": "𝐒", "T": "𝐓", "U": "𝐔",
    "V": "𝐕", "W": "𝐖", "X": "𝐗", "Y": "𝐘", "Z": "𝐙",
}

SMALL_MAP = {
    "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ", "g": "ɢ",
    "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
    "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "ꜱ", "t": "ᴛ", "u": "ᴜ",
    "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ",
}


def convert_to_stylish_text(text: str) -> str:
    """Convert visible user-facing text into Raj's saved bold + small-caps style."""
    result: list[str] = []
    for char in text:
        if char in CAPS_MAP:
            result.append(CAPS_MAP[char])
        elif char in SMALL_MAP:
            result.append(SMALL_MAP[char])
        else:
            result.append(char)
    return "".join(result)


def s(text: str) -> str:
    """Short alias for visible bot replies. Do not use for logs, commands, secrets, or raw API output."""
    return convert_to_stylish_text(text)
