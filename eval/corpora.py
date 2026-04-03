import datetime


CORE_CORPUS_TEXT = (
    "entries are due by January 4th, 2017 at 8:00pm\n"
    "created 01/15/2005 by ACME Inc. and associates\n"
    "we shipped on 2024-11-03 18:00 and archived on 2024-11-09\n"
    "tomorrow at noon we start phase two\n"
    "in 3 days we will finalize results\n"
    "we waited 20 days for delivery\n"
    "ayer recibimos el pago y mañana enviamos el contrato\n"
    "dans 2 jours la reunion est planifiee\n"
    "31/08/2012 to 30/08/2013\n"
    "Date: Tue, 23 Apr 1996 13:28:27 -0400\n"
    "CR is 0 for the past 40 minutes\n"
    "French 75 is a cocktail and should not be parsed as a date"
)

CORE_CORPUS_MATCHED_TEXT = [
    ("January 4th, 2017 at 8:00pm", (19, 46), datetime.datetime(2017, 1, 4, 20, 0)),
    ("01/15/2005", (55, 65), datetime.date(2005, 1, 15)),
    ("2024-11-03 18:00", (108, 124), datetime.datetime(2024, 11, 3, 18, 0)),
    ("2024-11-09", (141, 151), datetime.date(2024, 11, 9)),
    ("tomorrow at noon", (152, 168), datetime.datetime(2018, 8, 5, 12, 0)),
    ("in 3 days", (188, 197), datetime.timedelta(days=3)),
    ("20 days", (233, 240), datetime.timedelta(days=20)),
    ("31/08/2012 to 30/08/2013", (345, 369), (datetime.date(2012, 8, 31), datetime.date(2013, 8, 30))),
    (
        "Tue, 23 Apr 1996 13:28:27 -0400",
        (376, 407),
        datetime.datetime(1996, 4, 23, 13, 28, 27, tzinfo=datetime.timezone(datetime.timedelta(hours=-4))),
    ),
    ("for the past 40 minutes", (416, 439), datetime.timedelta(minutes=-40)),
]

CORPORA = {
    "core_corpus": {
        "id": "core_corpus",
        "source_hint": "datefinder bench/corpus_core.txt",
        "gold_status": "full",
        "text": CORE_CORPUS_TEXT,
        "expected": CORE_CORPUS_MATCHED_TEXT,
    },
    "seattle_html_76k": {
        "id": "seattle_html_76k",
        "source_hint": "datefinder tests/seattle_weekly.html",
        "gold_status": "unscoped",
        "text": None,
        "expected": None,
    },
    "test_data_560k": {
        "id": "test_data_560k",
        "source_hint": "datefinder tests/test_data.txt",
        "gold_status": "sample_only",
        "text": None,
        "expected": None,
    },
}

