import datetime

import pytz

from timefhuman import Direction


def localized_datetime(tz_name, *parts):
    return pytz.timezone(tz_name).localize(datetime.datetime(*parts))


DEFAULT_CASES = [
    # time only
    ("5p", [datetime.datetime(2018, 8, 4, 17, 0)]),
    ("3p EST", [localized_datetime("US/Michigan", 2018, 8, 4, 15, 0)]),

    # date only
    ("July 2019", [datetime.datetime(2019, 7, 1, 0, 0)]),
    ("7-17-18", [datetime.datetime(2018, 7, 17, 0, 0)]),
    ("2018-7-17", [datetime.datetime(2018, 7, 17, 0, 0)]),
    ("08.07.2013", [datetime.datetime(2013, 8, 7, 0, 0)]),
    ("2013.08.07", [datetime.datetime(2013, 8, 7, 0, 0)]),
    ("7/2018", [datetime.datetime(2018, 7, 1, 0, 0)]),
    ("Wed 25 Jun", [datetime.datetime(2018, 6, 25, 0, 0)]),

    # datetimes
    ("July 17, 2018 at 3p.m.", [datetime.datetime(2018, 7, 17, 15, 0)]),
    ("July 17, 2018 3 p.m.", [datetime.datetime(2018, 7, 17, 15, 0)]),
    ("3PM on July 17", [datetime.datetime(2018, 7, 17, 15, 0)]),
    ("July 17 at 3", [datetime.datetime(2018, 7, 17, 3, 0)]),
    ("7/17/18 3:00 p.m.", [datetime.datetime(2018, 7, 17, 15, 0)]),
    ("Wed., Jan 6 2016 at 10:13AM", [datetime.datetime(2016, 1, 6, 10, 13)]),
    ("01/13/2016 11 AM", [datetime.datetime(2016, 1, 13, 11, 0)]),
    ("11:00 a.m., Pacific Time, January 13, 2016", [localized_datetime("US/Pacific", 2016, 1, 13, 11, 0)]),
    ("5:00 p.m. Pacific Time, January 8, 2016", [localized_datetime("US/Pacific", 2016, 1, 8, 17, 0)]),
    ("3 p.m. today", [datetime.datetime(2018, 8, 4, 15, 0)]),
    ("Tomorrow 3p", [datetime.datetime(2018, 8, 5, 15, 0)]),
    ("3p tomorrow", [datetime.datetime(2018, 8, 5, 15, 0)]),
    ("yesterday 3p", [datetime.datetime(2018, 8, 3, 15, 0)]),
    ("July 3rd", [datetime.datetime(2018, 7, 3, 0, 0)]),

    # date-only ranges
    ("7/17-7/18", [(datetime.datetime(2018, 7, 17), datetime.datetime(2018, 7, 18))]),
    ("July 17-18", [(datetime.datetime(2018, 7, 17), datetime.datetime(2018, 7, 18))]),
    ("June 11-16, 2026", [(datetime.datetime(2026, 6, 11), datetime.datetime(2026, 6, 16))]),
    ("June 11-16 2026", [(datetime.datetime(2026, 6, 11), datetime.datetime(2026, 6, 16))]),

    # time-only ranges
    ("3p -4p", [(datetime.datetime(2018, 8, 4, 15, 0), datetime.datetime(2018, 8, 4, 16, 0))]),
    (
        "3p -4p PDT",
        [(
            localized_datetime("US/Pacific", 2018, 8, 4, 15, 0),
            localized_datetime("US/Pacific", 2018, 8, 4, 16, 0),
        )],
    ),
    ("6:00 pm - 12:00 am", [(datetime.datetime(2018, 8, 4, 18, 0), datetime.datetime(2018, 8, 5, 0, 0))]),
    ("8/4 6:00 pm - 8/4 12:00 am", [(datetime.datetime(2018, 8, 4, 18, 0), datetime.datetime(2018, 8, 4, 0, 0))]),
    ("11PM to 1AM", [(datetime.datetime(2018, 8, 4, 23, 0), datetime.datetime(2018, 8, 5, 1, 0))]),

    # date and time ranges
    ("7/17 3 pm- 7/19 2 pm", [(datetime.datetime(2018, 7, 17, 15, 0), datetime.datetime(2018, 7, 19, 14, 0))]),
    ("Jun 28 5:00 PM - Aug 02 7:00 PM", [(datetime.datetime(2018, 6, 28, 17, 0), datetime.datetime(2018, 8, 2, 19, 0))]),
    ("Jun 28 2019 5:00 PM - Aug 02 2019 7:00 PM", [(datetime.datetime(2019, 6, 28, 17, 0), datetime.datetime(2019, 8, 2, 19, 0))]),
    ("6/28 5:00 PM - 8/02 7:00 PM", [(datetime.datetime(2018, 6, 28, 17, 0), datetime.datetime(2018, 8, 2, 19, 0))]),
    ("6/28/2019 5:00 PM - 8/02/2019 7:00 PM", [(datetime.datetime(2019, 6, 28, 17, 0), datetime.datetime(2019, 8, 2, 19, 0))]),

    # choices
    ("July 4th or 5th at 3PM", [[datetime.datetime(2018, 7, 4, 15, 0), datetime.datetime(2018, 7, 5, 15, 0)]]),
    (
        "tomorrow noon,Wed 3 p.m.,Fri 11 AM",
        [[
            datetime.datetime(2018, 8, 5, 12, 0),
            datetime.datetime(2018, 8, 8, 15, 0),
            datetime.datetime(2018, 8, 10, 11, 0),
        ]],
    ),
    (
        "Are you free this Wed at 3p? Or maybe Fri at 5p?",
        [datetime.datetime(2018, 8, 8, 15, 0), datetime.datetime(2018, 8, 10, 17, 0)],
    ),

    # choices of ranges
    (
        "7/17 4-5 PM or 5-6 PM today",
        [[
            (datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
            (datetime.datetime(2018, 8, 4, 17, 0), datetime.datetime(2018, 8, 4, 18, 0)),
        ]],
    ),

    # timedeltas converted properly
    ("30 minutes", [datetime.datetime(2018, 8, 4, 14, 30)]),
    ("30-40 mins", [(datetime.datetime(2018, 8, 4, 14, 30), datetime.datetime(2018, 8, 4, 14, 40))]),
    ("1 or 2 days", [[datetime.datetime(2018, 8, 5, 14, 0), datetime.datetime(2018, 8, 6, 14, 0)]]),
    ("in 1 year", [datetime.datetime(2019, 8, 4, 14, 0)]),
    ("1 year ago", [datetime.datetime(2017, 8, 4, 14, 0)]),

    # standard structured formats
    ("2022-12-27T09:15:01.002", [datetime.datetime(2022, 12, 27, 9, 15, 1, 2)]),
]


NO_INFERENCE_CASES = [
    # empty
    ("", []),

    # time only
    ("5p", [datetime.time(17, 0)]),
    ("3 o'clock pm", [datetime.time(15, 0)]),
    ("5p Eastern Time", [datetime.time(17, 0, tzinfo=pytz.timezone("US/Michigan"))]),
    ("Wed., Jan 6 2016 at 10:13AM", [datetime.datetime(2016, 1, 6, 10, 13)]),
    ("01/13/2016 11 AM", [datetime.datetime(2016, 1, 13, 11, 0)]),
    ("11:00 a.m., Pacific Time, January 13, 2016", [localized_datetime("US/Pacific", 2016, 1, 13, 11, 0)]),

    # date only
    ("July 2019", [datetime.date(2019, 7, 1)]),
    ("Sunday 7/7/2019", [datetime.date(2019, 7, 7)]),
    ("1/1/95", [datetime.date(1995, 1, 1)]),
    ("08.07.2013", [datetime.date(2013, 8, 7)]),
    ("Wed 25 Jun", [datetime.date(2018, 6, 25)]),
    ("1.3.4", []),
    ("2-319", []),

    # date-only ranges
    ("7/17-7/18", [(datetime.date(2018, 7, 17), datetime.date(2018, 7, 18))]),
    ("July 17-18", [(datetime.date(2018, 7, 17), datetime.date(2018, 7, 18))]),
    ("June 11-16, 2026", [(datetime.date(2026, 6, 11), datetime.date(2026, 6, 16))]),
    ("June 11-16 2026", [(datetime.date(2026, 6, 11), datetime.date(2026, 6, 16))]),
    ("31/08/2012 to 30/08/2013", [(datetime.date(2012, 8, 31), datetime.date(2013, 8, 30))]),

    # time-only ranges
    ("3p -4p", [(datetime.time(15, 0), datetime.time(16, 0))]),
    ("3-4p", [(datetime.time(15, 0), datetime.time(16, 0))]),

    # durations
    ("30 minutes", [datetime.timedelta(minutes=30)]),
    ("30 mins", [datetime.timedelta(minutes=30)]),
    ("2 hours", [datetime.timedelta(hours=2)]),
    ("2 hours 30 minutes", [datetime.timedelta(hours=2, minutes=30)]),
    ("2 hours and 30 minutes", [datetime.timedelta(hours=2, minutes=30)]),
    ("2h30m", [datetime.timedelta(hours=2, minutes=30)]),
    ("1 day and an hour", [datetime.timedelta(days=1, hours=1)]),
    ("1.5 hours", [datetime.timedelta(hours=1, minutes=30)]),
    ("1.5h", [datetime.timedelta(hours=1, minutes=30)]),
    ("in five minutes", [datetime.timedelta(minutes=5)]),
    ("in 3 days", [datetime.timedelta(days=3)]),
    ("for 3 days", [datetime.timedelta(days=3)]),
    ("past 40 minutes", [datetime.timedelta(minutes=-40)]),
    ("for the past 40 minutes", [datetime.timedelta(minutes=-40)]),
    ("awk", []),
    ("a wk", [datetime.timedelta(days=7)]),
    ("thirty two hours", [datetime.timedelta(hours=32)]),
    ("in 1 year", [datetime.timedelta(days=365)]),
    ("1 year ago", [datetime.timedelta(days=-365)]),

    # duration ranges and lists
    ("30-40 mins", [(datetime.timedelta(minutes=30), datetime.timedelta(minutes=40))]),
    ("1 or 2 days", [[datetime.timedelta(days=1), datetime.timedelta(days=2)]]),

    # TODO: support "quarter to 3"
    # TODO: support "one and a half hours"

    # TODO ('noon next week') <- should be a list of options
    # TODO: support recurrences, like "5pm on thursdays" (see gh#33)

    # TODO: support natural language date ranges e.g., this week, next weekend, any weekday gh#18
    # TODO: support natural language time ranges e.g., afternoon, morning, evening, tonight, today night gh#30

    # TODO: christmas? new years? eve?
    # TODO: support 'this past July' (e.g., reduce to 'this')
    # TODO: support 'last week of dec'

    # support for date and month modifiers
    ("next Monday", [datetime.date(2018, 8, 6)]),
    ("this Monday", [datetime.date(2018, 8, 6)]),
    ("next next Monday", [datetime.date(2018, 8, 13)]),
    ("last Monday", [datetime.date(2018, 7, 30)]),
    ("following Monday", [datetime.date(2018, 8, 6)]),
    ("next July", [datetime.date(2019, 7, 1)]),
    ("last July", [datetime.date(2017, 7, 1)]),
    ("last Wednesday of December", [datetime.date(2018, 12, 26)]),
    ("first Wednesday of December", [datetime.date(2018, 12, 5)]),
    ("second Wednesday of December", [datetime.date(2018, 12, 12)]),
    ("third Wednesday of December", [datetime.date(2018, 12, 19)]),
    ("fourth Wednesday of December", [datetime.date(2018, 12, 26)]),
    ("3rd Monday in January", [datetime.date(2018, 1, 15)]),
    ("3rd Monday in February", [datetime.date(2018, 2, 19)]),
    ("1st Monday in September", [datetime.date(2018, 9, 3)]),
    ("4th Thursday of November", [datetime.date(2018, 11, 22)]),
    ("between 9:00 a.m. and 3:30 p.m.", [(datetime.time(9, 0), datetime.time(15, 30))]),

    # support for vernacular datetimes
    ("afternoon", [datetime.time(15, 0)]),
    ("morning", [datetime.time(6, 0)]),
    ("evening", [datetime.time(18, 0)]),
    ("night", [datetime.time(20, 0)]),
    ("today night", [datetime.datetime(2018, 8, 4, 20, 0)]),
    ("tonight", [datetime.datetime(2018, 8, 4, 20, 0)]),
    ("midnight", [datetime.time(0, 0)]),
    ("midday", [datetime.time(12, 0)]),
    ("e 6:50PM", [datetime.time(18, 50)]),
]


CUSTOM_CONFIG_CASES = [
    ({"direction": Direction.next, "infer_datetimes": False}, "mon", [datetime.date(2018, 8, 6)]),
    ({"direction": Direction.this, "infer_datetimes": False}, "mon", [datetime.date(2018, 8, 6)]),
    ({"direction": Direction.previous, "infer_datetimes": False}, "mon", [datetime.date(2018, 7, 30)]),
    ({"infer_datetimes": True}, "5p", [datetime.datetime(2018, 8, 4, 17, 0)]),
    ({"infer_datetimes": False}, "5p", [datetime.time(17, 0)]),
    ({"infer_datetimes": True}, "1p", [datetime.datetime(2018, 8, 5, 13, 0)]),
]


MATCHED_TEXT_CASES = [
    # sentence and prose extraction
    ("September 30, 2019.", [("September 30, 2019", (0, 18), datetime.datetime(2019, 9, 30, 0, 0))]),
    (
        "How does 5p mon sound? Or maybe 4p tu?",
        [
            ("5p mon", (9, 15), datetime.datetime(2018, 8, 6, 17, 0)),
            ("4p tu", (32, 37), datetime.datetime(2018, 8, 7, 16, 0)),
        ],
    ),
    ("There are 3 ways to do it", []),
    ("salmon for 9 amnesty tickets", []),
    ("s 1/1/24 C", [("1/1/24", (2, 8), datetime.datetime(2024, 1, 1, 0, 0))]),
    (
        "running from 7-11pm and featuring resident DJs",
        [("7-11pm", (13, 19), (datetime.datetime(2018, 8, 4, 19, 0), datetime.datetime(2018, 8, 4, 23, 0)))],
    ),
    ("foo 08-07-2013 bar", [("08-07-2013", (4, 14), datetime.datetime(2013, 8, 7, 0, 0))]),
    ("<!-- REMOVED 08-07-2013 -->", [("08-07-2013", (13, 23), datetime.datetime(2013, 8, 7, 0, 0))]),
    ("foo 08.07.2013 bar", [("08.07.2013", (4, 14), datetime.datetime(2013, 8, 7, 0, 0))]),
    (
        "foo January 4th, 2017 at 8:00pm bar",
        [("January 4th, 2017 at 8:00pm", (4, 31), datetime.datetime(2017, 1, 4, 20, 0))],
    ),
    (
        "foo 2024-11-09 tomorrow at noon bar",
        [
            ("2024-11-09", (4, 14), datetime.datetime(2024, 11, 9, 0, 0)),
            ("tomorrow at noon", (15, 31), datetime.datetime(2018, 8, 5, 12, 0)),
        ],
    ),
    ("we start phase two in 3 days", [("in 3 days", (19, 28), datetime.datetime(2018, 8, 7, 14, 0))]),
    ("we waited for 3 days", [("for 3 days", (10, 20), datetime.datetime(2018, 8, 7, 14, 0))]),
    (
        "CR is 0 for the past 40 minutes",
        [("for the past 40 minutes", (8, 31), datetime.datetime(2018, 8, 4, 13, 20))],
    ),
    ("the following may be used by the City in determining", []),
    ("foo 1.3.4 bar", []),
    ("style='width:1px; height:1px;'", []),
    ("telephone (253) 591-5252", []),
    ("Section 7.02B 7a. - e.", []),
    ("Meet at 7a.", [("7a", (8, 10), datetime.datetime(2018, 8, 5, 7, 0))]),
    ("Wait 3h please", [("3h", (5, 7), datetime.datetime(2018, 8, 4, 17, 0))]),
    ("Wed., Jan 6 2016 at 10:13AM", [("Wed., Jan 6 2016 at 10:13AM", (0, 27), datetime.datetime(2016, 1, 6, 10, 13))]),
    ("foo 01/13/2016 11 AM bar", [("01/13/2016 11 AM", (4, 20), datetime.datetime(2016, 1, 13, 11, 0))]),
    (
        "foo 11:00 a.m., Pacific Time, January 13, 2016 bar",
        [("11:00 a.m., Pacific Time, January 13, 2016", (4, 46), localized_datetime("US/Pacific", 2016, 1, 13, 11, 0))],
    ),
    (
        "foo 5:00 p.m. Pacific Time, January 8, 2016 bar",
        [("5:00 p.m. Pacific Time, January 8, 2016", (4, 43), localized_datetime("US/Pacific", 2016, 1, 8, 17, 0))],
    ),
    (
        "Deliveries shall be between 9:00 a.m. and 3:30 p.m. daily.",
        [("between 9:00 a.m. and 3:30 p.m", (20, 50), (datetime.datetime(2018, 8, 5, 9, 0), datetime.datetime(2018, 8, 5, 15, 30)))],
    ),
    (
        "Rev.: 07/2/07, 08/27/07, 01/16/08, 03/7/08, 09/11/08, 01/19/09, 06/15/09, 01/6/11, 03/17/11, 10/03/11",
        [(
            "07/2/07, 08/27/07, 01/16/08, 03/7/08, 09/11/08, 01/19/09, 06/15/09, 01/6/11, 03/17/11, 10/03/11",
            (6, 101),
            [
                datetime.datetime(2007, 7, 2, 0, 0),
                datetime.datetime(2007, 8, 27, 0, 0),
                datetime.datetime(2008, 1, 16, 0, 0),
                datetime.datetime(2008, 3, 7, 0, 0),
                datetime.datetime(2008, 9, 11, 0, 0),
                datetime.datetime(2009, 1, 19, 0, 0),
                datetime.datetime(2009, 6, 15, 0, 0),
                datetime.datetime(2011, 1, 6, 0, 0),
                datetime.datetime(2011, 3, 17, 0, 0),
                datetime.datetime(2011, 10, 3, 0, 0),
            ],
        )],
    ),
    ("holiday is on 3rd Monday in January", [("3rd Monday in January", (14, 35), datetime.datetime(2018, 1, 15, 0, 0))]),
    ("holiday is on 3rd Monday in February", [("3rd Monday in February", (14, 36), datetime.datetime(2018, 2, 19, 0, 0))]),
    ("holiday is on 1st Monday in September", [("1st Monday in September", (14, 37), datetime.datetime(2018, 9, 3, 0, 0))]),
    ("holiday is on 4th Thursday of November", [("4th Thursday of November", (14, 38), datetime.datetime(2018, 11, 22, 0, 0))]),
    ("RCW 62A.2-319", []),
    ("90p", []),
    ("4906/0", []),
    ("one-night-only", []),
    ("W:648 H:432", []),
    (
        "Tue, 23 Apr 1996 13:28:27 -0400",
        [(
            "Tue, 23 Apr 1996 13:28:27 -0400",
            (0, 31),
            datetime.datetime(1996, 4, 23, 13, 28, 27, tzinfo=datetime.timezone(datetime.timedelta(hours=-4))),
        )],
    ),
]
