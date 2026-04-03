import datetime

import pytz

from timefhuman import Direction


def localized_datetime(tz_name, *parts):
    return pytz.timezone(tz_name).localize(datetime.datetime(*parts))


DEFAULT_CASES = [
    {"id": "time_5p", "text": "5p", "expected": [datetime.datetime(2018, 8, 4, 17, 0)]},
    {
        "id": "time_3p_est",
        "text": "3p EST",
        "expected": [localized_datetime("US/Michigan", 2018, 8, 4, 15, 0)],
    },
    {"id": "date_july_2019", "text": "July 2019", "expected": [datetime.datetime(2019, 7, 1, 0, 0)]},
    {"id": "date_7_17_18", "text": "7-17-18", "expected": [datetime.datetime(2018, 7, 17, 0, 0)]},
    {"id": "date_2018_7_17", "text": "2018-7-17", "expected": [datetime.datetime(2018, 7, 17, 0, 0)]},
    {"id": "date_08_07_2013_dot", "text": "08.07.2013", "expected": [datetime.datetime(2013, 8, 7, 0, 0)]},
    {"id": "date_2013_08_07_dot", "text": "2013.08.07", "expected": [datetime.datetime(2013, 8, 7, 0, 0)]},
    {"id": "date_7_2018", "text": "7/2018", "expected": [datetime.datetime(2018, 7, 1, 0, 0)]},
    {"id": "date_wed_25_jun", "text": "Wed 25 Jun", "expected": [datetime.datetime(2018, 6, 25, 0, 0)]},
    {
        "id": "datetime_july_17_2018_3pm_at",
        "text": "July 17, 2018 at 3p.m.",
        "expected": [datetime.datetime(2018, 7, 17, 15, 0)],
    },
    {
        "id": "datetime_july_17_2018_3pm",
        "text": "July 17, 2018 3 p.m.",
        "expected": [datetime.datetime(2018, 7, 17, 15, 0)],
    },
    {"id": "datetime_3pm_on_july_17", "text": "3PM on July 17", "expected": [datetime.datetime(2018, 7, 17, 15, 0)]},
    {"id": "datetime_july_17_at_3", "text": "July 17 at 3", "expected": [datetime.datetime(2018, 7, 17, 3, 0)]},
    {"id": "datetime_numeric_3pm", "text": "7/17/18 3:00 p.m.", "expected": [datetime.datetime(2018, 7, 17, 15, 0)]},
    {"id": "datetime_3pm_today", "text": "3 p.m. today", "expected": [datetime.datetime(2018, 8, 4, 15, 0)]},
    {"id": "datetime_tomorrow_3p", "text": "Tomorrow 3p", "expected": [datetime.datetime(2018, 8, 5, 15, 0)]},
    {"id": "datetime_3p_tomorrow", "text": "3p tomorrow", "expected": [datetime.datetime(2018, 8, 5, 15, 0)]},
    {"id": "datetime_yesterday_3p", "text": "yesterday 3p", "expected": [datetime.datetime(2018, 8, 3, 15, 0)]},
    {"id": "datetime_july_3rd", "text": "July 3rd", "expected": [datetime.datetime(2018, 7, 3, 0, 0)]},
    {"id": "range_date_numeric", "text": "7/17-7/18", "expected": [(datetime.datetime(2018, 7, 17), datetime.datetime(2018, 7, 18))]},
    {"id": "range_date_month", "text": "July 17-18", "expected": [(datetime.datetime(2018, 7, 17), datetime.datetime(2018, 7, 18))]},
    {
        "id": "range_date_month_year_comma",
        "text": "June 11-16, 2026",
        "expected": [(datetime.datetime(2026, 6, 11), datetime.datetime(2026, 6, 16))],
    },
    {
        "id": "range_date_month_year",
        "text": "June 11-16 2026",
        "expected": [(datetime.datetime(2026, 6, 11), datetime.datetime(2026, 6, 16))],
    },
    {"id": "range_time_basic", "text": "3p -4p", "expected": [(datetime.datetime(2018, 8, 4, 15, 0), datetime.datetime(2018, 8, 4, 16, 0))]},
    {
        "id": "range_time_tz",
        "text": "3p -4p PDT",
        "expected": [
            (
                localized_datetime("US/Pacific", 2018, 8, 4, 15, 0),
                localized_datetime("US/Pacific", 2018, 8, 4, 16, 0),
            )
        ],
    },
    {
        "id": "range_time_cross_midnight",
        "text": "6:00 pm - 12:00 am",
        "expected": [(datetime.datetime(2018, 8, 4, 18, 0), datetime.datetime(2018, 8, 5, 0, 0))],
    },
    {
        "id": "range_time_force_date",
        "text": "8/4 6:00 pm - 8/4 12:00 am",
        "expected": [(datetime.datetime(2018, 8, 4, 18, 0), datetime.datetime(2018, 8, 4, 0, 0))],
    },
    {"id": "range_time_to_next_day", "text": "11PM to 1AM", "expected": [(datetime.datetime(2018, 8, 4, 23, 0), datetime.datetime(2018, 8, 5, 1, 0))]},
    {
        "id": "range_datetime_numeric",
        "text": "7/17 3 pm- 7/19 2 pm",
        "expected": [(datetime.datetime(2018, 7, 17, 15, 0), datetime.datetime(2018, 7, 19, 14, 0))],
    },
    {
        "id": "range_datetime_months",
        "text": "Jun 28 5:00 PM - Aug 02 7:00 PM",
        "expected": [(datetime.datetime(2018, 6, 28, 17, 0), datetime.datetime(2018, 8, 2, 19, 0))],
    },
    {
        "id": "range_datetime_months_2019",
        "text": "Jun 28 2019 5:00 PM - Aug 02 2019 7:00 PM",
        "expected": [(datetime.datetime(2019, 6, 28, 17, 0), datetime.datetime(2019, 8, 2, 19, 0))],
    },
    {
        "id": "range_datetime_numeric_months",
        "text": "6/28 5:00 PM - 8/02 7:00 PM",
        "expected": [(datetime.datetime(2018, 6, 28, 17, 0), datetime.datetime(2018, 8, 2, 19, 0))],
    },
    {
        "id": "range_datetime_numeric_months_2019",
        "text": "6/28/2019 5:00 PM - 8/02/2019 7:00 PM",
        "expected": [(datetime.datetime(2019, 6, 28, 17, 0), datetime.datetime(2019, 8, 2, 19, 0))],
    },
    {
        "id": "choice_july_4_or_5_3pm",
        "text": "July 4th or 5th at 3PM",
        "expected": [[datetime.datetime(2018, 7, 4, 15, 0), datetime.datetime(2018, 7, 5, 15, 0)]],
    },
    {
        "id": "choice_tomorrow_wed_fri",
        "text": "tomorrow noon,Wed 3 p.m.,Fri 11 AM",
        "expected": [[
            datetime.datetime(2018, 8, 5, 12, 0),
            datetime.datetime(2018, 8, 8, 15, 0),
            datetime.datetime(2018, 8, 10, 11, 0),
        ]],
    },
    {
        "id": "choice_sentence_two_options",
        "text": "Are you free this Wed at 3p? Or maybe Fri at 5p?",
        "expected": [datetime.datetime(2018, 8, 8, 15, 0), datetime.datetime(2018, 8, 10, 17, 0)],
    },
    {
        "id": "choice_of_ranges",
        "text": "7/17 4-5 PM or 5-6 PM today",
        "expected": [[
            (datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
            (datetime.datetime(2018, 8, 4, 17, 0), datetime.datetime(2018, 8, 4, 18, 0)),
        ]],
    },
    {"id": "duration_30_minutes", "text": "30 minutes", "expected": [datetime.datetime(2018, 8, 4, 14, 30)]},
    {
        "id": "duration_range_30_40_mins",
        "text": "30-40 mins",
        "expected": [(datetime.datetime(2018, 8, 4, 14, 30), datetime.datetime(2018, 8, 4, 14, 40))],
    },
    {
        "id": "duration_choice_1_or_2_days",
        "text": "1 or 2 days",
        "expected": [[datetime.datetime(2018, 8, 5, 14, 0), datetime.datetime(2018, 8, 6, 14, 0)]],
    },
    {"id": "duration_in_1_year", "text": "in 1 year", "expected": [datetime.datetime(2019, 8, 4, 14, 0)]},
    {"id": "duration_1_year_ago", "text": "1 year ago", "expected": [datetime.datetime(2017, 8, 4, 14, 0)]},
    {
        "id": "iso_datetime",
        "text": "2022-12-27T09:15:01.002",
        "expected": [datetime.datetime(2022, 12, 27, 9, 15, 1, 2)],
    },
]


NO_INFERENCE_CASES = [
    {"id": "empty", "text": "", "expected": []},
    {"id": "time_5p", "text": "5p", "expected": [datetime.time(hour=17, minute=0)]},
    {"id": "time_3_oclock_pm", "text": "3 o'clock pm", "expected": [datetime.time(hour=15, minute=0)]},
    {
        "id": "time_5p_eastern_time",
        "text": "5p Eastern Time",
        "expected": [datetime.time(hour=17, minute=0, tzinfo=pytz.timezone("US/Michigan"))],
    },
    {"id": "date_july_2019", "text": "July 2019", "expected": [datetime.date(2019, 7, 1)]},
    {"id": "date_sunday_7_7_2019", "text": "Sunday 7/7/2019", "expected": [datetime.date(2019, 7, 7)]},
    {"id": "date_1_1_95", "text": "1/1/95", "expected": [datetime.date(1995, 1, 1)]},
    {"id": "date_08_07_2013_dot", "text": "08.07.2013", "expected": [datetime.date(2013, 8, 7)]},
    {"id": "date_wed_25_jun", "text": "Wed 25 Jun", "expected": [datetime.date(2018, 6, 25)]},
    {"id": "date_1_3_4_invalid", "text": "1.3.4", "expected": []},
    {"id": "range_date_numeric", "text": "7/17-7/18", "expected": [(datetime.date(2018, 7, 17), datetime.date(2018, 7, 18))]},
    {"id": "range_date_month", "text": "July 17-18", "expected": [(datetime.date(2018, 7, 17), datetime.date(2018, 7, 18))]},
    {
        "id": "range_date_month_year_comma",
        "text": "June 11-16, 2026",
        "expected": [(datetime.date(2026, 6, 11), datetime.date(2026, 6, 16))],
    },
    {
        "id": "range_date_month_year",
        "text": "June 11-16 2026",
        "expected": [(datetime.date(2026, 6, 11), datetime.date(2026, 6, 16))],
    },
    {
        "id": "range_date_ddmmyyyy",
        "text": "31/08/2012 to 30/08/2013",
        "expected": [(datetime.date(2012, 8, 31), datetime.date(2013, 8, 30))],
    },
    {"id": "range_time_basic", "text": "3p -4p", "expected": [(datetime.time(15, 0), datetime.time(16, 0))]},
    {"id": "range_time_distributed_meridiem", "text": "3-4p", "expected": [(datetime.time(15, 0), datetime.time(16, 0))]},
    {"id": "duration_30_minutes", "text": "30 minutes", "expected": [datetime.timedelta(minutes=30)]},
    {"id": "duration_30_mins", "text": "30 mins", "expected": [datetime.timedelta(minutes=30)]},
    {"id": "duration_2_hours", "text": "2 hours", "expected": [datetime.timedelta(hours=2)]},
    {"id": "duration_2_hours_30_minutes", "text": "2 hours 30 minutes", "expected": [datetime.timedelta(hours=2, minutes=30)]},
    {
        "id": "duration_2_hours_and_30_minutes",
        "text": "2 hours and 30 minutes",
        "expected": [datetime.timedelta(hours=2, minutes=30)],
    },
    {"id": "duration_2h30m", "text": "2h30m", "expected": [datetime.timedelta(hours=2, minutes=30)]},
    {"id": "duration_1_day_and_hour", "text": "1 day and an hour", "expected": [datetime.timedelta(days=1, hours=1)]},
    {"id": "duration_1_5_hours", "text": "1.5 hours", "expected": [datetime.timedelta(hours=1, minutes=30)]},
    {"id": "duration_1_5h", "text": "1.5h", "expected": [datetime.timedelta(hours=1, minutes=30)]},
    {"id": "duration_in_five_minutes", "text": "in five minutes", "expected": [datetime.timedelta(minutes=5)]},
    {"id": "duration_in_3_days", "text": "in 3 days", "expected": [datetime.timedelta(days=3)]},
    {"id": "duration_for_3_days", "text": "for 3 days", "expected": [datetime.timedelta(days=3)]},
    {"id": "duration_past_40_minutes", "text": "past 40 minutes", "expected": [datetime.timedelta(minutes=-40)]},
    {
        "id": "duration_for_the_past_40_minutes",
        "text": "for the past 40 minutes",
        "expected": [datetime.timedelta(minutes=-40)],
    },
    {"id": "duration_awk_invalid", "text": "awk", "expected": []},
    {"id": "duration_a_wk", "text": "a wk", "expected": [datetime.timedelta(days=7)]},
    {"id": "duration_thirty_two_hours", "text": "thirty two hours", "expected": [datetime.timedelta(hours=32)]},
    {"id": "duration_in_1_year", "text": "in 1 year", "expected": [datetime.timedelta(days=365)]},
    {"id": "duration_1_year_ago", "text": "1 year ago", "expected": [datetime.timedelta(days=-365)]},
    {"id": "duration_range_30_40_mins", "text": "30-40 mins", "expected": [(datetime.timedelta(minutes=30), datetime.timedelta(minutes=40))]},
    {"id": "duration_choice_1_or_2_days", "text": "1 or 2 days", "expected": [[datetime.timedelta(days=1), datetime.timedelta(days=2)]]},
    {"id": "modifier_next_monday", "text": "next Monday", "expected": [datetime.date(2018, 8, 6)]},
    {"id": "modifier_this_monday", "text": "this Monday", "expected": [datetime.date(2018, 8, 6)]},
    {"id": "modifier_next_next_monday", "text": "next next Monday", "expected": [datetime.date(2018, 8, 13)]},
    {"id": "modifier_last_monday", "text": "last Monday", "expected": [datetime.date(2018, 7, 30)]},
    {"id": "modifier_next_july", "text": "next July", "expected": [datetime.date(2019, 7, 1)]},
    {"id": "modifier_last_july", "text": "last July", "expected": [datetime.date(2017, 7, 1)]},
    {"id": "modifier_last_wednesday_of_december", "text": "last Wednesday of December", "expected": [datetime.date(2018, 12, 26)]},
    {"id": "modifier_first_wednesday_of_december", "text": "first Wednesday of December", "expected": [datetime.date(2018, 12, 5)]},
    {"id": "modifier_second_wednesday_of_december", "text": "second Wednesday of December", "expected": [datetime.date(2018, 12, 12)]},
    {"id": "modifier_third_wednesday_of_december", "text": "third Wednesday of December", "expected": [datetime.date(2018, 12, 19)]},
    {"id": "modifier_fourth_wednesday_of_december", "text": "fourth Wednesday of December", "expected": [datetime.date(2018, 12, 26)]},
    {"id": "vernacular_afternoon", "text": "afternoon", "expected": [datetime.time(hour=15, minute=0)]},
    {"id": "vernacular_morning", "text": "morning", "expected": [datetime.time(hour=6, minute=0)]},
    {"id": "vernacular_evening", "text": "evening", "expected": [datetime.time(hour=18, minute=0)]},
    {"id": "vernacular_night", "text": "night", "expected": [datetime.time(hour=20, minute=0)]},
    {"id": "vernacular_today_night", "text": "today night", "expected": [datetime.datetime(2018, 8, 4, 20, 0)]},
    {"id": "vernacular_tonight", "text": "tonight", "expected": [datetime.datetime(2018, 8, 4, 20, 0)]},
    {"id": "vernacular_midnight", "text": "midnight", "expected": [datetime.time(hour=0, minute=0)]},
    {"id": "vernacular_midday", "text": "midday", "expected": [datetime.time(hour=12, minute=0)]},
    {"id": "prefixed_650pm", "text": "e 6:50PM", "expected": [datetime.time(hour=18, minute=50)]},
]


CUSTOM_CONFIG_CASES = [
    {
        "id": "custom_direction_next_mon",
        "config_kwargs": {"direction": Direction.next, "infer_datetimes": False},
        "text": "mon",
        "expected": [datetime.date(2018, 8, 6)],
    },
    {
        "id": "custom_direction_this_mon",
        "config_kwargs": {"direction": Direction.this, "infer_datetimes": False},
        "text": "mon",
        "expected": [datetime.date(2018, 8, 6)],
    },
    {
        "id": "custom_direction_previous_mon",
        "config_kwargs": {"direction": Direction.previous, "infer_datetimes": False},
        "text": "mon",
        "expected": [datetime.date(2018, 7, 30)],
    },
    {
        "id": "custom_infer_true_5p",
        "config_kwargs": {"infer_datetimes": True},
        "text": "5p",
        "expected": [datetime.datetime(2018, 8, 4, 17, 0)],
    },
    {
        "id": "custom_infer_false_5p",
        "config_kwargs": {"infer_datetimes": False},
        "text": "5p",
        "expected": [datetime.time(hour=17, minute=0)],
    },
    {
        "id": "custom_infer_true_1p_next_day",
        "config_kwargs": {"infer_datetimes": True},
        "text": "1p",
        "expected": [datetime.datetime(2018, 8, 5, 13, 0)],
    },
]


MATCHED_TEXT_CASES = [
    {
        "id": "matched_punctuated_full_date",
        "text": "September 30, 2019.",
        "expected": [("September 30, 2019", (0, 18), datetime.datetime(2019, 9, 30, 0, 0))],
    },
    {
        "id": "matched_sentence_two_options",
        "text": "How does 5p mon sound? Or maybe 4p tu?",
        "expected": [
            ("5p mon", (9, 15), datetime.datetime(2018, 8, 6, 17, 0)),
            ("4p tu", (32, 37), datetime.datetime(2018, 8, 7, 16, 0)),
        ],
    },
    {"id": "matched_ambiguous_number_ignored", "text": "There are 3 ways to do it", "expected": []},
    {"id": "matched_salmon_amnesty", "text": "salmon for 9 amnesty tickets", "expected": []},
    {"id": "matched_embedded_numeric_date", "text": "s 1/1/24 C", "expected": [("1/1/24", (2, 8), datetime.datetime(2024, 1, 1, 0, 0))]},
    {
        "id": "matched_compact_time_range",
        "text": "running from 7-11pm and featuring resident DJs",
        "expected": [("7-11pm", (13, 19), (datetime.datetime(2018, 8, 4, 19, 0), datetime.datetime(2018, 8, 4, 23, 0)))],
    },
    {"id": "matched_embedded_dash_date", "text": "foo 08-07-2013 bar", "expected": [("08-07-2013", (4, 14), datetime.datetime(2013, 8, 7, 0, 0))]},
    {"id": "matched_comment_dash_date", "text": "<!-- REMOVED 08-07-2013 -->", "expected": [("08-07-2013", (13, 23), datetime.datetime(2013, 8, 7, 0, 0))]},
    {"id": "matched_embedded_dot_date", "text": "foo 08.07.2013 bar", "expected": [("08.07.2013", (4, 14), datetime.datetime(2013, 8, 7, 0, 0))]},
    {
        "id": "matched_embedded_long_datetime",
        "text": "foo January 4th, 2017 at 8:00pm bar",
        "expected": [("January 4th, 2017 at 8:00pm", (4, 31), datetime.datetime(2017, 1, 4, 20, 0))],
    },
    {
        "id": "matched_two_adjacent_dates",
        "text": "foo 2024-11-09 tomorrow at noon bar",
        "expected": [
            ("2024-11-09", (4, 14), datetime.datetime(2024, 11, 9, 0, 0)),
            ("tomorrow at noon", (15, 31), datetime.datetime(2018, 8, 5, 12, 0)),
        ],
    },
    {"id": "matched_in_3_days", "text": "we start phase two in 3 days", "expected": [("in 3 days", (19, 28), datetime.datetime(2018, 8, 7, 14, 0))]},
    {"id": "matched_for_3_days", "text": "we waited for 3 days", "expected": [("for 3 days", (10, 20), datetime.datetime(2018, 8, 7, 14, 0))]},
    {
        "id": "matched_for_the_past_40_minutes",
        "text": "CR is 0 for the past 40 minutes",
        "expected": [("for the past 40 minutes", (8, 31), datetime.datetime(2018, 8, 4, 13, 20))],
    },
    {"id": "matched_invalid_dotted_version", "text": "foo 1.3.4 bar", "expected": []},
    {"id": "matched_css_dimensions", "text": "style='width:1px; height:1px;'", "expected": []},
    {"id": "matched_phone_number", "text": "telephone (253) 591-5252", "expected": []},
    {"id": "matched_section_label", "text": "Section 7.02B 7a. - e.", "expected": []},
    {"id": "matched_valid_7a", "text": "Meet at 7a.", "expected": [("7a", (8, 10), datetime.datetime(2018, 8, 5, 7, 0))]},
    {"id": "matched_valid_3h", "text": "Wait 3h please", "expected": [("3h", (5, 7), datetime.datetime(2018, 8, 4, 17, 0))]},
    {"id": "matched_invalid_90p", "text": "90p", "expected": []},
    {"id": "matched_invalid_4906_0", "text": "4906/0", "expected": []},
    {
        "id": "matched_rfc_822_datetime",
        "text": "Tue, 23 Apr 1996 13:28:27 -0400",
        "expected": [(
            "Tue, 23 Apr 1996 13:28:27 -0400",
            (0, 31),
            datetime.datetime(1996, 4, 23, 13, 28, 27, tzinfo=datetime.timezone(datetime.timedelta(hours=-4))),
        )],
    },
]


_DEFAULT_CASES_BY_ID = {case["id"]: case for case in DEFAULT_CASES}

SHORT_BENCHMARK_INPUT_IDS = [
    "time_5p",
    "time_3p_est",
    "date_july_2019",
    "date_7_17_18",
    "date_2018_7_17",
    "date_7_2018",
    "datetime_july_17_2018_3pm_at",
    "datetime_july_17_2018_3pm",
    "datetime_3pm_on_july_17",
    "datetime_july_17_at_3",
    "datetime_numeric_3pm",
    "datetime_3pm_today",
    "datetime_tomorrow_3p",
    "datetime_3p_tomorrow",
    "datetime_yesterday_3p",
    "datetime_july_3rd",
    "range_date_numeric",
    "range_date_month",
    "range_time_basic",
    "range_time_tz",
    "range_time_cross_midnight",
    "range_time_force_date",
    "range_time_to_next_day",
    "range_datetime_numeric",
    "range_datetime_months",
    "range_datetime_months_2019",
    "range_datetime_numeric_months",
    "range_datetime_numeric_months_2019",
    "choice_july_4_or_5_3pm",
    "choice_tomorrow_wed_fri",
    "choice_of_ranges",
    "duration_30_minutes",
    "duration_range_30_40_mins",
    "duration_choice_1_or_2_days",
    "duration_in_1_year",
    "duration_1_year_ago",
    "iso_datetime",
]

SHORT_EXACTNESS_IDS = [
    "date_july_2019",
    "date_2018_7_17",
    "datetime_july_17_2018_3pm_at",
    "datetime_3pm_today",
    "datetime_tomorrow_3p",
    "datetime_yesterday_3p",
    "datetime_july_3rd",
    "duration_in_1_year",
    "duration_1_year_ago",
    "iso_datetime",
]

SHORT_BENCHMARK_INPUTS = [_DEFAULT_CASES_BY_ID[case_id]["text"] for case_id in SHORT_BENCHMARK_INPUT_IDS]
SHORT_EXACTNESS_CASES = [
    {
        "id": case_id,
        "text": _DEFAULT_CASES_BY_ID[case_id]["text"],
        "expected": _DEFAULT_CASES_BY_ID[case_id]["expected"][0],
    }
    for case_id in SHORT_EXACTNESS_IDS
]

