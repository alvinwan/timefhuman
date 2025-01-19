from datetime import datetime
import pytz
from babel.dates import get_timezone_name
from lark.tree import Tree
from lark.lexer import Token
from dataclasses import dataclass
from enum import Enum


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
    

def nodes_to_dict(nodes: list[Tree]) -> dict:
    result = {}
    for node in nodes:
        assert isinstance(node, (Tree, dict, Token)), f"Expected a Tree or dict, got {type(node)} ({node})"
        if isinstance(node, dict):
            result.update(node)
        elif isinstance(node, Tree):
            assert len(node.children) == 1, f"Expected 1 child for {node.data.value}, got {len(node.children)}"
            result[node.data.value] = node.children[0].value
    return result
