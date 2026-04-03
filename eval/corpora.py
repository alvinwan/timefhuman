import datetime
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPORA_DIR = REPO_ROOT / ".eval_corpora"
DATEFINDER_ROOT = Path(os.environ.get("DATEFINDER_ROOT", "/tmp/datefinder"))


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
    ("ayer", (254, 258), datetime.date(2018, 8, 3)),
    ("mañana", (279, 285), datetime.date(2018, 8, 5)),
    ("dans 2 jours", (307, 319), datetime.timedelta(days=2)),
    ("31/08/2012 to 30/08/2013", (345, 369), (datetime.date(2012, 8, 31), datetime.date(2013, 8, 30))),
    (
        "Tue, 23 Apr 1996 13:28:27 -0400",
        (376, 407),
        datetime.datetime(1996, 4, 23, 13, 28, 27, tzinfo=datetime.timezone(datetime.timedelta(hours=-4))),
    ),
    ("for the past 40 minutes", (416, 439), datetime.timedelta(minutes=-40)),
]

SEATTLE_HTML_76K_MATCHED_TEXT = [
    ("08-07-2013", (12812, 12822), datetime.date(2013, 8, 7)),
    ("08-07-2013", (13302, 13312), datetime.date(2013, 8, 7)),
    ("08-07-2013", (13554, 13564), datetime.date(2013, 8, 7)),
    ("08-07-2013", (14053, 14063), datetime.date(2013, 8, 7)),
    ("08-07-2013", (14598, 14608), datetime.date(2013, 8, 7)),
    ("08-07-2013", (15087, 15097), datetime.date(2013, 8, 7)),
    ("08-07-2013", (15576, 15586), datetime.date(2013, 8, 7)),
    ("08-07-2013", (16086, 16096), datetime.date(2013, 8, 7)),
    ("08-07-2013", (16625, 16635), datetime.date(2013, 8, 7)),
    ("08-07-2013", (17304, 17314), datetime.date(2013, 8, 7)),
    ("08-07-2013", (17484, 17494), datetime.date(2013, 8, 7)),
    ("08-07-2013", (17693, 17703), datetime.date(2013, 8, 7)),
    ("7-10-2013", (17851, 17860), datetime.date(2013, 7, 10)),
    ("08-07-2013", (18039, 18049), datetime.date(2013, 8, 7)),
    ("08-07-2013", (18233, 18243), datetime.date(2013, 8, 7)),
    ("08-07-2013", (18498, 18508), datetime.date(2013, 8, 7)),
    ("08-07-2013", (19810, 19820), datetime.date(2013, 8, 7)),
    ("08-07-2013", (20002, 20012), datetime.date(2013, 8, 7)),
    ("08-07-2013", (20267, 20277), datetime.date(2013, 8, 7)),
    ("08-07-2013", (21418, 21428), datetime.date(2013, 8, 7)),
    ("08-07-2013", (21601, 21611), datetime.date(2013, 8, 7)),
    ("08-07-2013", (21783, 21793), datetime.date(2013, 8, 7)),
    ("08-07-2013", (21982, 21992), datetime.date(2013, 8, 7)),
    ("08-07-2013", (22245, 22255), datetime.date(2013, 8, 7)),
    ("6-3-2014", (23694, 23702), datetime.date(2014, 6, 3)),
    ("08-07-2013", (24978, 24988), datetime.date(2013, 8, 7)),
    ("08-07-2013", (25158, 25168), datetime.date(2013, 8, 7)),
    ("08-07-2013", (25342, 25352), datetime.date(2013, 8, 7)),
    ("08-07-2013", (25528, 25538), datetime.date(2013, 8, 7)),
    ("08-07-2013", (25869, 25879), datetime.date(2013, 8, 7)),
    ("08-07-2013", (26130, 26140), datetime.date(2013, 8, 7)),
    ("08-07-2013", (27582, 27592), datetime.date(2013, 8, 7)),
    ("08-07-2013", (27762, 27772), datetime.date(2013, 8, 7)),
    ("7-10-2013", (27924, 27933), datetime.date(2013, 7, 10)),
    ("7-10-2013", (28107, 28116), datetime.date(2013, 7, 10)),
    ("7-10-2013", (28395, 28404), datetime.date(2013, 7, 10)),
    ("08-07-2013", (28617, 28627), datetime.date(2013, 8, 7)),
    ("08-07-2013", (28811, 28821), datetime.date(2013, 8, 7)),
    ("08-07-2013", (29840, 29850), datetime.date(2013, 8, 7)),
    ("7-10-2013", (29996, 30005), datetime.date(2013, 7, 10)),
    ("08-07-2013", (30267, 30277), datetime.date(2013, 8, 7)),
    ("7-10-2013", (30429, 30438), datetime.date(2013, 7, 10)),
    ("08-07-2013", (31349, 31359), datetime.date(2013, 8, 7)),
    ("7-10-2013", (31513, 31522), datetime.date(2013, 7, 10)),
    ("08-07-2013", (31725, 31735), datetime.date(2013, 8, 7)),
    ("08-07-2013", (31921, 31931), datetime.date(2013, 8, 7)),
    ("08-07-2013", (32114, 32124), datetime.date(2013, 8, 7)),
    ("08-07-2013", (32391, 32401), datetime.date(2013, 8, 7)),
    ("7-10-2013", (32556, 32565), datetime.date(2013, 7, 10)),
    ("08-07-2013", (33816, 33826), datetime.date(2013, 8, 7)),
    ("7-10-2013", (34028, 34037), datetime.date(2013, 7, 10)),
    ("7-10-2013", (34239, 34248), datetime.date(2013, 7, 10)),
    ("Wed., Jan 6 2016 at 10:13AM", (39898, 39925), datetime.datetime(2016, 1, 6, 10, 13)),
    ("7-11pm", (45310, 45316), (datetime.time(19, 0), datetime.time(23, 0))),
    ("2013-01-23", (49125, 49135), datetime.date(2013, 1, 23)),
]

