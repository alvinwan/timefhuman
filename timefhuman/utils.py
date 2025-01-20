from datetime import datetime
import pytz
from babel.dates import get_timezone_name
from lark.tree import Tree
from lark.lexer import Token
from dataclasses import dataclass
from enum import Enum
from typing import List


MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]
Direction = Enum('Direction', ['previous', 'next', 'this'])


@dataclass
class tfhConfig:
    # Default to the next valid datetime or the previous one
    direction: Direction = Direction.next
    
    # Always produce datetime objects. If no date, use the current date. If no time, use midnight.
    infer_datetimes: bool = True
    
    # The 'current' datetime, used if infer_datetimes is True
    now: datetime = datetime.now()    
    
    # Return the matched text from the input string
    return_matched_text: bool = False
    
    # Return a single object instead of a list when there's only one match
    return_single_object: bool = True


def generate_timezone_mapping():
    text_to_timezone = {}

    for tz_name in pytz.all_timezones:
        timezone = pytz.timezone(tz_name)
        abbreviation1 = timezone.localize(datetime(2025, 1, 15)).strftime('%Z')
        abbreviation2 = timezone.localize(datetime(2025, 7, 15)).strftime('%Z')
        name = get_timezone_name(timezone)
        text_to_timezone[abbreviation1] = tz_name
        text_to_timezone[abbreviation2] = tz_name
        text_to_timezone[name] = tz_name

    return {
        key.lower(): value for key, value in text_to_timezone.items()
        if key[0] not in ('+', '-') and not key.startswith('Unknown')
    }
    
    
def get_month_mapping():
    mapping = {
        month: i + 1 for i, month in enumerate(MONTHS)
    }
    mapping.update({
        month[:3]: i + 1 for i, month in enumerate(MONTHS)
    })
    return mapping


def node_to_dict(node: Tree) -> dict:
    assert isinstance(node, (Tree, dict, Token)), f"Expected a Tree or dict, got {type(node)} ({node})"
    if isinstance(node, dict):
        return node
    elif isinstance(node, Tree):
        assert len(node.children) == 1, f"Expected 1 child for {node.data.value}, got {len(node.children)}"
        return {node.data.value: node.children[0].value}
    elif isinstance(node, Token):
        return {node.type: node.value}
    raise ValueError(f"Unknown node type: {type(node)} ({node})")


def nodes_to_dict(nodes: List[Tree]) -> dict:
    result = {}
    for node in nodes:
        result.update(node_to_dict(node))
    return result


def nodes_to_multidict(nodes: List[Tree]) -> dict:
    result = {}
    for node in nodes:
        for key, value in node_to_dict(node).items():
            if key not in result:
                result[key] = []
            result[key].append(value)
    return result


def direction_to_offset(direction: Direction) -> int:
    if direction == Direction.next:
        return +1
    elif direction == Direction.previous:
        return -1
    else:
        return 0
