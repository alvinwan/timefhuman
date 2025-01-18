from datetime import datetime
import pytz
from babel.dates import get_timezone_name
from lark.tree import Tree


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
        key: value for key, value in text_to_timezone.items()
        if key[0] not in ('+', '-') and not key.startswith('Unknown')
    }
    

def nodes_to_dict(nodes: list[Tree]) -> dict:
    result = {}
    for node in nodes:
        assert isinstance(node, Tree), f"Expected a Tree, got {type(node)}"
        assert len(node.children) == 1, f"Expected 1 child for {node.data.value}, got {len(node.children)}"
        result[node.data.value] = node.children[0].value
    return result
