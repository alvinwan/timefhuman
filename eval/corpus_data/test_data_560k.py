import datetime

from eval.corpus_data._shared import localized_datetime


MATCHED_TEXT = [
    ("11:00 a.m., Pacific Time, January 13, 2016", (1914, 1956), localized_datetime("US/Pacific", 2016, 1, 13, 11, 0)),
    ("5:00 p.m. Pacific\nTime, January 8, 2016", (12858, 12897), localized_datetime("US/Pacific", 2016, 1, 8, 17, 0)),
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
    ("3rd Monday in January", (26838, 26859), datetime.date(2018, 1, 15)),
    ("3rd Monday in February", (26884, 26906), datetime.date(2018, 2, 19)),
    ("1st Monday in September", (26979, 27002), datetime.date(2018, 9, 3)),
    ("4th Thursday of November", (27050, 27074), datetime.date(2018, 11, 22)),
    ("between 9:00 a.m. and 3:30 p.m", (72939, 72969), (datetime.time(9, 0), datetime.time(15, 30))),
    ("7 AM to 5 PM", (363423, 363435), (datetime.time(7, 0), datetime.time(17, 0))),
    (
        "6:00 pm Saturday to 6:00 am Monday",
        (510499, 510533),
        (datetime.datetime(2018, 8, 4, 18, 0), datetime.datetime(2018, 8, 6, 6, 0)),
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
]

FORBIDDEN = [
    ("1/2", (94891, 94894)),
    ("8-1/2", (492931, 492936)),
    ("1-1/2", (513156, 513161)),
    ("3-4", (419673, 419676)),
    ("4-14", (541435, 541439)),
    ("08-24-101", (552003, 552012)),
]

DATA = {
    "id": "test_data_560k",
    "source_hint": "datefinder tests/test_data.txt",
    "gold_status": "sample",
    "text": None,
    "expected": MATCHED_TEXT,
    "forbidden": FORBIDDEN,
}
