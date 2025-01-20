from datetime import timedelta
import datetime
from pathlib import Path

from lark import Lark, Transformer, v_args, Token, Discard
import pytz
from timefhuman.utils import generate_timezone_mapping, nodes_to_dict, nodes_to_multidict, get_month_mapping, tfhConfig, Direction, direction_to_offset
from timefhuman.renderers import tfhDatetime, tfhDate, tfhTime, tfhRange, tfhList, tfhTimedelta, tfhAmbiguous, tfhUnknown, tfhDatelike, tfhMatchable
from dateutil.relativedelta import relativedelta, weekdays


__all__ = ('timefhuman',)


DIRECTORY = Path(__file__).parent
parser = None
timezone_mapping = None


def get_parser():
    global parser, timezone_mapping
    if parser is None:
        timezone_mapping = generate_timezone_mapping()
        with open(DIRECTORY / 'grammar.lark', 'r') as file:
            grammar = file.read()
        grammar = grammar.replace('(TIMEZONE_MAPPING)', '|'.join(timezone_mapping.keys()))
        parser = Lark(grammar, start="start", propagate_positions=True)
    return parser


def timefhuman(string, config: tfhConfig = tfhConfig(), raw=None):
    parser = get_parser()
    tree = parser.parse(string)

    if raw:
        return tree

    transformer = tfhTransformer(config=config)
    renderers = transformer.transform(tree)
    renderers = list(filter(lambda r: not isinstance(r, (tfhUnknown, tfhAmbiguous)), renderers))
    datetimes = [renderer.to_object(config) for renderer in renderers]
    
    if config.return_matched_text:
        matched_texts = [string[renderer.matched_text_pos[0]:renderer.matched_text_pos[1]] for renderer in renderers]
        return list(zip(matched_texts, datetimes))
    
    if config.return_single_object and len(datetimes) == 1:
        return datetimes[0]
    return datetimes


def infer_from(source: tfhDatelike, target: tfhDatelike):
    if isinstance(source, tfhAmbiguous):
        # NOTE: Ambiguous tokens have no information to offer
        return target
    if isinstance(target, tfhAmbiguous) and isinstance(source, tfhDatelike):
        if source.time:
            target = tfhDatetime(time=tfhTime(hour=target.value, meridiem=source.meridiem))
        elif source.year:
            target = tfhDatetime(date=tfhDate(year=target.value))
        elif source.day:
            target = tfhDatetime(date=tfhDate(day=target.value))
        elif source.month:
            target = tfhDatetime(date=tfhDate(month=target.value))
        else:
            raise NotImplementedError(f"Not enough context to infer what {target} is")
    if isinstance(source, tfhDatelike) and isinstance(target, tfhDatelike):
        if source.date and not target.date:
            target.date = source.date
        if source.time and not target.time:
            target.time = source.time
        if source.month and not target.month:
            target.month = source.month
        if source.year and not target.year:
            target.year = source.year
        if source.meridiem and not target.meridiem:
            target.meridiem = source.meridiem
        if source.tz and not target.tz:
            target.tz = source.tz
    if isinstance(source, tfhTimedelta) and isinstance(target, tfhAmbiguous):
        target = tfhTimedelta.from_object(timedelta(**{source.unit: target.value}), unit=source.unit)
    return target


def infer(datetimes):
    """
    Infer any missing components of datetimes from the first or last datetime.
    """
    for i, dt in enumerate(datetimes[1:], start=1):
        datetimes[i] = infer_from(datetimes[0], dt)
        
    for i, dt in enumerate(datetimes[:-1]):
        datetimes[i] = infer_from(datetimes[-1], dt)

    return datetimes


