from datetime import datetime

from dataclasses import replace
from lark import Tree, Token
from timefhuman.extraction import extract_fast, prefer_extraction
from timefhuman.lalr import parse_lalr_renderers as _parse_lalr
from timefhuman.scanner import TOKEN_PATTERN
from timefhuman.utils import Direction, generate_timezone_mapping, tfhConfig
from timefhuman.fastpath import parse_fast
from timefhuman.renderers import tfhAmbiguous


__all__ = ("timefhuman", "tfhConfig", "Direction", "DEFAULT_CONFIG")


DEFAULT_CONFIG = tfhConfig()
def _build_candidate_parsers(config: tfhConfig):
    timezone_mapping = generate_timezone_mapping()

    def parse_fast_candidate(string: str, start_pos: int = 0):
        return parse_fast(string, config=config, timezone_mapping=timezone_mapping, start_pos=start_pos)

    def parse_lalr_candidate(string: str, start_pos: int = 0):
        return _parse_lalr(string, config=config, start_pos=start_pos)

    parse_fast_candidate._cache_tag = ("fast", config.now, config.direction)
    parse_lalr_candidate._cache_tag = ("lalr", config.now, config.direction)
    return parse_fast_candidate, parse_lalr_candidate


def _parse_renderers(string: str, config: tfhConfig):
    parse_fast_candidate, parse_lalr_candidate = _build_candidate_parsers(config)
    use_extraction = prefer_extraction(string)

    if use_extraction:
        for parse_candidate in (parse_fast_candidate, parse_lalr_candidate):
            renderers = extract_fast(string, parse_candidate=parse_candidate)
            if renderers is not None:
                return renderers
        return []

    renderers = parse_fast_candidate(string)
    if renderers is not None:
        return renderers

    renderers = parse_lalr_candidate(string)
    if renderers is not None:
        return renderers

    for parse_candidate in (parse_fast_candidate, parse_lalr_candidate):
        renderers = extract_fast(string, parse_candidate=parse_candidate)
        if renderers is not None:
            return renderers

    return []


def _matched_results(string: str, renderers, config: tfhConfig):
    results = []
    for renderer in renderers:
        try:
            value = renderer.to_object(config)
        except (OverflowError, ValueError):
            continue
        start, end = renderer.matched_text_pos
        results.append((string[start:end], (start, end), value))
    return results


def _valid_objects(renderers, config: tfhConfig):
    results = []
    for renderer in renderers:
        try:
            results.append(renderer.to_object(config))
        except (OverflowError, ValueError):
            continue
    return results


def build_raw_tree(string: str, config: tfhConfig):
    match_config = replace(config, return_matched_text=True)
    renderers = _parse_renderers(string, match_config)

    children = []
    cursor = 0
    for start, end in [(renderer.matched_text_pos[0], renderer.matched_text_pos[1]) for renderer in renderers]:
        children.extend(_unknown_children(string[cursor:start]))
        children.append(Tree('expression', [Token('MATCH', string[start:end])]))
        cursor = end
    children.extend(_unknown_children(string[cursor:]))
    return Tree('start', children)


def _unknown_children(text: str):
    return [Tree('unknown', [Token('UNKNOWN', match.group(0))]) for match in TOKEN_PATTERN.finditer(text)]


def timefhuman(string, config: tfhConfig = DEFAULT_CONFIG, raw: bool=False, now: bool=False):
    if not string.strip():
        assert not raw, "Empty string not allowed when raw=True"
        return []

    config = config if config.now is not None else replace(config, now=datetime.now())
    if now:
        return config.now

    if raw:
        return build_raw_tree(string, config)

    renderers = [renderer for renderer in _parse_renderers(string, config) if not isinstance(renderer, tfhAmbiguous)]

    if config.return_matched_text:
        return _matched_results(string, renderers, config)
    return _valid_objects(renderers, config)
