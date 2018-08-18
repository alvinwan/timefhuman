import string


def tokenize(characters):
    """Tokenize all characters in the string.

    >>> list(tokenize('7/17/18 3:00 p.m.'))
    ['7/17/18', '3:00', 'p.m.']
    >>> list(tokenize('July 17, 2018 at 3p.m.'))
    ['July', '17', '2018', 'at', '3', 'p.m.']
    >>> list(tokenize('July 17, 2018 3 p.m.'))
    ['July', '17', '2018', '3', 'p.m.']
    >>> list(tokenize('3PM on July 17'))
    ['3', 'PM', 'on', 'July', '17']
    """
    token = ''
    punctuation = ''
    last_type = None
    for character in characters:
        type = get_character_type(character)
        is_different_type = None not in (type, last_type) and type != last_type \
            and 'punctuation' not in (type, last_type)
        is_break_character = character in string.whitespace + ','

        if is_break_character or is_different_type:
            if token:
                yield token
                token = ''
            token = character if is_different_type else ''
            last_type = type
            continue
        token += character
        last_type = type
    yield token


def get_character_type(character):
    """
    >>> get_character_type('a')
    'alpha'
    >>> get_character_type('1')
    'numeric'
    >>> get_character_type('.')
    'punctuation'
    >>> get_character_type(' ')
    """
    if character.isalpha():
        return 'alpha'
    elif character.isnumeric():
        return 'numeric'
    elif character in string.punctuation:
        return 'punctuation'
    return None
