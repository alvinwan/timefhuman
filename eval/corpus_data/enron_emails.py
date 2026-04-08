import datetime

from eval.corpus_data._shared import fixed_offset


TZ_MINUS_0800 = fixed_offset(-480)
TZ_MINUS_0700 = fixed_offset(-420)

# Curated body-text snippets with per-message send times for relative-date resolution.
CONTEXT_MATCHED_TEXT_CASES = [
    {
        'source_path': 'kitchen-l/_americas/turbines/18.',
        'source_span': (792106649, 792106692),
        'sent_at': datetime.datetime(2001, 10, 3, 8, 24, 32, tzinfo=TZ_MINUS_0700),
        'text': "Let's discuss first thing tomorrow morning.",
        'expected': [
                ('tomorrow morning', (26, 42), datetime.datetime(2001, 10, 4, 6, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'kitchen-l/_americas/turbines/18.',
        'source_span': (792107847, 792107902),
        'sent_at': datetime.datetime(2001, 10, 3, 8, 24, 32, tzinfo=TZ_MINUS_0700),
        'text': 'Please review and forward comments by tomorrow morning.',
        'expected': [
                ('tomorrow morning', (38, 54), datetime.datetime(2001, 10, 4, 6, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'kitchen-l/_americas/turbines/18.',
        'source_span': (792111624, 792111702),
        'sent_at': datetime.datetime(2001, 10, 3, 8, 24, 32, tzinfo=TZ_MINUS_0700),
        'text': 'I would appreciate if you could reserve a conference room for today from 2-3p.',
        'expected': [
                ('today from 2-3p', (62, 77), (datetime.datetime(2001, 10, 3, 14, 0, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 10, 3, 15, 0, 0, tzinfo=TZ_MINUS_0700))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'kitchen-l/_americas/turbines/18.',
        'source_span': (792111891, 792111944),
        'sent_at': datetime.datetime(2001, 10, 3, 8, 24, 32, tzinfo=TZ_MINUS_0700),
        'text': 'I would like to reserve a conference room from 9a-4p.',
        'expected': [
                ('9a-4p', (47, 52), (datetime.datetime(2001, 10, 3, 9, 0, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 10, 3, 16, 0, 0, tzinfo=TZ_MINUS_0700))),
            ],
    },
    {
        'source_path': 'stokley-c/chris_stokley/murray/51.',
        'source_span': (1279308789, 1279308912),
        'sent_at': datetime.datetime(2001, 7, 24, 7, 30, 58, tzinfo=TZ_MINUS_0700),
        'text': 'We are setting up a meeting with CSC for this Wednesday to discuss the needs and start defining Iteration 2 of the project.',
        'expected': [
                ('this Wednesday', (41, 55), datetime.datetime(2001, 7, 25, 0, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'stokley-c/chris_stokley/murray/51.',
        'source_span': (1279310319, 1279310349),
        'sent_at': datetime.datetime(2001, 7, 24, 7, 30, 58, tzinfo=TZ_MINUS_0700),
        'text': '07/24/2001\n10:00 AM - 11:00 AM',
        'expected': [
                ('07/24/2001\n10:00 AM - 11:00 AM', (0, 30), (datetime.datetime(2001, 7, 24, 10, 0, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 7, 24, 11, 0, 0, tzinfo=TZ_MINUS_0700))),
            ],
    },
    {
        'source_path': 'stokley-c/chris_stokley/murray/8.',
        'source_span': (1279379889, 1279379942),
        'sent_at': datetime.datetime(2001, 10, 1, 17, 49, 14, tzinfo=TZ_MINUS_0700),
        'text': 'I think we have a meeting schedule for tomorrow 10/2.',
        'expected': [
                ('tomorrow 10/2', (39, 52), datetime.datetime(2001, 10, 2, 0, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'stokley-c/chris_stokley/murray/8.',
        'source_span': (1279383145, 1279383234),
        'sent_at': datetime.datetime(2001, 10, 1, 17, 49, 14, tzinfo=TZ_MINUS_0700),
        'text': 'I do have a few questions which I would like to discuss with you next week (9/24 - 9/26).',
        'expected': [
                ('9/24 - 9/26', (76, 87), (datetime.datetime(2001, 9, 24, 0, 0, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 9, 26, 0, 0, 0, tzinfo=TZ_MINUS_0700))),
            ],
    },
    {
        'source_path': 'kitchen-l/_americas/turbines/65.',
        'source_span': (792249453, 792249561),
        'sent_at': datetime.datetime(2001, 6, 18, 22, 56, 0, tzinfo=TZ_MINUS_0700),
        'text': 'I will call you tomorrow morning to answer any questions you have on the turbine report or other activities.',
        'expected': [
                ('tomorrow morning', (16, 32), datetime.datetime(2001, 6, 19, 6, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'kitchen-l/_americas/turbines/65.',
        'source_span': (792249562, 792249616),
        'sent_at': datetime.datetime(2001, 6, 18, 22, 56, 0, tzinfo=TZ_MINUS_0700),
        'text': 'I will also be in Houston all day Thursday and Friday.',
        'expected': [
                ('Thursday and Friday', (34, 53), [
                        datetime.datetime(2001, 6, 21, 0, 0, 0, tzinfo=TZ_MINUS_0700),
                        datetime.datetime(2001, 6, 22, 0, 0, 0, tzinfo=TZ_MINUS_0700),
                    ]),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'pereira-s/all_documents/87.',
        'source_span': (1026147099, 1026147141),
        'sent_at': datetime.datetime(2001, 2, 7, 3, 48, 0, tzinfo=TZ_MINUS_0800),
        'text': 'I hear any objections by tomorrow evening.',
        'expected': [
                ('tomorrow evening', (25, 41), datetime.datetime(2001, 2, 8, 18, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'stokley-c/chris_stokley/murray/47.',
        'source_span': (1279298379, 1279298448),
        'sent_at': datetime.datetime(2001, 7, 25, 14, 49, 20, tzinfo=TZ_MINUS_0700),
        'text': 'Please send me your status on these items by close of business today.',
        'expected': [
                ('close of business today', (45, 68), datetime.datetime(2001, 7, 25, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'kitchen-l/_americas/turbines/34.',
        'source_span': (775550542, 775550691),
        'sent_at': datetime.datetime(2001, 8, 30, 6, 58, 50, tzinfo=TZ_MINUS_0700),
        'text': 'Bob Shults and I will be attending an eNYMEX reception this Thursday, and John and Greg are still trying to coordinate a meeting with Bo and Vincent.',
        'expected': [
                ('this Thursday', (55, 68), datetime.datetime(2001, 8, 30, 0, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'schwieger-j/all_documents/58.',
        'source_span': (1129408702, 1129408767),
        'sent_at': datetime.datetime(2001, 3, 19, 1, 3, 0, tzinfo=TZ_MINUS_0800),
        'text': 'The boys and I are leaving for Colorado to go skiing this Friday.',
        'expected': [
                ('this Friday', (53, 64), datetime.datetime(2001, 3, 23, 0, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'scholtes-d/stf/2.',
        'source_span': (1123711333, 1123711406),
        'sent_at': datetime.datetime(2001, 10, 15, 12, 57, 51, tzinfo=TZ_MINUS_0700),
        'text': 'Please get back with your thought by next Wednesday so I can put together',
        'expected': [
                ('next Wednesday', (37, 51), datetime.datetime(2001, 10, 17, 0, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'stokley-c/chris_stokley/sent/209.',
        'source_span': (1280120357, 1280120445),
        'sent_at': datetime.datetime(2001, 5, 4, 11, 49, 52, tzinfo=TZ_MINUS_0700),
        'text': "Tentative target date for completion of Prelim's is next Thursday, and Finals on Friday.",
        'expected': [
                ('next Thursday', (52, 65), datetime.datetime(2001, 5, 10, 0, 0, 0, tzinfo=TZ_MINUS_0700)),
                ('Friday', (81, 87), datetime.datetime(2001, 5, 11, 0, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'kitchen-l/_americas/turbines/18.',
        'source_span': (792113371, 792113412),
        'sent_at': datetime.datetime(2001, 10, 3, 8, 24, 32, tzinfo=TZ_MINUS_0700),
        'text': 'Does anytime from 1-3p work for everyone.',
        'expected': [
                ('1-3p', (18, 22), (datetime.datetime(2001, 10, 3, 13, 0, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 10, 3, 15, 0, 0, tzinfo=TZ_MINUS_0700))),
            ],
    },
    {
        'source_path': 'kitchen-l/_americas/turbines/82.',
        'source_span': (792275974, 792276029),
        'sent_at': datetime.datetime(2001, 4, 10, 17, 21, 0, tzinfo=TZ_MINUS_0700),
        'text': 'did not pick up my mail until late yesterday afternoon.',
        'expected': [
                ('yesterday afternoon', (35, 54), datetime.datetime(2001, 4, 9, 15, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'allen-p/_sent_mail/109.',
        'source_span': (24959, 25012),
        'sent_at': datetime.datetime(2000, 10, 4, 9, 23, 0, tzinfo=TZ_MINUS_0700),
        'text': 'Date:  Wednesday, October 11th\n\n  Time:  2:30 - 3:30 ',
        'expected': [
                ('Wednesday, October 11th\n\n  Time:  2:30 - 3:30', (7, 52), (datetime.datetime(2000, 10, 11, 14, 30, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2000, 10, 11, 15, 30, 0, tzinfo=TZ_MINUS_0700))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'allen-p/_sent_mail/115.',
        'source_span': (31659, 31734),
        'sent_at': datetime.datetime(2000, 9, 28, 6, 17, 0, tzinfo=TZ_MINUS_0700),
        'text': 'As we discussed yesterday, I am concerned there may have been an attempt to',
        'expected': [
                ('yesterday,', (16, 26), datetime.datetime(2000, 9, 27, 0, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'arora-h/all_documents/28.',
        'source_span': (17086247, 17086305),
        'sent_at': datetime.datetime(2001, 1, 17, 1, 46, 0, tzinfo=TZ_MINUS_0800),
        'text': 'Could you please confirm 1:30 pm today, on the 27th floor.',
        'expected': [
                ('1:30 pm today', (25, 38), datetime.datetime(2001, 1, 17, 13, 30, 0, tzinfo=TZ_MINUS_0800)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'badeer-r/_sent_mail/29.',
        'source_span': (20761281, 20761355),
        'sent_at': datetime.datetime(2000, 7, 11, 9, 17, 0, tzinfo=TZ_MINUS_0700),
        'text': 'I will be out of the office this Thursday and Friday (7-13/14) to attend a',
        'expected': [
                ('this Thursday and Friday (7-13/14)', (28, 62), [
                        datetime.datetime(2000, 7, 13, 0, 0, 0, tzinfo=TZ_MINUS_0700),
                        datetime.datetime(2000, 7, 14, 0, 0, 0, tzinfo=TZ_MINUS_0700),
                    ]),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'bailey-s/deleted_items/114.',
        'source_span': (23030184, 23030280),
        'sent_at': datetime.datetime(2002, 1, 24, 12, 43, 0, tzinfo=TZ_MINUS_0800),
        'text': 'As mentioned in my voice mail -- I can meet with you anytime this afternoon -- how about 3:30pm.',
        'expected': [
                ('afternoon', (66, 75), datetime.datetime(2002, 1, 24, 15, 0, 0, tzinfo=TZ_MINUS_0800)),
                ('3:30pm', (89, 95), datetime.datetime(2002, 1, 24, 15, 30, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'bass-e/_sent_mail/100.',
        'source_span': (23941163, 23941234),
        'sent_at': datetime.datetime(2000, 12, 7, 6, 2, 0, tzinfo=TZ_MINUS_0800),
        'text': 'Let me know what you get and are you spending the night tomorrow night?',
        'expected': [
                ('tomorrow night', (56, 70), datetime.datetime(2000, 12, 8, 20, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'bass-e/_sent_mail/100.',
        'source_span': (23941235, 23941299),
        'sent_at': datetime.datetime(2000, 12, 7, 6, 2, 0, tzinfo=TZ_MINUS_0800),
        'text': 'Jake is having surgery tomorrow morning so say a prayer for him.',
        'expected': [
                ('tomorrow morning', (23, 39), datetime.datetime(2000, 12, 8, 6, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'baughman-d/all_documents/103.',
        'source_span': (45493280, 45493345),
        'sent_at': datetime.datetime(2001, 1, 23, 0, 38, 0, tzinfo=TZ_MINUS_0800),
        'text': 'You should be able to activate your password by lunch time today.',
        'expected': [
                ('lunch time today', (48, 64), datetime.datetime(2001, 1, 23, 12, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'beck-s/2001_plan/2.',
        'source_span': (55706860, 55706913),
        'sent_at': datetime.datetime(2000, 11, 7, 6, 10, 0, tzinfo=TZ_MINUS_0800),
        'text': 'Please submit this explanation by tomorrow afternoon.',
        'expected': [
                ('tomorrow afternoon', (34, 52), datetime.datetime(2000, 11, 8, 15, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'beck-s/_sent_mail/1.',
        'source_span': (55715267, 55715334),
        'sent_at': datetime.datetime(2000, 12, 12, 9, 34, 0, tzinfo=TZ_MINUS_0800),
        'text': 'I will be in Houston the week after Christmas (12/26-12/29) and was',
        'expected': [
                ('12/26-12/29', (47, 58), (datetime.datetime(2000, 12, 26, 0, 0, 0, tzinfo=TZ_MINUS_0800), datetime.datetime(2000, 12, 29, 0, 0, 0, tzinfo=TZ_MINUS_0800))),
            ],
    },
    {
        'source_path': 'beck-s/_sent_mail/1001.',
        'source_span': (55724172, 55724223),
        'sent_at': datetime.datetime(2001, 1, 11, 2, 3, 0, tzinfo=TZ_MINUS_0800),
        'text': 'Date: Friday, January 12, 2001\nTime: 8:30 - 2:00 PM',
        'expected': [
                ('Friday, January 12, 2001\nTime: 8:30 - 2:00 PM', (6, 51), (datetime.datetime(2001, 1, 12, 8, 30, 0, tzinfo=TZ_MINUS_0800), datetime.datetime(2001, 1, 12, 14, 0, 0, tzinfo=TZ_MINUS_0800))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'benson-r/all_documents/14.',
        'source_span': (83932637, 83932683),
        'sent_at': datetime.datetime(2001, 5, 8, 4, 34, 0, tzinfo=TZ_MINUS_0700),
        'text': 'DATE CONFIRMATION - May 18 (9:30 am - 3:00 pm)',
        'expected': [
                ('May 18 (9:30 am - 3:00 pm)', (20, 46), (datetime.datetime(2001, 5, 18, 9, 30, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 5, 18, 15, 0, 0, tzinfo=TZ_MINUS_0700))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'benson-r/all_documents/18.',
        'source_span': (83939197, 83939222),
        'sent_at': datetime.datetime(2001, 5, 8, 17, 55, 0, tzinfo=TZ_MINUS_0700),
        'text': 'May. 11 - 10:30 -11:30 AM',
        'expected': [
                ('May. 11 - 10:30 -11:30 AM', (0, 25), (datetime.datetime(2001, 5, 11, 10, 30, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 5, 11, 11, 30, 0, tzinfo=TZ_MINUS_0700))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'brawner-s/_sent_mail/15.',
        'source_span': (94617798, 94617841),
        'sent_at': datetime.datetime(2001, 4, 24, 14, 42, 0, tzinfo=TZ_MINUS_0700),
        'text': 'Can I call you this evening on my way home?',
        'expected': [
                ('evening', (20, 27), datetime.datetime(2001, 4, 24, 18, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'buy-r/_sent_mail/119.',
        'source_span': (97175484, 97175520),
        'sent_at': datetime.datetime(2001, 1, 17, 0, 31, 0, tzinfo=TZ_MINUS_0800),
        'text': 'Tuesday, January 23rd\n3:00-4:00 p.m.',
        'expected': [
                ('Tuesday, January 23rd\n3:00-4:00 p.m.', (0, 36), (datetime.datetime(2001, 1, 23, 15, 0, 0, tzinfo=TZ_MINUS_0800), datetime.datetime(2001, 1, 23, 16, 0, 0, tzinfo=TZ_MINUS_0800))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'buy-r/_sent_mail/119.',
        'source_span': (97175852, 97175879),
        'sent_at': datetime.datetime(2001, 1, 17, 0, 31, 0, tzinfo=TZ_MINUS_0800),
        'text': 'Monday, Jan 22  4:00 - 5:00',
        'expected': [
                ('Monday, Jan 22  4:00 - 5:00', (0, 27), (datetime.datetime(2001, 1, 22, 16, 0, 0, tzinfo=TZ_MINUS_0800), datetime.datetime(2001, 1, 22, 17, 0, 0, tzinfo=TZ_MINUS_0800))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'cash-m/all_documents/117.',
        'source_span': (125077942, 125077972),
        'sent_at': datetime.datetime(2001, 1, 25, 3, 44, 0, tzinfo=TZ_MINUS_0800),
        'text': '01/26/2001\n01:30 PM - 02:30 PM',
        'expected': [
                ('01/26/2001\n01:30 PM - 02:30 PM', (0, 30), (datetime.datetime(2001, 1, 26, 13, 30, 0, tzinfo=TZ_MINUS_0800), datetime.datetime(2001, 1, 26, 14, 30, 0, tzinfo=TZ_MINUS_0800))),
            ],
    },
    {
        'source_path': 'crandell-s/deleted_items/11.',
        'source_span': (142093251, 142093284),
        'sent_at': datetime.datetime(2002, 2, 5, 10, 44, 24, tzinfo=TZ_MINUS_0800),
        'text': 'Please let me know by noon today.',
        'expected': [
                ('noon today', (22, 32), datetime.datetime(2002, 2, 5, 12, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'gilbertsmith-d/inbox/5.',
        'source_span': (412618197, 412618249),
        'sent_at': datetime.datetime(2002, 2, 6, 12, 52, 47, tzinfo=TZ_MINUS_0800),
        'text': 'Please RSVP by COB Friday (2/8), to Christine Meloro',
        'expected': [
                ('COB Friday (2/8)', (15, 31), datetime.datetime(2002, 2, 8, 17, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'holst-k/inbox/33.',
        'source_span': (522836096, 522836139),
        'sent_at': datetime.datetime(2001, 9, 25, 15, 35, 8, tzinfo=TZ_MINUS_0700),
        'text': 'Please respond by COB Thursday, Sept. 27th.',
        'expected': [
                ('COB Thursday, Sept. 27th', (18, 42), datetime.datetime(2001, 9, 27, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'lay-k/discussion_threads/169.',
        'source_span': (813094915, 813094978),
        'sent_at': datetime.datetime(2000, 9, 5, 7, 37, 0, tzinfo=TZ_MINUS_0700),
        'text': 'Please let me know if you have any comments by 5:00 p.m. today.',
        'expected': [
                ('5:00 p.m. today', (47, 62), datetime.datetime(2000, 9, 5, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'jones-t/all_documents/1267.',
        'source_span': (550007925, 550007983),
        'sent_at': datetime.datetime(2000, 4, 17, 2, 50, 0, tzinfo=TZ_MINUS_0700),
        'text': 'R.S.V.P. to Sylvia Hu x 36775 or email by Noon, Wed. 4/19.',
        'expected': [
                ('Noon, Wed. 4/19', (42, 57), datetime.datetime(2000, 4, 19, 12, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'jones-t/notes_inbox/3263.',
        'source_span': (571842663, 571842696),
        'sent_at': datetime.datetime(2001, 3, 1, 5, 22, 0, tzinfo=TZ_MINUS_0800),
        'text': 'Please R.S.V.P. by 5 p.m. Monday.',
        'expected': [
                ('5 p.m. Monday', (19, 32), datetime.datetime(2001, 3, 5, 17, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'zipper-a/all_documents/27.',
        'source_span': (1425332443, 1425332515),
        'sent_at': datetime.datetime(2000, 12, 11, 6, 15, 0, tzinfo=TZ_MINUS_0800),
        'text': 'By next Tuesday, I plan to send you our proposed agenda for the meeting.',
        'expected': [
                ('next Tuesday', (3, 15), datetime.datetime(2000, 12, 12, 0, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'sanders-r/sent_items/226.',
        'source_span': (1121678592, 1121678636),
        'sent_at': datetime.datetime(2001, 6, 5, 9, 43, 0, tzinfo=TZ_MINUS_0700),
        'text': 'What about lunch? Thurs or Fri of next week?',
        'expected': [
                ('Thurs or Fri of next week', (18, 43), [
                        datetime.datetime(2001, 6, 7, 0, 0, 0, tzinfo=TZ_MINUS_0700),
                        datetime.datetime(2001, 6, 8, 0, 0, 0, tzinfo=TZ_MINUS_0700),
                    ]),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'stokley-c/chris_stokley/sent/1.',
        'source_span': (1279893159, 1279893296),
        'sent_at': datetime.datetime(2001, 8, 1, 6, 20, 48, tzinfo=TZ_MINUS_0700),
        'text': 'Please have your plans of action/feedback/comments to me by Thursday morning, so I can make sure they get included in the report he sees.',
        'expected': [
                ('Thursday morning', (60, 76), datetime.datetime(2001, 8, 2, 6, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'mclaughlin-e/eol___tagg/131.',
        'source_span': (974491262, 974491341),
        'sent_at': datetime.datetime(2001, 7, 27, 8, 14, 20, tzinfo=TZ_MINUS_0700),
        'text': 'This is a reminder that the sign-off forms are due by COB, Wednesday, August 1.',
        'expected': [
                ('COB, Wednesday, August 1', (54, 78), datetime.datetime(2001, 8, 1, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'shankman-j/deleted_items/309.',
        'source_span': (1201536974, 1201537050),
        'sent_at': datetime.datetime(2001, 10, 22, 5, 50, 42, tzinfo=TZ_MINUS_0700),
        'text': 'please submit your BUSINESS HIGHLIGHT OR NEWS by noon Wednesday, October 24.',
        'expected': [
                ('noon Wednesday, October 24', (49, 75), datetime.datetime(2001, 10, 24, 12, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'skilling-j/_sent_mail/302.',
        'source_span': (1236283014, 1236283051),
        'sent_at': datetime.datetime(2001, 4, 26, 1, 13, 0, tzinfo=TZ_MINUS_0700),
        'text': 'RSVP:          By noon on May 4, 2001',
        'expected': [
                ('noon on May 4, 2001', (18, 37), datetime.datetime(2001, 5, 4, 12, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'skilling-j/discussion_threads/1144.',
        'source_span': (1240792297, 1240792340),
        'sent_at': datetime.datetime(2001, 5, 7, 7, 16, 0, tzinfo=TZ_MINUS_0700),
        'text': 'RSVP:          By 5:00 p.m. on May 18, 2001',
        'expected': [
                ('5:00 p.m. on May 18, 2001', (18, 43), datetime.datetime(2001, 5, 18, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'holst-k/deleted_items/97.',
        'source_span': (522005008, 522005096),
        'sent_at': datetime.datetime(2001, 10, 17, 15, 8, 36, tzinfo=TZ_MINUS_0700),
        'text': 'Starting next Wednesday you have EB30C2 for your Fundies Meeting from 3:00 PM to 4:30 PM',
        'expected': [
                ('Starting next Wednesday you have EB30C2 for your Fundies Meeting from 3:00 PM to 4:30 PM', (0, 88), (datetime.datetime(2001, 10, 24, 15, 0, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 10, 24, 16, 30, 0, tzinfo=TZ_MINUS_0700))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'shively-h/discussion_threads/110.',
        'source_span': (1234594150, 1234594200),
        'sent_at': datetime.datetime(2000, 10, 16, 10, 9, 0, tzinfo=TZ_MINUS_0700),
        'text': 'next Tuesday  October 17, 2000, \nfrom 3:00-5:00 pm',
        'expected': [
                ('next Tuesday  October 17, 2000, \nfrom 3:00-5:00 pm', (0, 50), (datetime.datetime(2000, 10, 17, 15, 0, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2000, 10, 17, 17, 0, 0, tzinfo=TZ_MINUS_0700))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'corman-s/sent_items/47.',
        'source_span': (141651990, 141652048),
        'sent_at': datetime.datetime(2001, 10, 24, 9, 35, 27, tzinfo=TZ_MINUS_0700),
        'text': '39C1 is available from 3:00 - 4:00 pm on Tuesday, Oct. 30.',
        'expected': [
                ('3:00 - 4:00 pm on Tuesday, Oct. 30', (23, 57), (datetime.datetime(2001, 10, 30, 15, 0, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 10, 30, 16, 0, 0, tzinfo=TZ_MINUS_0700))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'jones-t/all_documents/3791.',
        'source_span': (555101397, 555101439),
        'sent_at': datetime.datetime(2000, 9, 13, 2, 24, 0, tzinfo=TZ_MINUS_0700),
        'text': 'R.S.V.P. to Sylvia Hu x36775 by Noon, 9/26',
        'expected': [
                ('Noon, 9/26', (32, 42), datetime.datetime(2000, 9, 26, 12, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'shankman-j/deleted_items/322.',
        'source_span': (1201586284, 1201586332),
        'sent_at': datetime.datetime(2001, 10, 19, 14, 40, 56, tzinfo=TZ_MINUS_0700),
        'text': 'from 10:00 a.m. Saturday until 8:00 a.m. Sunday.',
        'expected': [
                ('10:00 a.m. Saturday until 8:00 a.m. Sunday', (5, 47), (datetime.datetime(2001, 10, 20, 10, 0, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 10, 21, 8, 0, 0, tzinfo=TZ_MINUS_0700))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'kitchen-l/_americas/culture/2.',
        'source_span': (774637885, 774637990),
        'sent_at': datetime.datetime(2001, 9, 10, 6, 46, 9, tzinfo=TZ_MINUS_0700),
        'text': 'We would like to share our recommendations with you tomorrow from 1:30 to 2:30 in Conference Room EB16C1.',
        'expected': [
                ('tomorrow from 1:30 to 2:30', (52, 78), (datetime.datetime(2001, 9, 11, 13, 30, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 9, 11, 14, 30, 0, tzinfo=TZ_MINUS_0700))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'corman-s/inbox/65.',
        'source_span': (138431704, 138431791),
        'sent_at': datetime.datetime(2002, 3, 25, 13, 1, 44, tzinfo=TZ_MINUS_0800),
        'text': "The time is blocked for Michelle Lokay and Paul Y'Barbo, tomorrow from 2:00 until 3:00.",
        'expected': [
                ('tomorrow from 2:00 until 3:00', (57, 86), (datetime.datetime(2002, 3, 26, 14, 0, 0, tzinfo=TZ_MINUS_0800), datetime.datetime(2002, 3, 26, 15, 0, 0, tzinfo=TZ_MINUS_0800))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'corman-s/inbox/archives/142.',
        'source_span': (138632752, 138632813),
        'sent_at': datetime.datetime(2002, 2, 13, 13, 52, 41, tzinfo=TZ_MINUS_0800),
        'text': 'Shelley will only be available tomorrow from 3:00 until 5:00.',
        'expected': [
                ('tomorrow from 3:00 until 5:00', (31, 60), (datetime.datetime(2002, 2, 14, 15, 0, 0, tzinfo=TZ_MINUS_0800), datetime.datetime(2002, 2, 14, 17, 0, 0, tzinfo=TZ_MINUS_0800))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'holst-k/deleted_items/71.',
        'source_span': (521893530, 521893627),
        'sent_at': datetime.datetime(2001, 10, 22, 8, 59, 58, tzinfo=TZ_MINUS_0700),
        'text': 'The meeting with IHS Energy representatives will take place tomorrow from 10:30 to 1:30 in EB3321',
        'expected': [
                ('tomorrow from 10:30 to 1:30', (60, 87), (datetime.datetime(2001, 10, 23, 10, 30, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 10, 23, 13, 30, 0, tzinfo=TZ_MINUS_0700))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'lay-k/discussion_threads/105.',
        'source_span': (812876104, 812876154),
        'sent_at': datetime.datetime(2000, 8, 22, 4, 34, 0, tzinfo=TZ_MINUS_0700),
        'text': 'to me via e-mail by 5:00 pm on Tuesday, August 22.',
        'expected': [
                ('5:00 pm on Tuesday, August 22', (20, 49), datetime.datetime(2000, 8, 22, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'shankman-j/deleted_items/14.',
        'source_span': (1201030927, 1201031003),
        'sent_at': datetime.datetime(2001, 10, 29, 6, 8, 7, tzinfo=TZ_MINUS_0800),
        'text': 'please submit your BUSINESS HIGHLIGHT OR NEWS by noon Wednesday, October 31.',
        'expected': [
                ('noon Wednesday, October 31', (49, 75), datetime.datetime(2001, 10, 31, 12, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'shively-h/inbox/34.',
        'source_span': (1235234344, 1235234372),
        'sent_at': datetime.datetime(2002, 1, 31, 8, 34, 11, tzinfo=TZ_MINUS_0800),
        'text': 'by noon this Friday  2/01/02',
        'expected': [
                ('noon this Friday  2/01/02', (3, 28), datetime.datetime(2002, 2, 1, 12, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'shively-h/deleted_items/609.',
        'source_span': (1233746316, 1233746338),
        'sent_at': datetime.datetime(2001, 5, 31, 11, 35, 40, tzinfo=TZ_MINUS_0700),
        'text': 'by 3:00 p.m. tomorrow.',
        'expected': [
                ('3:00 p.m. tomorrow', (3, 21), datetime.datetime(2001, 6, 1, 15, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'shively-h/inbox/57.',
        'source_span': (1235292060, 1235292077),
        'sent_at': datetime.datetime(2002, 1, 2, 11, 3, 45, tzinfo=TZ_MINUS_0800),
        'text': 'by 3:00 pm today.',
        'expected': [
                ('3:00 pm today', (3, 16), datetime.datetime(2002, 1, 2, 15, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'shively-h/deleted_items/699.',
        'source_span': (1234108469, 1234108494),
        'sent_at': datetime.datetime(2001, 11, 14, 10, 16, 13, tzinfo=TZ_MINUS_0800),
        'text': 'by 5:00 PM, Friday, 11/16',
        'expected': [
                ('5:00 PM, Friday, 11/16', (3, 25), datetime.datetime(2001, 11, 16, 17, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'shively-h/deleted_items/699.',
        'source_span': (1234108882, 1234108907),
        'sent_at': datetime.datetime(2001, 11, 14, 10, 16, 13, tzinfo=TZ_MINUS_0800),
        'text': 'Monday morning at 5:00 AM',
        'expected': [
                ('Monday morning at 5:00 AM', (0, 25), datetime.datetime(2001, 11, 19, 5, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'donohoe-t/inbox/234.',
        'source_span': (324772731, 324772814),
        'sent_at': datetime.datetime(2001, 10, 25, 13, 19, 47, tzinfo=TZ_MINUS_0700),
        'text': 'Bids are due by 11:00 am on Monday October 29.  Bids should be awarded by\n11:30 am.',
        'expected': [
                ('11:00 am on Monday October 29', (16, 45), datetime.datetime(2001, 10, 29, 11, 0, 0, tzinfo=TZ_MINUS_0700)),
                ('11:30 am', (74, 82), datetime.datetime(2001, 10, 29, 11, 30, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'zipper-a/inbox/81.',
        'source_span': (1427952983, 1427953007),
        'sent_at': datetime.datetime(2001, 6, 5, 15, 36, 6, tzinfo=TZ_MINUS_0700),
        'text': 'by 5:00PM on Monday 6/11',
        'expected': [
                ('5:00PM on Monday 6/11', (3, 24), datetime.datetime(2001, 6, 11, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'zipper-a/inbox/90.',
        'source_span': (1427978752, 1427978772),
        'sent_at': datetime.datetime(2001, 6, 6, 8, 14, 39, tzinfo=TZ_MINUS_0700),
        'text': 'by noon on Thursday.',
        'expected': [
                ('noon on Thursday', (3, 19), datetime.datetime(2001, 6, 7, 12, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'jones-t/all_documents/9583.',
        'source_span': (561745697, 561745747),
        'sent_at': datetime.datetime(2001, 2, 23, 9, 43, 0, tzinfo=TZ_MINUS_0800),
        'text': 'Please respond by 10 a.m. on Tuesday, February 27.',
        'expected': [
                ('10 a.m. on Tuesday, February 27', (18, 49), datetime.datetime(2001, 2, 27, 10, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'shankman-j/inbox/51.',
        'source_span': (1205378800, 1205378839),
        'sent_at': datetime.datetime(2001, 10, 22, 13, 20, 34, tzinfo=TZ_MINUS_0700),
        'text': 'by 5:00 p.m. Tuesday, October 30, 2001.',
        'expected': [
                ('5:00 p.m. Tuesday, October 30, 2001', (3, 38), datetime.datetime(2001, 10, 30, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'kitchen-l/_americas/sec/15.',
        'source_span': (785965693, 785965726),
        'sent_at': datetime.datetime(2001, 11, 16, 17, 45, 8, tzinfo=TZ_MINUS_0800),
        'text': 'by 2:00 pm Saturday, November 17.',
        'expected': [
                ('2:00 pm Saturday, November 17', (3, 32), datetime.datetime(2001, 11, 17, 14, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'kitchen-l/_americas/sec/27.',
        'source_span': (786107775, 786107786),
        'sent_at': datetime.datetime(2001, 11, 7, 17, 49, 36, tzinfo=TZ_MINUS_0800),
        'text': 'by 9:00 pm.',
        'expected': [
                ('9:00 pm', (3, 10), datetime.datetime(2001, 11, 7, 21, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'kitchen-l/_americas/east_power/164.',
        'source_span': (774887525, 774887546),
        'sent_at': datetime.datetime(2001, 6, 29, 19, 44, 0, tzinfo=TZ_MINUS_0700),
        'text': 'by 10:00 am on July 3',
        'expected': [
                ('10:00 am on July 3', (3, 21), datetime.datetime(2001, 7, 3, 10, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'kitchen-l/_americas/esvl/337.',
        'source_span': (776442395, 776442418),
        'sent_at': datetime.datetime(2001, 12, 6, 15, 41, 52, tzinfo=TZ_MINUS_0800),
        'text': 'by 9:00 a.m. on Friday.',
        'expected': [
                ('9:00 a.m. on Friday', (3, 22), datetime.datetime(2001, 12, 7, 9, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'stokley-c/chris_stokley/murray/31.',
        'source_span': (1279259821, 1279259848),
        'sent_at': datetime.datetime(2001, 8, 20, 5, 28, 13, tzinfo=TZ_MINUS_0700),
        'text': 'Monday and Tuesday, 8/20&21',
        'expected': [
                ('Monday and Tuesday, 8/20&21', (0, 27), [
                        datetime.datetime(2001, 8, 20, 0, 0, 0, tzinfo=TZ_MINUS_0700),
                        datetime.datetime(2001, 8, 21, 0, 0, 0, tzinfo=TZ_MINUS_0700),
                    ]),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'stokley-c/chris_stokley/murray/31.',
        'source_span': (1279259890, 1279259921),
        'sent_at': datetime.datetime(2001, 8, 20, 5, 28, 13, tzinfo=TZ_MINUS_0700),
        'text': 'Tuesday, 8/21, from 1:00 - 2:30',
        'expected': [
                ('Tuesday, 8/21, from 1:00 - 2:30', (0, 31), (datetime.datetime(2001, 8, 21, 13, 0, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 8, 21, 14, 30, 0, tzinfo=TZ_MINUS_0700))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'stokley-c/chris_stokley/murray/31.',
        'source_span': (1279260236, 1279260252),
        'sent_at': datetime.datetime(2001, 8, 20, 5, 28, 13, tzinfo=TZ_MINUS_0700),
        'text': 'by COB on Monday',
        'expected': [
                ('COB on Monday', (3, 16), datetime.datetime(2001, 8, 20, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'kitchen-l/_americas/turbines/22.',
        'source_span': (792126949, 792126982),
        'sent_at': datetime.datetime(2001, 9, 25, 10, 30, 30, tzinfo=TZ_MINUS_0700),
        'text': 'by the close of business tomorrow',
        'expected': [
                ('close of business tomorrow', (7, 33), datetime.datetime(2001, 9, 26, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'stokley-c/chris_stokley/sent/243.',
        'source_span': (1280191358, 1280191386),
        'sent_at': datetime.datetime(2001, 4, 11, 13, 43, 0, tzinfo=TZ_MINUS_0700),
        'text': 'by end of business tommowrow',
        'expected': [
                ('end of business tommowrow', (3, 28), datetime.datetime(2001, 4, 12, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'scholtes-d/ferc/43.',
        'source_span': (1123045722, 1123045758),
        'sent_at': datetime.datetime(2001, 6, 12, 16, 16, 44, tzinfo=TZ_MINUS_0700),
        'text': 'close of business on Friday, June 22',
        'expected': [
                ('close of business on Friday, June 22', (0, 36), datetime.datetime(2001, 6, 22, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'zipper-a/broker_client/3.',
        'source_span': (1425512764, 1425512791),
        'sent_at': datetime.datetime(2001, 6, 1, 8, 23, 45, tzinfo=TZ_MINUS_0700),
        'text': '$200 K if signed by COB 6/8',
        'expected': [
                ('COB 6/8', (20, 27), datetime.datetime(2001, 6, 8, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'zipper-a/broker_client/3.',
        'source_span': (1425512792, 1425512820),
        'sent_at': datetime.datetime(2001, 6, 1, 8, 23, 45, tzinfo=TZ_MINUS_0700),
        'text': '$225 K if signed by COB 6/15',
        'expected': [
                ('COB 6/15', (20, 28), datetime.datetime(2001, 6, 15, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'kitchen-l/_americas/esvl/443.',
        'source_span': (776719904, 776719948),
        'sent_at': datetime.datetime(2001, 11, 27, 10, 45, 33, tzinfo=TZ_MINUS_0800),
        'text': 'by close of business on Tuesday, November 27',
        'expected': [
                ('close of business on Tuesday, November 27', (3, 44), datetime.datetime(2001, 11, 27, 17, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'kitchen-l/_americas/esvl/264.',
        'source_span': (776281978, 776282015),
        'sent_at': datetime.datetime(2001, 12, 13, 14, 44, 2, tzinfo=TZ_MINUS_0800),
        'text': 'following the close of business today',
        'expected': [
                ('close of business today', (14, 37), datetime.datetime(2001, 12, 13, 17, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'corman-s/inbox/measurement/18.',
        'source_span': (140631002, 140631040),
        'sent_at': datetime.datetime(2002, 1, 28, 11, 31, 6, tzinfo=TZ_MINUS_0800),
        'text': 'by the close of business on February 5',
        'expected': [
                ('close of business on February 5', (7, 38), datetime.datetime(2002, 2, 5, 17, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'allen-p/_sent_mail/1001.',
        'source_span': (3485, 3501),
        'sent_at': datetime.datetime(2000, 8, 31, 5, 7, 0, tzinfo=TZ_MINUS_0700),
        'text': 'Tuesday at 11:45',
        'expected': [
                ('Tuesday at 11:45', (0, 16), datetime.datetime(2000, 9, 5, 11, 45, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'allen-p/_sent_mail/1002.',
        'source_span': (3997, 4021),
        'sent_at': datetime.datetime(2000, 8, 31, 4, 17, 0, tzinfo=TZ_MINUS_0700),
        'text': 'next Tuesday or Thursday',
        'expected': [
                ('next Tuesday or Thursday', (0, 24), [
                        datetime.datetime(2000, 9, 5, 0, 0, 0, tzinfo=TZ_MINUS_0700),
                        datetime.datetime(2000, 9, 7, 0, 0, 0, tzinfo=TZ_MINUS_0700),
                    ]),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'allen-p/_sent_mail/111.',
        'source_span': (28973, 29001),
        'sent_at': datetime.datetime(2000, 10, 3, 9, 15, 0, tzinfo=TZ_MINUS_0700),
        'text': 'Tuesday, Oct. 10th at 4:00pm',
        'expected': [
                ('Tuesday, Oct. 10th at 4:00pm', (0, 28), datetime.datetime(2000, 10, 10, 16, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'allen-p/_sent_mail/122.',
        'source_span': (63929, 63961),
        'sent_at': datetime.datetime(2000, 9, 26, 5, 7, 0, tzinfo=TZ_MINUS_0700),
        'text': 'Thursday, 9/28 from 3:00 - \n4:00',
        'expected': [
                ('Thursday, 9/28 from 3:00 - \n4:00', (0, 32), (datetime.datetime(2000, 9, 28, 15, 0, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2000, 9, 28, 16, 0, 0, tzinfo=TZ_MINUS_0700))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'pereira-s/all_documents/47.',
        'source_span': (1026290737, 1026290753),
        'sent_at': datetime.datetime(2001, 4, 2, 7, 5, 0, tzinfo=TZ_MINUS_0700),
        'text': 'Tomorrow at 1:45',
        'expected': [
                ('Tomorrow at 1:45', (0, 16), datetime.datetime(2001, 4, 3, 1, 45, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'beck-s/sap/27.',
        'source_span': (79882441, 79882456),
        'sent_at': datetime.datetime(2000, 5, 11, 5, 58, 0, tzinfo=TZ_MINUS_0700),
        'text': 'today at 4:00pm',
        'expected': [
                ('today at 4:00pm', (0, 15), datetime.datetime(2000, 5, 11, 16, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'kitchen-l/_americas/turbines/52.',
        'source_span': (792224374, 792224391),
        'sent_at': datetime.datetime(2001, 8, 5, 17, 38, 20, tzinfo=TZ_MINUS_0700),
        'text': 'Monday or Tuesday',
        'expected': [
                ('Monday or Tuesday', (0, 17), [
                        datetime.datetime(2001, 8, 6, 0, 0, 0, tzinfo=TZ_MINUS_0700),
                        datetime.datetime(2001, 8, 7, 0, 0, 0, tzinfo=TZ_MINUS_0700),
                    ]),
            ],
    },
    {
        'source_path': 'corman-s/deleted_items/171.',
        'source_span': (136570938, 136571074),
        'sent_at': datetime.datetime(2002, 1, 10, 8, 54, 13, tzinfo=TZ_MINUS_0800),
        'text': "starting on Tuesday, January 15th , in San Diego. Wednesday and Thursday's meetings will be in Houston, and Friday's meeting in Phoenix.",
        'expected': [
                ('Tuesday, January 15th', (12, 33), datetime.datetime(2002, 1, 15, 0, 0, 0, tzinfo=TZ_MINUS_0800)),
                ('Wednesday and Thursday', (50, 72), [
                        datetime.datetime(2002, 1, 16, 0, 0, 0, tzinfo=TZ_MINUS_0800),
                        datetime.datetime(2002, 1, 17, 0, 0, 0, tzinfo=TZ_MINUS_0800),
                    ]),
                ('Friday', (108, 114), datetime.datetime(2002, 1, 18, 0, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'mclaughlin-e/private_folders/corp_info_announcements/128.',
        'source_span': (976532967, 976532998),
        'sent_at': datetime.datetime(2001, 9, 13, 20, 8, 51, tzinfo=TZ_MINUS_0700),
        'text': 'tomorrow from 9:00 - 11:00 a.m.',
        'expected': [
                ('tomorrow from 9:00 - 11:00 a.m.', (0, 31), (datetime.datetime(2001, 9, 14, 9, 0, 0, tzinfo=TZ_MINUS_0700), datetime.datetime(2001, 9, 14, 11, 0, 0, tzinfo=TZ_MINUS_0700))),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'shankman-j/deleted_items/200.',
        'source_span': (1201225248, 1201225261),
        'sent_at': datetime.datetime(2001, 10, 24, 5, 22, 33, tzinfo=TZ_MINUS_0700),
        'text': 'by noon today',
        'expected': [
                ('noon today', (3, 13), datetime.datetime(2001, 10, 24, 12, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'skilling-j/_sent_mail/66.',
        'source_span': (1236578752, 1236578767),
        'sent_at': datetime.datetime(2000, 7, 12, 6, 28, 0, tzinfo=TZ_MINUS_0700),
        'text': 'by 5 p.m. today',
        'expected': [
                ('5 p.m. today', (3, 15), datetime.datetime(2000, 7, 12, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
    },
    {
        'source_path': 'shackleton-s/all_documents/4220.',
        'source_span': (1168208375, 1168208435),
        'sent_at': datetime.datetime(2000, 10, 19, 4, 27, 0, tzinfo=TZ_MINUS_0700),
        'text': 'Effective Date: Friday, October 20, 2000 (close of business)',
        'expected': [
                ('Friday, October 20, 2000 (close of business)', (16, 60), datetime.datetime(2000, 10, 20, 17, 0, 0, tzinfo=TZ_MINUS_0700)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'shackleton-s/all_documents/5161.',
        'source_span': (1170434353, 1170434417),
        'sent_at': datetime.datetime(2000, 12, 12, 7, 7, 0, tzinfo=TZ_MINUS_0800),
        'text': 'Effective Date: Wednesday, December 13, 2000 (close of business)',
        'expected': [
                ('Wednesday, December 13, 2000 (close of business)', (16, 64), datetime.datetime(2000, 12, 13, 17, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'shackleton-s/all_documents/8560.',
        'source_span': (1171330034, 1171330096),
        'sent_at': datetime.datetime(2000, 12, 19, 6, 20, 0, tzinfo=TZ_MINUS_0800),
        'text': 'Effective Date: Tuesday, December 19, 2000 (close of business)',
        'expected': [
                ('Tuesday, December 19, 2000 (close of business)', (16, 62), datetime.datetime(2000, 12, 19, 17, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
        'known_failure': 'Current parser output does not yet match this manually reviewed Enron golden.',
    },
    {
        'source_path': 'shively-h/deleted_items/1.',
        'source_span': (1232479237, 1232479253),
        'sent_at': datetime.datetime(2002, 2, 6, 15, 14, 2, tzinfo=TZ_MINUS_0800),
        'text': 'by 7 p.m. Monday',
        'expected': [
                ('7 p.m. Monday', (3, 16), datetime.datetime(2002, 2, 11, 19, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
    {
        'source_path': 'martin-t/inbox/462.',
        'source_span': (942803504, 942803532),
        'sent_at': datetime.datetime(2001, 11, 2, 10, 10, 27, tzinfo=TZ_MINUS_0800),
        'text': 'by 5:00 PM on Friday 11/9/01',
        'expected': [
                ('5:00 PM on Friday 11/9/01', (3, 28), datetime.datetime(2001, 11, 9, 17, 0, 0, tzinfo=TZ_MINUS_0800)),
            ],
    },
]

FORBIDDEN = []

DATA = {
    "id": "enron_emails",
    "source_hint": "CMU Enron Email Dataset (May 7, 2015)",
    "gold_status": "context_sample",
    "text": None,
    "expected": None,
    "context_expected": CONTEXT_MATCHED_TEXT_CASES,
    "forbidden": FORBIDDEN,
}
