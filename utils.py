from typing import Any

import re

def VerifyInvalidPListCharacter(text: str) -> bool:
    # print text
    # text = unicode(text)

    _controlCharPat = re.compile(
        r"[\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f"
        r"\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f]"
    )
    m = _controlCharPat.search(text)

    if m is not None:
        return True
    else:
        return False

def decode(text: Any, encoding: str, *args) -> Any:
    try:
        return text.decode(encoding, *args)
    except AttributeError:
        return text

def encode(text: Any, encoding: str, *args) -> Any:
    try:
        return text.encode(encoding, *args)
    except AttributeError:
        return text
