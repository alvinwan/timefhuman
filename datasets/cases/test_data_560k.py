import datetime

from datasets.cases._shared import localized_datetime


MATCHED_TEXT = [
    # Bid dates and deadlines.
    ("01/13/2016\n            11 AM", (36, 64), datetime.datetime(2016, 1, 13, 11, 0)),
    ("01/05/2016", (190, 200), datetime.date(2016, 1, 5)),
    ("11:00 a.m., Pacific Time, January 13, 2016", (1914, 1956), localized_datetime("US/Pacific", 2016, 1, 13, 11, 0)),
    ("48 hours", (3223, 3231), datetime.timedelta(days=2)),
    ("09/22/2011", (3301, 3311), datetime.date(2011, 9, 22)),
    ("5:00 p.m. Pacific\nTime, January 8, 2016", (12858, 12897), localized_datetime("US/Pacific", 2016, 1, 8, 17, 0)),

    # Revision/date lists and holiday schedule.
    (
        "07/2/07, 08/27/07, 01/16/08, 03/7/08, 09/11/08, 01/19/09, 06/15/09, 01/6/11, 03/17/11, 10/03/11",
        (17966, 18061),
        [
            datetime.date(2007, 7, 2),
            datetime.date(2007, 8, 27),
            datetime.date(2008, 1, 16),
            datetime.date(2008, 3, 7),
            datetime.date(2008, 9, 11),
            datetime.date(2009, 1, 19),
            datetime.date(2009, 6, 15),
            datetime.date(2011, 1, 6),
            datetime.date(2011, 3, 17),
            datetime.date(2011, 10, 3),
        ],
    ),
    ("January 1", (26796, 26805), datetime.date(2018, 1, 1)),
    ("3rd Monday in January", (26838, 26859), datetime.date(2018, 1, 15)),
    ("3rd Monday in February", (26884, 26906), datetime.date(2018, 2, 19)),
    ("Last Monday in May", (26922, 26940), datetime.date(2018, 5, 28)),
    ("July 4", (26960, 26966), datetime.date(2018, 7, 4)),
    ("1st Monday in September", (26979, 27002), datetime.date(2018, 9, 3)),
    ("November 11", (27019, 27030), datetime.date(2018, 11, 11)),
    ("4th Thursday of November", (27050, 27074), datetime.date(2018, 11, 22)),
    ("4th Friday of November", (27100, 27122), datetime.date(2018, 11, 23)),
    ("December 25", (27139, 27150), datetime.date(2018, 12, 25)),
    ("Saturday or Sunday", (27188, 27206), [datetime.date(2018, 8, 4), datetime.date(2018, 8, 5)]),
    ("preceding Friday", (27212, 27228), datetime.date(2018, 8, 3)),
    ("following Monday", (27236, 27252), datetime.date(2018, 8, 6)),
    ("10 days", (31315, 31322), datetime.timedelta(days=10)),
    ("30 days", (37592, 37599), datetime.timedelta(days=30)),
    ("January 2012", (56685, 56697), datetime.date(2012, 1, 1)),
    ("one year", (67331, 67339), datetime.timedelta(days=365)),
    ("eighteen months", (68776, 68791), datetime.timedelta(days=540)),
    ("between 9:00 a.m. and 3:30 p.m", (72939, 72969), (datetime.time(9, 0), datetime.time(15, 30))),
    ("45 days", (101457, 101464), datetime.timedelta(days=45)),
    ("11/19/11", (113198, 113206), datetime.date(2011, 11, 19)),
    ("07/20/07, 04/09/12", (114241, 114259), [datetime.date(2007, 7, 20), datetime.date(2012, 4, 9)]),
    ("03/28/2014", (117160, 117170), datetime.date(2014, 3, 28)),
    ("09/11/2014", (119859, 119869), datetime.date(2014, 9, 11)),
    ("July 1, 2010", (125487, 125499), datetime.date(2010, 7, 1)),
    ("for one year", (137857, 137869), datetime.timedelta(days=365)),
    ("45 Days", (140204, 140211), datetime.timedelta(days=45)),
    ("30 Days", (140281, 140288), datetime.timedelta(days=30)),
    ("14 Days", (144165, 144172), datetime.timedelta(days=14)),
    ("90 Days,", (147080, 147088), datetime.timedelta(days=90)),
    ("eight hours", (173725, 173736), datetime.timedelta(seconds=28800)),
    ("ten hours", (174463, 174472), datetime.timedelta(seconds=36000)),
    ("forty hours", (174734, 174745), datetime.timedelta(days=1, seconds=57600)),
    ("7 Days", (187192, 187198), datetime.timedelta(days=7)),
    ("120 Days", (250919, 250927), datetime.timedelta(days=120)),
    ("60 Days", (253667, 253674), datetime.timedelta(days=60)),
    ("30 Day", (255253, 255259), datetime.timedelta(days=30)),
    ("for 3 years", (259143, 259154), datetime.timedelta(days=1095)),
    ("7 Day", (260642, 260647), datetime.timedelta(days=7)),
    ("Six year", (269824, 269832), datetime.timedelta(days=2190)),
    ("6 years", (270048, 270055), datetime.timedelta(days=2190)),
    ("midnight to midnight", (279943, 279963), (datetime.time(0, 0), datetime.time(0, 0))),

    # Project specs and work-hour rules.
    ("1/4/2016", (349927, 349935), datetime.date(2016, 1, 4)),
    ("72 hours", (352308, 352316), datetime.timedelta(days=3)),
    ("7 AM to 5 PM", (363423, 363435), (datetime.time(7, 0), datetime.time(17, 0))),
    ("between 7 AM and 5 PM", (364459, 364480), (datetime.time(7, 0), datetime.time(17, 0))),
    ("15 days,", (401438, 401446), datetime.timedelta(days=15)),
    ("60 days,", (401618, 401626), datetime.timedelta(days=60)),
    ("one day", (405260, 405267), datetime.timedelta(days=1)),
    ("one year", (423375, 423383), datetime.timedelta(days=365)),
    ("1 year", (448275, 448281), datetime.timedelta(days=365)),

    # Wage schedules and seasonal/hour rules.
    (
        "6:00 pm Saturday to 6:00 am Monday",
        (510499, 510533),
        (datetime.datetime(2018, 8, 4, 18, 0), datetime.datetime(2018, 8, 6, 6, 0)),
    ),
    (
        "6:00 pm Saturday to 5:00 am Monday",
        (511564, 511598),
        (datetime.datetime(2018, 8, 4, 18, 0), datetime.datetime(2018, 8, 6, 5, 0)),
    ),
    (
        "between March 16th and October 14th",
        (512932, 512967),
        (datetime.date(2018, 3, 16), datetime.date(2018, 10, 14)),
    ),
    (
        "between October 15th and March 15th",
        (513078, 513113),
        (datetime.date(2018, 10, 15), datetime.date(2019, 3, 15)),
    ),
    ("five day", (513358, 513366), datetime.timedelta(days=5)),
    ("four day-ten hour", (513407, 513424), (datetime.timedelta(days=4), datetime.timedelta(seconds=36000))),

    # Effective/published/filed dates near the end of the corpus.
    ("9/2/2015", (527295, 527303), datetime.date(2015, 9, 2)),
    ("3/1/2016", (527309, 527317), datetime.date(2016, 3, 1)),
    ("August 31, 2012", (531295, 531310), datetime.date(2012, 8, 31)),
    ("09/02/2015", (535820, 535830), datetime.date(2015, 9, 2)),
    ("August 3rd, 2015", (535850, 535866), datetime.date(2015, 8, 3)),
    ("12/2/08", (552036, 552043), datetime.date(2008, 12, 2)),
    ("1/2/09", (552055, 552061), datetime.date(2009, 1, 2)),
    ("12/18/91", (552179, 552187), datetime.date(1991, 12, 18)),
    ("4/1/92", (552192, 552198), datetime.date(1992, 4, 1)),
    ("8/31/92", (552210, 552217), datetime.date(1992, 8, 31)),
]

FORBIDDEN = [
    ("1/2", (94891, 94894)),
    ("8-1/2", (492931, 492936)),
    ("1-1/2", (513156, 513161)),
    ("3-4", (419673, 419676)),
    ("4-14", (541435, 541439)),
    ("08-24-101", (552003, 552012)),
]

KNOWN_FALSE_POSITIVES = [
    ("following may", (21591, 21604)),
    ("following may", (102929, 102942)),
    ("7-10", (463245, 463249)),
    ("a second", (347048, 347056)),
    ("January 1 , 3 Monday", (280883, 280903)),
    ("last Monday of May, July 4 , 1 Monday", (280944, 280981)),
    ("4 Thursday", (281046, 281056)),
    ("4 Friday", (281070, 281078)),
]

DATA = {
    "id": "test_data_560k",
    "source_hint": "datefinder tests/test_data.txt",
    "gold_status": "broad_sample",
    "text": None,
    "cases": [
        {
            "id": "document",
            "mode": "document",
            "source": "dataset",
            "assertion": "contains",
            "expected": MATCHED_TEXT,
            "forbidden": FORBIDDEN,
            "config": {
                "infer_datetimes": False,
                "return_matched_text": True,
            },
            "tags": ("document",),
        },
    ],
}
