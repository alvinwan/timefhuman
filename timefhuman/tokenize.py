import string


def tokenize(characters):
    """Tokenize all characters in the string.

    >>> list(tokenize('7/17-7/18 3 pm- 4 pm'))
    ['7/17', '-', '7/18', '3', 'pm', '-', '4', 'pm']
    >>> list(tokenize('7/17 3 pm- 7/19 2 pm'))
    ['7/17', '3', 'pm', '-', '7/19', '2', 'pm']
    >>> list(tokenize('7/17, 7/18, 7/19 at 2'))
    ['7/17', ',', '7/18', ',', '7/19', 'at', '2']
    """
    tokens = generic_tokenize(characters)
    tokens = clean_dash_tokens(tokens)
    return tokens


def generic_tokenize(characters):
    """Default tokenizer

    >>> list(generic_tokenize('7/17/18 3:00 p.m.'))
    ['7/17/18', '3:00', 'p.m.']
    >>> list(generic_tokenize('July 17, 2018 at 3p.m.'))
    ['July', '17', ',', '2018', 'at', '3', 'p.m.']
    >>> list(generic_tokenize('July 17, 2018 3 p.m.'))
    ['July', '17', ',', '2018', '3', 'p.m.']
    >>> list(generic_tokenize('3PM on July 17'))
    ['3', 'PM', 'on', 'July', '17']
    >>> list(generic_tokenize('tomorrow noon,Wed 3 p.m.,Fri 11 AM'))
    ['tomorrow', 'noon', ',', 'Wed', '3', 'p.m.', ',', 'Fri', '11', 'AM']
    """
    token = ''
    punctuation = ''
    last_type = None
    for character in characters:
        type = get_character_type(character)
        is_different_type = None not in (type, last_type) and type != last_type \
            and 'punctuation' not in (type, last_type)
        is_skip_character = character in string.whitespace
        is_break_character = character in ','

        if is_skip_character or is_different_type or is_break_character:
            if token:
                yield token
                token = ''
            token = character if not is_skip_character else ''
            if is_break_character:
                yield token
                token = ''
            last_type = type
            continue
        token += character
        last_type = type
    yield token


def clean_dash_tokens(tokens):
    """Clean up dash tokens.

    - If the dash-delimited values are not integers, the values joined by dashes
      will need further parsing.

    >>> list(clean_dash_tokens(['7-18', '3', 'pm-']))
    ['7-18', '3', 'pm', '-']
    >>> list(clean_dash_tokens(['7/17-7/18']))
    ['7/17', '-', '7/18']
    """
    for token in tokens:
        if '-' in token:
            parts = token.split('-')
            if not all([s.isdigit() for s in parts]):
                if parts[0]:
                    yield parts[0]
                for part in parts[1:]:
                    yield '-'
                    if part:
                        yield part
                continue
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