class tfhTransformer(Transformer):
    def __init__(self, config: tfhConfig = tfhConfig()):
        self.config = config

    def start(self, children):
        """Strip the 'start' rule and return child(ren) directly."""
        return children

    @v_args(tree=True)
    def expression(self, tree):
        """The top-level expression could be a range, list, or single."""
        expr = tree.children[0]
        if self.config.return_matched_text:
            assert isinstance(expr, tfhMatchable), f"Expected tfhDatelike or tfhAmbiguous, got {type(expr)}"
            expr.matched_text_pos = (tree.meta.start_pos, tree.meta.end_pos)
        return expr
    
    def unknown(self, children):
        return tfhUnknown(children[0].value)

    def single(self, children):
        """A single object can be a datetime, a date, or a time."""
        if len(children) == 1 and hasattr(children[0], 'data') and children[0].data.value == 'ambiguous':
            return tfhAmbiguous(int(children[0].children[0].value))
        return children[0]
    
    ###############
    # Collections #
    ###############
    
    def range(self, children):
        """Handles expressions like '7/17 3 PM - 7/18 4 PM'."""
        assert len(children) == 2
        return tfhRange(infer(children))

    def list(self, children):
        """Handles comma/or lists like '7/17, 7/18, 7/19' or '7/17 or 7/18'."""
        return tfhList(infer(children))
    
    ############
    # Duration #
    ############
    
    def duration(self, children):
        # TODO: just grabbing the first may cause problems later. how to do this more generically?
        return tfhTimedelta.from_object(sum([child.to_object(self.config) for child in children], timedelta()), unit=children[0].unit)
    
    def duration_part(self, children):
        mapping = {
            'an': 1,
            'a': 1,
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10,
            'eleven': 11,
            'twelve': 12,
            'thirteen': 13,
            'fourteen': 14,
            'fifteen': 15,
            'sixteen': 16,
            'seventeen': 17,
            'eighteen': 18,
            'nineteen': 19,
            'twenty': 20,
            'thirty': 30,
            'forty': 40,
            'fifty': 50,
            'sixty': 60,
            'seventy': 70,
            'eighty': 80,
            'ninety': 90,
        }
        # TODO: write my own multidict?
        data = {child.data.value: [_child.value for _child in child.children] for child in children}
        duration_number = float(data['duration_number'][0]) if 'duration_number' in data else sum([mapping[value] for value in data.get('duration_numbername', [])])
        duration_unit = data.get('duration_unit', data.get('duration_unit_letter', None))[0]
        for group in (
            ('minutes', 'minute', 'mins', 'min', 'm'),
            ('hours', 'hour', 'hrs', 'hr', 'h'),
            ('days', 'day', 'd'),
            ('weeks', 'week', 'wks', 'wk'),
            ('months', 'month', 'mos'),
            ('years', 'year', 'yrs', 'yr'),
        ):
            if duration_unit in group:
                return tfhTimedelta.from_object(timedelta(**{group[0]: duration_number}), unit=group[0])
        raise NotImplementedError(f"Unknown duration unit: {data['duration_unit']}")

    ############
    # Datetime #
    ############

    def datetime(self, children):
        data = nodes_to_dict(children)
        if 'datetime' in data:
            return data['datetime']
        return tfhDatetime(date=data.get('date'), time=data.get('time'))
    
    def date(self, children):
        data = nodes_to_dict(children)
        
        if 'date' in data:
            # TODO: simply return data?
            return {'date': data['date']}
        
        # If there's a weekday and no other date info, use the weekday
        if 'weekday' in data and all(key not in data for key in ('day', 'month', 'year')):
            return {'date': data['weekday']}
        
        delta = None
        if 'offset' in data:
            _data = nodes_to_multidict(children)
            delta = relativedelta(years=sum(_data['offset']))  # sum offsets, such as 'next next'  
        elif 'position' in data:
            assert 'month' in data and 'weekday' in data
            weekday = weekdays[data['weekday'].to_object(self.config).weekday()]
            position = data['position']
            if position == 'first':
                delta = relativedelta(day=1, weekday=weekday(+1))
            elif position == 'second':
                delta = relativedelta(day=8, weekday=weekday(+1))
            elif position == 'third':
                delta = relativedelta(day=15, weekday=weekday(+1))
            elif position == 'fourth':
                delta = relativedelta(day=22, weekday=weekday(+1))
            elif position == 'last':
                delta = relativedelta(day=31, weekday=weekday(-1))
            else:
                raise NotImplementedError(f"Unknown position: {position}")

        return {'date': tfhDate(
            year=data.get('year'),
            month=data.get('month'),
            day=data.get('day'),
            delta=delta,
        )}
        
        
    def day(self, children):
        return {'day': int(children[0].value)}
    
    def month(self, children):
        return {'month': int(children[0].value)}
    
    def year(self, children):
        value = int(children[0].value)
        
        if 50 < value < 100:
            value = 1900 + value
        elif 0 < value < 50:
            value = 2000 + value
        
        return {'year': value}
    
    def monthname(self, children):
        monthname = children[0].value.lower()
        month = get_month_mapping().get(monthname, self.config.now.month)
        return {'month': month}
    
    def weekday(self, children):
        data = nodes_to_multidict(children)
        
        weekday = data['WEEKDAY'][0][:2].lower()
        target_weekday = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su'].index(weekday)
        
        offset = direction_to_offset(self.config.direction)
        if 'offset' in data:
            offset = sum(data['offset'])  # sum offsets, such as 'next next'

        # TODO: store as delta and let renderer infer date?
        date = self.config.now.date() + relativedelta(weekday=weekdays[target_weekday](offset))
        return {'weekday': tfhDate.from_object(date)}
    
    def modifier(self, children):
        value = children[0].value
        if value in ('next', 'upcoming', 'following'):
            return {'offset': +1}
        elif value in ('previous', 'last', 'past', 'preceding'):  # TODO: support 'last' for both meanings
            return {'offset': -1}
        elif value == 'this':
            return {'offset': 0}
        raise NotImplementedError(f"Unknown modifier: {value}")
    
    def datename(self, children):
        datename = children[0].value.lower()
        if datename == 'today':
            _date = tfhDate.from_object(self.config.now.date())
        elif datename == 'tomorrow':
            _date = tfhDate.from_object(self.config.now.date() + timedelta(days=1))
        elif datename == 'yesterday':
            _date = tfhDate.from_object(self.config.now.date() - timedelta(days=1))
        else:
            raise NotImplementedError(f"Unknown datename: {datename}")
        return {'date': _date}
    
    def dayoryear(self, children):
        if children[0].value.isdigit():
            value = int(children[0].value)
            return {'day': value} if value < 32 else {'year': value}
        raise NotImplementedError(f"Unknown day or year: {children[0]}")

    def time(self, children):
        data = nodes_to_dict(children)
        
        if 'time' in data:
            # TODO: simply return data?
            return {'time': data['time']}
        
        return {'time': tfhTime(
            hour=int(data.get("hour", 0)),
            minute=int(data.get("minute", 0)),
            second=int(data.get("second", 0)),
            millisecond=int(data.get("millisecond", 0)),
            meridiem=data.get("meridiem", None),
            tz=data.get("timezone", None),
        )}
    
    def meridiem(self, children):
        meridiem = children[0].value.lower()
        if meridiem.startswith('a'):
            return {'meridiem': tfhTime.Meridiem.AM}
        elif meridiem.startswith('p'):
            return {'meridiem': tfhTime.Meridiem.PM}
        raise NotImplementedError(f"Unknown meridiem: {meridiem}")
    
    def timezone(self, children):
        timezone = children[0].value.lower()
        return {'timezone': pytz.timezone(timezone_mapping[timezone])}

    def timename(self, children):
        timename = children[0].value.lower()
        if timename == 'noon':
            _time = tfhTime(hour=12, minute=0, meridiem=tfhTime.Meridiem.PM)
        elif timename == 'midday':
            _time = tfhTime(hour=12, minute=0, meridiem=tfhTime.Meridiem.PM)
        elif timename == 'midnight':
            _time = tfhTime(hour=0, minute=0, meridiem=tfhTime.Meridiem.AM)
        elif timename == 'morning':
            _time = tfhTime(hour=6, minute=0, meridiem=tfhTime.Meridiem.AM)
        elif timename == 'afternoon':
            _time = tfhTime(hour=15, minute=0, meridiem=tfhTime.Meridiem.PM)
        elif timename == 'evening':
            _time = tfhTime(hour=18, minute=0, meridiem=tfhTime.Meridiem.PM)
        elif timename == 'night':
            _time = tfhTime(hour=20, minute=0, meridiem=tfhTime.Meridiem.PM)
        else:
            raise NotImplementedError(f"Unknown timename: {timename}")
        return {'time': _time}
    
    def houronly(self, children):
        return {'time': tfhTime(hour=int(children[0].value))}

    def datetimename(self, children):
        datetimename = children[0].value.lower()
        if datetimename == 'tonight':
            _datetime = tfhDatetime(date=tfhDate.from_object(self.config.now.date()), time=tfhTime(hour=20, minute=0, meridiem=tfhTime.Meridiem.PM))
        else:
            raise NotImplementedError(f"Unknown datetimename: {datetimename}")
        return {'datetime': _datetime}

