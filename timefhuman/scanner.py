import re


__all__ = ("MERIDIEM_PATTERN", "TOKEN_PATTERN", "first_token", "iter_tokens", "tokenize")


MERIDIEM_PATTERN = r"(?:[ap](?:\.?m\.?)?)"
TOKEN_PATTERN = re.compile(
    rf"(?iu)\d+(?:[/:.-]\d+)*(?:st|nd|rd|th)?(?:{MERIDIEM_PATTERN})?|[^\W\d_]+(?:\.[^\W\d_]+\.?)?|\S"
)

def tokenize(text: str):
    return [(value := match.group(0), value.lower(), match.start(), match.end()) for match in TOKEN_PATTERN.finditer(text)]


def iter_tokens(text: str, start_pos: int = 0, end_pos: int | None = None):
    if end_pos is None:
        for match in TOKEN_PATTERN.finditer(text, start_pos):
            value = match.group(0)
            yield (value, value.lower(), match.start(), match.end())
        return
    for match in TOKEN_PATTERN.finditer(text, start_pos, end_pos):
        value = match.group(0)
        yield (value, value.lower(), match.start(), match.end())


def first_token(text: str):
    match = TOKEN_PATTERN.match(text)
    if match is None:
        return None
    value = match.group(0)
    return (value, value.lower(), match.start(), match.end())