CORPUS_FILES = {
    "core_corpus": {
        "cache_name": "core_corpus.txt",
        "datefinder_relpath": ("bench", "corpus_core.txt"),
        "download_url": "https://raw.githubusercontent.com/akoumjian/datefinder/master/bench/corpus_core.txt",
    },
    "seattle_html_76k": {
        "cache_name": "seattle_weekly.html",
        "datefinder_relpath": ("tests", "seattle_weekly.html"),
        "download_url": "https://raw.githubusercontent.com/akoumjian/datefinder/master/tests/seattle_weekly.html",
    },
    "test_data_560k": {
        "cache_name": "test_data.txt",
        "datefinder_relpath": ("tests", "test_data.txt"),
        "download_url": "https://raw.githubusercontent.com/akoumjian/datefinder/master/tests/test_data.txt",
    },
}

CORPORA = {
    "core_corpus": {
        "id": "core_corpus",
        "source_hint": "datefinder bench/corpus_core.txt",
        "gold_status": "full",
        "text": CORE_CORPUS_TEXT,
        "expected": CORE_CORPUS_MATCHED_TEXT,
        "policy": None,
    },
    "seattle_html_76k": {
        "id": "seattle_html_76k",
        "source_hint": "datefinder tests/seattle_weekly.html",
        "gold_status": "full",
        "text": None,
        "expected": SEATTLE_HTML_76K_MATCHED_TEXT,
        "policy": "eval/seattle_html_76k.policy.md",
    },
    "test_data_560k": {
        "id": "test_data_560k",
        "source_hint": "datefinder tests/test_data.txt",
        "gold_status": "sample_only",
        "text": None,
        "expected": None,
        "policy": None,
    },
}


def corpora_dir():
    return Path(os.environ.get("TIMEFHUMAN_CORPORA_DIR", DEFAULT_CORPORA_DIR))


def resolve_corpus_path(name: str):
    info = CORPUS_FILES[name]
    datefinder_path = DATEFINDER_ROOT.joinpath(*info["datefinder_relpath"])
    if datefinder_path.exists():
        return datefinder_path

    cached_path = corpora_dir() / info["cache_name"]
    if cached_path.exists():
        return cached_path

    return None


def load_corpus_text(name: str):
    text = CORPORA[name]["text"]
    if text is not None:
        return text

    path = resolve_corpus_path(name)
    if path is None:
        return None
    return path.read_text(encoding="utf-8", errors="ignore")
