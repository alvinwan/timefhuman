import datetime

from eval.corpus_data._shared import fixed_offset


TZ_MINUS_0800 = fixed_offset(-480)
TZ_MINUS_0700 = fixed_offset(-420)

# Evenly sampled RFC 822 Date headers across the flattened Enron corpus text.
MATCHED_TEXT = [
    ('Mon, 14 May 2001 16:39:00 -0700', (103, 134), datetime.datetime(2001, 5, 14, 16, 39, 0, tzinfo=TZ_MINUS_0700)),  # allen-p/_sent_mail/1.
    ('Mon, 29 Oct 2001 09:16:09 -0800', (3702067, 3702098), datetime.datetime(2001, 10, 29, 9, 16, 9, tzinfo=TZ_MINUS_0800)),  # allen-p/inbox/31.
    ('Sun, 5 Nov 2000 08:58:00 -0800', (6985104, 6985134), datetime.datetime(2000, 11, 5, 8, 58, 0, tzinfo=TZ_MINUS_0800)),  # arnold-j/all_documents/235.
    ('Wed, 6 Dec 2000 02:29:00 -0800', (13365972, 13366002), datetime.datetime(2000, 12, 6, 2, 29, 0, tzinfo=TZ_MINUS_0800)),  # arnold-j/etol/3.
    ('Thu, 27 Dec 2001 01:27:21 -0800', (18153395, 18153426), datetime.datetime(2001, 12, 27, 1, 27, 21, tzinfo=TZ_MINUS_0800)),  # arora-h/deleted_items/28.
    ('Thu, 8 Mar 2001 08:47:00 -0800', (24289308, 24289338), datetime.datetime(2001, 3, 8, 8, 47, 0, tzinfo=TZ_MINUS_0800)),  # bass-e/_sent_mail/1185.
    ('Mon, 26 Mar 2001 04:59:00 -0800', (27495339, 27495370), datetime.datetime(2001, 3, 26, 4, 59, 0, tzinfo=TZ_MINUS_0800)),  # bass-e/all_documents/1745.
    ('Wed, 24 Jan 2001 02:26:00 -0800', (35775124, 35775155), datetime.datetime(2001, 1, 24, 2, 26, 0, tzinfo=TZ_MINUS_0800)),  # bass-e/discussion_threads/1725.
    ('Thu, 2 Nov 2000 02:01:00 -0800', (43080874, 43080904), datetime.datetime(2000, 11, 2, 2, 1, 0, tzinfo=TZ_MINUS_0800)),  # bass-e/sent/108.
    ('Thu, 17 Jan 2002 12:29:20 -0800', (47259452, 47259483), datetime.datetime(2002, 1, 17, 12, 29, 20, tzinfo=TZ_MINUS_0800)),  # baughman-d/deleted_items/166.
    ('Wed, 25 Apr 2001 19:29:00 -0700', (54559167, 54559198), datetime.datetime(2001, 4, 25, 19, 29, 0, tzinfo=TZ_MINUS_0700)),  # baughman-d/power/legal_agreements/63.
    ('Fri, 18 Aug 2000 10:24:00 -0700', (59717700, 59717731), datetime.datetime(2000, 8, 18, 10, 24, 0, tzinfo=TZ_MINUS_0700)),  # beck-s/all_documents/1652.
    ('Thu, 29 Mar 2001 03:40:00 -0800', (64145229, 64145260), datetime.datetime(2001, 3, 29, 3, 40, 0, tzinfo=TZ_MINUS_0800)),  # beck-s/all_documents/536.
    ('Tue, 3 Oct 2000 09:59:00 -0700', (68870744, 68870774), datetime.datetime(2000, 10, 3, 9, 59, 0, tzinfo=TZ_MINUS_0700)),  # beck-s/discussion_threads/1777.
    ('Tue, 12 Sep 2000 03:13:00 -0700', (73465615, 73465646), datetime.datetime(2000, 9, 12, 3, 13, 0, tzinfo=TZ_MINUS_0700)),  # beck-s/eol/20.
    ('Fri, 19 Jan 2001 09:59:00 -0800', (79599155, 79599186), datetime.datetime(2001, 1, 19, 9, 59, 0, tzinfo=TZ_MINUS_0800)),  # beck-s/recruiting/32.
    ('Thu, 31 Jan 2002 15:14:09 -0800', (84253930, 84253961), datetime.datetime(2002, 1, 31, 15, 14, 9, tzinfo=TZ_MINUS_0800)),  # benson-r/deleted_items/11.
    ('Wed, 27 Jun 2001 16:02:00 -0700', (91102258, 91102289), datetime.datetime(2001, 6, 27, 16, 2, 0, tzinfo=TZ_MINUS_0700)),  # blair-l/meetings/170.
    ('Mon, 17 Sep 2001 07:56:52 -0700', (94466126, 94466157), datetime.datetime(2001, 9, 17, 7, 56, 52, tzinfo=TZ_MINUS_0700)),  # blair-l/vacations_2001/1.
    ('Fri, 25 Jan 2002 13:15:07 -0800', (99294876, 99294907), datetime.datetime(2002, 1, 25, 13, 15, 7, tzinfo=TZ_MINUS_0800)),  # buy-r/inbox/20.
    ('Fri, 20 Apr 2001 10:02:00 -0700', (104303522, 104303553), datetime.datetime(2001, 4, 20, 10, 2, 0, tzinfo=TZ_MINUS_0700)),  # campbell-l/all_documents/1466.
    ('Wed, 23 May 2001 08:31:00 -0700', (109811786, 109811817), datetime.datetime(2001, 5, 23, 8, 31, 0, tzinfo=TZ_MINUS_0700)),  # campbell-l/discussion_threads/1695.
    ('Fri, 27 Jul 2001 04:49:21 -0700', (115720659, 115720690), datetime.datetime(2001, 7, 27, 4, 49, 21, tzinfo=TZ_MINUS_0700)),  # campbell-l/inbox/750.
    ('Fri, 1 Sep 2000 03:07:00 -0700', (120800336, 120800366), datetime.datetime(2000, 9, 1, 3, 7, 0, tzinfo=TZ_MINUS_0700)),  # carson-m/all_documents/112.
    ('Fri, 26 Oct 2001 06:24:31 -0700', (126880364, 126880395), datetime.datetime(2001, 10, 26, 6, 24, 31, tzinfo=TZ_MINUS_0700)),  # cash-m/deleted_items/163.
    ('Tue, 13 Nov 2001 13:33:41 -0800', (133267254, 133267285), datetime.datetime(2001, 11, 13, 13, 33, 41, tzinfo=TZ_MINUS_0800)),  # cash-m/sent_items/488.
    ('Mon, 25 Feb 2002 23:01:50 -0800', (139447467, 139447498), datetime.datetime(2002, 2, 25, 23, 1, 50, tzinfo=TZ_MINUS_0800)),  # corman-s/inbox/archives/366.
    ('Sun, 18 Nov 2001 09:08:54 -0800', (146085992, 146086023), datetime.datetime(2001, 11, 18, 9, 8, 54, tzinfo=TZ_MINUS_0800)),  # cuilla-m/deleted_items/361.
    ('Thu, 19 Apr 2001 06:20:00 -0700', (155112257, 155112288), datetime.datetime(2001, 4, 19, 6, 20, 0, tzinfo=TZ_MINUS_0700)),  # dasovich-j/all_documents/11298.
    ('Tue, 29 May 2001 08:45:00 -0700', (167935958, 167935989), datetime.datetime(2001, 5, 29, 8, 45, 0, tzinfo=TZ_MINUS_0700)),  # dasovich-j/all_documents/13162.
    ('Wed, 13 Jun 2001 05:51:00 -0700', (178483171, 178483202), datetime.datetime(2001, 6, 13, 5, 51, 0, tzinfo=TZ_MINUS_0700)),  # dasovich-j/all_documents/27803.
    ('Thu, 9 Nov 2000 03:37:00 -0800', (190958851, 190958881), datetime.datetime(2000, 11, 9, 3, 37, 0, tzinfo=TZ_MINUS_0800)),  # dasovich-j/all_documents/3265.
    ('Mon, 18 Dec 2000 07:27:00 -0800', (198580733, 198580764), datetime.datetime(2000, 12, 18, 7, 27, 0, tzinfo=TZ_MINUS_0800)),  # dasovich-j/all_documents/7826.
    ('Tue, 6 Mar 2001 03:04:00 -0800', (207729166, 207729196), datetime.datetime(2001, 3, 6, 3, 4, 0, tzinfo=TZ_MINUS_0800)),  # dasovich-j/all_documents/9689.
    ('Wed, 26 Apr 2000 07:48:00 -0700', (219121980, 219122011), datetime.datetime(2000, 4, 26, 7, 48, 0, tzinfo=TZ_MINUS_0700)),  # dasovich-j/distributed_generation/12.
    ('Sat, 21 Oct 2000 09:10:00 -0700', (230177889, 230177920), datetime.datetime(2000, 10, 21, 9, 10, 0, tzinfo=TZ_MINUS_0700)),  # dasovich-j/notes_inbox/1087.
    ('Wed, 22 Nov 2000 08:03:00 -0800', (244345250, 244345281), datetime.datetime(2000, 11, 22, 8, 3, 0, tzinfo=TZ_MINUS_0800)),  # dasovich-j/notes_inbox/1927.
    ('Mon, 11 Sep 2000 10:35:00 -0700', (260129646, 260129677), datetime.datetime(2000, 9, 11, 10, 35, 0, tzinfo=TZ_MINUS_0700)),  # dasovich-j/notes_inbox/377.
    ('Fri, 26 Jan 2001 06:32:00 -0800', (272285124, 272285155), datetime.datetime(2001, 1, 26, 6, 32, 0, tzinfo=TZ_MINUS_0800)),  # dasovich-j/notes_inbox/5601.
    ('Tue, 5 Sep 2000 11:04:00 -0700', (280258500, 280258530), datetime.datetime(2000, 9, 5, 11, 4, 0, tzinfo=TZ_MINUS_0700)),  # dasovich-j/sent/150.
    ('Tue, 1 May 2001 12:57:00 -0700', (286388613, 286388643), datetime.datetime(2001, 5, 1, 12, 57, 0, tzinfo=TZ_MINUS_0700)),  # dasovich-j/sent/4427.
    ('Mon, 15 Oct 2001 15:58:49 -0700', (291030218, 291030249), datetime.datetime(2001, 10, 15, 15, 58, 49, tzinfo=TZ_MINUS_0700)),  # dasovich-j/sent_items/609.
    ('Tue, 27 Nov 2001 09:35:50 -0800', (295768720, 295768751), datetime.datetime(2001, 11, 27, 9, 35, 50, tzinfo=TZ_MINUS_0800)),  # davis-d/inbox/109.
    ('Thu, 25 Oct 2001 06:38:07 -0700', (302716599, 302716630), datetime.datetime(2001, 10, 25, 6, 38, 7, tzinfo=TZ_MINUS_0700)),  # dean-c/inbox/463.
    ('Wed, 13 Dec 2000 10:20:00 -0800', (309186254, 309186285), datetime.datetime(2000, 12, 13, 10, 20, 0, tzinfo=TZ_MINUS_0800)),  # delainey-d/all_documents/2.
    ('Thu, 20 Jul 2000 05:19:00 -0700', (313901950, 313901981), datetime.datetime(2000, 7, 20, 5, 19, 0, tzinfo=TZ_MINUS_0700)),  # delainey-d/sent/450.
    ('Fri, 5 Oct 2001 16:52:38 -0700', (319332508, 319332538), datetime.datetime(2001, 10, 5, 16, 52, 38, tzinfo=TZ_MINUS_0700)),  # derrick-j/sent_items/381.
    ('Tue, 31 Oct 2000 10:49:00 -0800', (323926673, 323926704), datetime.datetime(2000, 10, 31, 10, 49, 0, tzinfo=TZ_MINUS_0800)),  # donohoe-t/discussion_threads/186.
    ('Sun, 19 Nov 2000 02:13:00 -0800', (330704498, 330704529), datetime.datetime(2000, 11, 19, 2, 13, 0, tzinfo=TZ_MINUS_0800)),  # dorland-c/sent/3.
    ('Mon, 12 Mar 2001 14:02:00 -0800', (338157890, 338157921), datetime.datetime(2001, 3, 12, 14, 2, 0, tzinfo=TZ_MINUS_0800)),  # farmer-d/_sent_mail/1.
    ('Wed, 22 Mar 2000 03:34:00 -0800', (341818628, 341818659), datetime.datetime(2000, 3, 22, 3, 34, 0, tzinfo=TZ_MINUS_0800)),  # farmer-d/all_documents/2262.
    ('Thu, 28 Sep 2000 02:39:00 -0700', (345292631, 345292662), datetime.datetime(2000, 9, 28, 2, 39, 0, tzinfo=TZ_MINUS_0700)),  # farmer-d/all_documents/657.
    ('Fri, 28 Jul 2000 03:56:00 -0700', (349676859, 349676890), datetime.datetime(2000, 7, 28, 3, 56, 0, tzinfo=TZ_MINUS_0700)),  # farmer-d/discussion_threads/1779.
    ('Fri, 30 Mar 2001 02:17:00 -0800', (353135988, 353136019), datetime.datetime(2001, 3, 30, 2, 17, 0, tzinfo=TZ_MINUS_0800)),  # farmer-d/discussion_threads/4948.
    ('Tue, 4 Jan 2000 04:47:00 -0800', (357242856, 357242886), datetime.datetime(2000, 1, 4, 4, 47, 0, tzinfo=TZ_MINUS_0800)),  # farmer-d/logistics/646.
    ('Tue, 10 Apr 2001 09:11:54 -0700', (360943639, 360943670), datetime.datetime(2001, 4, 10, 9, 11, 54, tzinfo=TZ_MINUS_0700)),  # farmer-d/tufco/42.
    ('Thu, 18 Apr 2002 00:50:00 -0700', (364492803, 364492834), datetime.datetime(2002, 4, 18, 0, 50, 0, tzinfo=TZ_MINUS_0700)),  # fischer-m/notes_inbox/270.
    ('Thu, 1 Feb 2001 09:38:00 -0800', (370708839, 370708869), datetime.datetime(2001, 2, 1, 9, 38, 0, tzinfo=TZ_MINUS_0800)),  # fossum-d/_sent_mail/843.
    ('Wed, 1 Nov 2000 06:06:00 -0800', (376077515, 376077545), datetime.datetime(2000, 11, 1, 6, 6, 0, tzinfo=TZ_MINUS_0800)),  # fossum-d/discussion_threads/408.
    ('Thu, 18 Apr 2002 04:59:28 -0700', (381513452, 381513483), datetime.datetime(2002, 4, 18, 4, 59, 28, tzinfo=TZ_MINUS_0700)),  # gang-l/deleted_items/376.
    ('Tue, 23 Oct 2001 11:51:07 -0700', (385580236, 385580267), datetime.datetime(2001, 10, 23, 11, 51, 7, tzinfo=TZ_MINUS_0700)),  # geaccone-t/deleted_items/143.
    ('Tue, 25 Jan 2000 05:36:00 -0800', (389642596, 389642627), datetime.datetime(2000, 1, 25, 5, 36, 0, tzinfo=TZ_MINUS_0800)),  # germany-c/_sent_mail/1682.
    ('Fri, 3 Mar 2000 10:03:00 -0800', (393033525, 393033555), datetime.datetime(2000, 3, 3, 10, 3, 0, tzinfo=TZ_MINUS_0800)),  # germany-c/all_documents/2047.
    ('Fri, 24 Mar 2000 02:55:00 -0800', (396129354, 396129385), datetime.datetime(2000, 3, 24, 2, 55, 0, tzinfo=TZ_MINUS_0800)),  # germany-c/appala/67.
    ('Tue, 5 Sep 2000 06:28:00 -0700', (401504240, 401504270), datetime.datetime(2000, 9, 5, 6, 28, 0, tzinfo=TZ_MINUS_0700)),  # germany-c/discussion_threads/1644.
    ('Wed, 29 Mar 2000 08:09:00 -0800', (405296035, 405296066), datetime.datetime(2000, 3, 29, 8, 9, 0, tzinfo=TZ_MINUS_0800)),  # germany-c/sent/1078.
    ('Fri, 7 Jun 2002 11:39:53 -0700', (408223927, 408223957), datetime.datetime(2002, 6, 7, 11, 39, 53, tzinfo=TZ_MINUS_0700)),  # germany-c/sent_items/1.
    ('Tue, 20 Nov 2001 13:23:53 -0800', (412411653, 412411684), datetime.datetime(2001, 11, 20, 13, 23, 53, tzinfo=TZ_MINUS_0800)),  # gilbertsmith-d/inbox/142.
    ('Wed, 24 Oct 2001 10:19:53 -0700', (416531345, 416531376), datetime.datetime(2001, 10, 24, 10, 19, 53, tzinfo=TZ_MINUS_0700)),  # giron-d/deleted_items/310.
    ('Tue, 3 Apr 2001 04:08:00 -0700', (421090499, 421090529), datetime.datetime(2001, 4, 3, 4, 8, 0, tzinfo=TZ_MINUS_0700)),  # giron-d/sent/99.
    ('Mon, 27 Nov 2000 04:33:00 -0800', (426006933, 426006964), datetime.datetime(2000, 11, 27, 4, 33, 0, tzinfo=TZ_MINUS_0800)),  # griffith-j/discussion_threads/2.
    ('Thu, 18 Oct 2001 14:03:49 -0700', (429872189, 429872220), datetime.datetime(2001, 10, 18, 14, 3, 49, tzinfo=TZ_MINUS_0700)),  # grigsby-m/deleted_items/140.
    ('Tue, 6 Feb 2001 01:24:00 -0800', (436088236, 436088266), datetime.datetime(2001, 2, 6, 1, 24, 0, tzinfo=TZ_MINUS_0800)),  # guzman-m/all_documents/1196.
    ('Mon, 12 Mar 2001 05:35:00 -0800', (443888737, 443888768), datetime.datetime(2001, 3, 12, 5, 35, 0, tzinfo=TZ_MINUS_0800)),  # guzman-m/discussion_threads/1161.
    ('Wed, 10 Jan 2001 01:52:00 -0800', (448502355, 448502386), datetime.datetime(2001, 1, 10, 1, 52, 0, tzinfo=TZ_MINUS_0800)),  # guzman-m/notes_inbox/1255.
    ('Fri, 10 Nov 2000 05:53:00 -0800', (455816649, 455816680), datetime.datetime(2000, 11, 10, 5, 53, 0, tzinfo=TZ_MINUS_0800)),  # haedicke-m/all_documents/2200.
    ('Tue, 30 Oct 2001 03:00:48 -0800', (463101516, 463101547), datetime.datetime(2001, 10, 30, 3, 0, 48, tzinfo=TZ_MINUS_0800)),  # haedicke-m/inbox/2.
    ('Fri, 28 May 1999 09:16:00 -0700', (471306039, 471306070), datetime.datetime(1999, 5, 28, 9, 16, 0, tzinfo=TZ_MINUS_0700)),  # haedicke-m/sent/6.
    ('Mon, 19 Mar 2001 02:17:00 -0800', (479607180, 479607211), datetime.datetime(2001, 3, 19, 2, 17, 0, tzinfo=TZ_MINUS_0800)),  # hain-m/all_documents/762.
    ('Tue, 20 Mar 2001 08:23:00 -0800', (489982872, 489982903), datetime.datetime(2001, 3, 20, 8, 23, 0, tzinfo=TZ_MINUS_0800)),  # hain-m/notes_inbox/582.
    ('Fri, 19 May 2000 03:33:00 -0700', (494837964, 494837995), datetime.datetime(2000, 5, 19, 3, 33, 0, tzinfo=TZ_MINUS_0700)),  # hayslett-r/discussion_threads/84.
    ('Wed, 31 Oct 2001 15:32:03 -0800', (499479494, 499479525), datetime.datetime(2001, 10, 31, 15, 32, 3, tzinfo=TZ_MINUS_0800)),  # heard-m/inbox/master_netting/116.
    ('Fri, 13 Oct 2000 05:49:00 -0700', (504493992, 504494023), datetime.datetime(2000, 10, 13, 5, 49, 0, tzinfo=TZ_MINUS_0700)),  # hernandez-j/_sent_mail/48.
    ('Mon, 6 Aug 2001 17:20:39 -0700', (511863259, 511863289), datetime.datetime(2001, 8, 6, 17, 20, 39, tzinfo=TZ_MINUS_0700)),  # hernandez-j/inbox/310.
    ('Tue, 25 Sep 2001 15:04:00 -0700', (518550855, 518550886), datetime.datetime(2001, 9, 25, 15, 4, 0, tzinfo=TZ_MINUS_0700)),  # hodge-j/inbox/355.
    ('Wed, 23 Feb 2000 07:04:00 -0800', (525976143, 525976174), datetime.datetime(2000, 2, 23, 7, 4, 0, tzinfo=TZ_MINUS_0800)),  # horton-s/all_documents/92.
    ('Tue, 27 Nov 2001 07:05:15 -0800', (533030437, 533030468), datetime.datetime(2001, 11, 27, 7, 5, 15, tzinfo=TZ_MINUS_0800)),  # hyatt-k/deleted_items/572.
    ('Wed, 13 Jun 2001 02:47:00 -0700', (538632753, 538632784), datetime.datetime(2001, 6, 13, 2, 47, 0, tzinfo=TZ_MINUS_0700)),  # hyvl-d/all_documents/2544.
    ('Fri, 23 Feb 2001 06:55:00 -0800', (542701905, 542701936), datetime.datetime(2001, 2, 23, 6, 55, 0, tzinfo=TZ_MINUS_0800)),  # hyvl-d/sent/288.
    ('Tue, 4 Apr 2000 08:56:00 -0700', (547451515, 547451545), datetime.datetime(2000, 4, 4, 8, 56, 0, tzinfo=TZ_MINUS_0700)),  # jones-t/all_documents/1154.
    ('Mon, 19 Jun 2000 09:52:00 -0700', (551745930, 551745961), datetime.datetime(2000, 6, 19, 9, 52, 0, tzinfo=TZ_MINUS_0700)),  # jones-t/all_documents/2184.
    ('Fri, 22 Sep 2000 08:40:00 -0700', (555599654, 555599685), datetime.datetime(2000, 9, 22, 8, 40, 0, tzinfo=TZ_MINUS_0700)),  # jones-t/all_documents/4029.
    ('Thu, 16 Dec 1999 01:28:00 -0800', (559763607, 559763638), datetime.datetime(1999, 12, 16, 1, 28, 0, tzinfo=TZ_MINUS_0800)),  # jones-t/all_documents/588.
    ('Thu, 11 Oct 2001 11:52:12 -0700', (564100610, 564100641), datetime.datetime(2001, 10, 11, 11, 52, 12, tzinfo=TZ_MINUS_0700)),  # jones-t/inbox/379.
    ('Fri, 28 Apr 2000 02:46:00 -0700', (569328554, 569328585), datetime.datetime(2000, 4, 28, 2, 46, 0, tzinfo=TZ_MINUS_0700)),  # jones-t/notes_inbox/231.
    ('Thu, 19 Apr 2001 07:33:00 -0700', (574526230, 574526261), datetime.datetime(2001, 4, 19, 7, 33, 0, tzinfo=TZ_MINUS_0700)),  # jones-t/notes_inbox/4180.
    ('Wed, 26 Apr 2000 09:52:00 -0700', (579019296, 579019327), datetime.datetime(2000, 4, 26, 9, 52, 0, tzinfo=TZ_MINUS_0700)),  # jones-t/sent/1029.
    ('Fri, 19 Nov 1999 06:14:00 -0800', (582109317, 582109348), datetime.datetime(1999, 11, 19, 6, 14, 0, tzinfo=TZ_MINUS_0800)),  # jones-t/sent/487.
    ('Tue, 25 Sep 2001 07:41:46 -0700', (585753974, 585754005), datetime.datetime(2001, 9, 25, 7, 41, 46, tzinfo=TZ_MINUS_0700)),  # jones-t/sent_items/71.
    ('Tue, 16 May 2000 05:36:00 -0700', (590000485, 590000516), datetime.datetime(2000, 5, 16, 5, 36, 0, tzinfo=TZ_MINUS_0700)),  # kaminski-v/_sent_mail/3990.
    ('Tue, 8 Feb 2000 03:59:00 -0800', (594714139, 594714169), datetime.datetime(2000, 2, 8, 3, 59, 0, tzinfo=TZ_MINUS_0800)),  # kaminski-v/all_documents/10549.
    ('Thu, 21 Dec 2000 01:06:00 -0800', (598948691, 598948722), datetime.datetime(2000, 12, 21, 1, 6, 0, tzinfo=TZ_MINUS_0800)),  # kaminski-v/all_documents/2520.
    ('Mon, 21 Aug 2000 06:25:00 -0700', (603449660, 603449691), datetime.datetime(2000, 8, 21, 6, 25, 0, tzinfo=TZ_MINUS_0700)),  # kaminski-v/all_documents/4621.
    ('Fri, 23 Mar 2001 10:18:00 -0800', (608093885, 608093916), datetime.datetime(2001, 3, 23, 10, 18, 0, tzinfo=TZ_MINUS_0800)),  # kaminski-v/all_documents/943.
    ('Thu, 30 Mar 2000 06:33:00 -0800', (612547452, 612547483), datetime.datetime(2000, 3, 30, 6, 33, 0, tzinfo=TZ_MINUS_0800)),  # kaminski-v/c/technote/mail/projects/482.
    ('Tue, 15 Jan 2002 09:23:50 -0800', (618940784, 618940815), datetime.datetime(2002, 1, 15, 9, 23, 50, tzinfo=TZ_MINUS_0800)),  # kaminski-v/deleted_items/478.
    ('Mon, 8 Jan 2001 08:39:00 -0800', (623958367, 623958397), datetime.datetime(2001, 1, 8, 8, 39, 0, tzinfo=TZ_MINUS_0800)),  # kaminski-v/discussion_threads/2525.
    ('Tue, 11 Jan 2000 01:29:00 -0800', (628524096, 628524127), datetime.datetime(2000, 1, 11, 1, 29, 0, tzinfo=TZ_MINUS_0800)),  # kaminski-v/discussion_threads/4472.
    ('Thu, 29 Jun 2000 21:53:00 -0700', (633480001, 633480032), datetime.datetime(2000, 6, 29, 21, 53, 0, tzinfo=TZ_MINUS_0700)),  # kaminski-v/eci/eci/28.
    ('Mon, 8 May 2000 02:51:00 -0700', (638722192, 638722222), datetime.datetime(2000, 5, 8, 2, 51, 0, tzinfo=TZ_MINUS_0700)),  # kaminski-v/resumes/701.
    ('Mon, 19 Jun 2000 01:22:00 -0700', (642861911, 642861942), datetime.datetime(2000, 6, 19, 1, 22, 0, tzinfo=TZ_MINUS_0700)),  # kaminski-v/sent/2533.
    ('Thu, 10 Jan 2002 12:14:38 -0800', (647387120, 647387151), datetime.datetime(2002, 1, 10, 12, 14, 38, tzinfo=TZ_MINUS_0800)),  # kaminski-v/sent_items/144.
    ('Mon, 5 Jun 2000 06:26:00 -0700', (652281001, 652281031), datetime.datetime(2000, 6, 5, 6, 26, 0, tzinfo=TZ_MINUS_0700)),  # kaminski-v/var/118.
    ('Thu, 24 May 2001 07:00:00 -0700', (660059730, 660059761), datetime.datetime(2001, 5, 24, 7, 0, 0, tzinfo=TZ_MINUS_0700)),  # kean-s/all_documents/4761.
    ('Mon, 17 Jul 2000 03:19:00 -0700', (669861952, 669861983), datetime.datetime(2000, 7, 17, 3, 19, 0, tzinfo=TZ_MINUS_0700)),  # kean-s/all_documents/724.
    ('Fri, 8 Aug 1997 01:00:00 -0700', (676387997, 676388027), datetime.datetime(1997, 8, 8, 1, 0, 0, tzinfo=TZ_MINUS_0700)),  # kean-s/archiving/untitled/2255.
    ('Sun, 21 Jan 2001 09:12:00 -0800', (687118560, 687118591), datetime.datetime(2001, 1, 21, 9, 12, 0, tzinfo=TZ_MINUS_0800)),  # kean-s/archiving/untitled/6209.
    ('Thu, 16 Dec 1999 11:22:00 -0800', (693386705, 693386736), datetime.datetime(1999, 12, 16, 11, 22, 0, tzinfo=TZ_MINUS_0800)),  # kean-s/attachments/1896.
    ('Wed, 6 Oct 1999 08:00:00 -0700', (700162210, 700162240), datetime.datetime(1999, 10, 6, 8, 0, 0, tzinfo=TZ_MINUS_0700)),  # kean-s/calendar/untitled/154.
    ('Fri, 9 Feb 2001 08:56:00 -0800', (707282206, 707282236), datetime.datetime(2001, 2, 9, 8, 56, 0, tzinfo=TZ_MINUS_0800)),  # kean-s/calendar/untitled/7429.
    ('Thu, 1 Feb 2001 10:39:00 -0800', (720468336, 720468366), datetime.datetime(2001, 2, 1, 10, 39, 0, tzinfo=TZ_MINUS_0800)),  # kean-s/california/482.
    ('Thu, 28 Dec 2000 08:48:00 -0800', (731213743, 731213774), datetime.datetime(2000, 12, 28, 8, 48, 0, tzinfo=TZ_MINUS_0800)),  # kean-s/discussion_threads/1923.
    ('Wed, 28 Feb 2001 10:43:00 -0800', (741953984, 741954015), datetime.datetime(2001, 2, 28, 10, 43, 0, tzinfo=TZ_MINUS_0800)),  # kean-s/discussion_threads/6119.
    ('Mon, 18 Jun 2001 08:30:00 -0700', (751008494, 751008525), datetime.datetime(2001, 6, 18, 8, 30, 0, tzinfo=TZ_MINUS_0700)),  # kean-s/market_structure/41.
    ('Thu, 31 Aug 2000 10:42:00 -0700', (757652263, 757652294), datetime.datetime(2000, 8, 31, 10, 42, 0, tzinfo=TZ_MINUS_0700)),  # kean-s/sent/261.
    ('Wed, 6 Dec 2000 23:44:00 -0800', (764394992, 764395022), datetime.datetime(2000, 12, 6, 23, 44, 0, tzinfo=TZ_MINUS_0800)),  # keavey-p/discussion_threads/167.
    ('Tue, 22 Jan 2002 05:38:23 -0800', (771196040, 771196071), datetime.datetime(2002, 1, 22, 5, 38, 23, tzinfo=TZ_MINUS_0800)),  # keiser-k/sent_items/144.
    ('Mon, 12 Nov 2001 14:04:30 -0800', (777017568, 777017599), datetime.datetime(2001, 11, 12, 14, 4, 30, tzinfo=TZ_MINUS_0800)),  # kitchen-l/_americas/esvl/567.
    ('Fri, 23 Feb 2001 18:39:00 -0800', (783682372, 783682403), datetime.datetime(2001, 2, 23, 18, 39, 0, tzinfo=TZ_MINUS_0800)),  # kitchen-l/_americas/portland/203.
    ('Tue, 16 Oct 2001 07:48:57 -0700', (795146727, 795146758), datetime.datetime(2001, 10, 16, 7, 48, 57, tzinfo=TZ_MINUS_0700)),  # kitchen-l/sent_items/754.
    ('Thu, 1 Jun 2000 00:37:00 -0700', (799402457, 799402487), datetime.datetime(2000, 6, 1, 0, 37, 0, tzinfo=TZ_MINUS_0700)),  # lavorato-j/all_documents/170.
    ('Sun, 10 Dec 2000 03:02:00 -0800', (803799457, 803799488), datetime.datetime(2000, 12, 10, 3, 2, 0, tzinfo=TZ_MINUS_0800)),  # lavorato-j/discussion_threads/401.
    ('Wed, 23 Aug 2000 02:16:00 -0700', (806971409, 806971440), datetime.datetime(2000, 8, 23, 2, 16, 0, tzinfo=TZ_MINUS_0700)),  # lay-k/_sent/115.
    ('Wed, 30 Jan 2002 09:45:11 -0800', (811977968, 811977999), datetime.datetime(2002, 1, 30, 9, 45, 11, tzinfo=TZ_MINUS_0800)),  # lay-k/deleted_items/560.
    ('Wed, 24 Oct 2001 11:48:36 -0700', (817169290, 817169321), datetime.datetime(2001, 10, 24, 11, 48, 36, tzinfo=TZ_MINUS_0700)),  # lay-k/inbox/284.
    ('Tue, 27 Jun 2000 03:08:00 -0700', (822728812, 822728843), datetime.datetime(2000, 6, 27, 3, 8, 0, tzinfo=TZ_MINUS_0700)),  # lenhart-m/all_documents/1151.
    ('Thu, 25 Oct 2001 12:44:37 -0700', (825340408, 825340439), datetime.datetime(2001, 10, 25, 12, 44, 37, tzinfo=TZ_MINUS_0700)),  # lenhart-m/deleted_items/231.
    ('Tue, 14 Nov 2000 03:59:00 -0800', (829358855, 829358886), datetime.datetime(2000, 11, 14, 3, 59, 0, tzinfo=TZ_MINUS_0800)),  # lenhart-m/sent/1970.
    ('Tue, 23 Oct 2001 17:31:04 -0700', (835797185, 835797216), datetime.datetime(2001, 10, 23, 17, 31, 4, tzinfo=TZ_MINUS_0700)),  # lewis-a/deleted_items/1082.
    ('Fri, 6 Apr 2001 21:58:00 -0700', (847603806, 847603836), datetime.datetime(2001, 4, 6, 21, 58, 0, tzinfo=TZ_MINUS_0700)),  # linder-e/all_documents/249.
    ('Mon, 16 Apr 2001 21:43:00 -0700', (852446244, 852446275), datetime.datetime(2001, 4, 16, 21, 43, 0, tzinfo=TZ_MINUS_0700)),  # linder-e/notes_inbox/399.
    ('Tue, 20 Jun 2000 06:38:00 -0700', (858274730, 858274761), datetime.datetime(2000, 6, 20, 6, 38, 0, tzinfo=TZ_MINUS_0700)),  # lokay-m/articles/133.
    ('Thu, 19 Apr 2001 11:12:36 -0700', (864486834, 864486865), datetime.datetime(2001, 4, 19, 11, 12, 36, tzinfo=TZ_MINUS_0700)),  # lokay-m/enron_t_s/202.
    ('Wed, 19 Sep 2001 16:39:26 -0700', (869070700, 869070731), datetime.datetime(2001, 9, 19, 16, 39, 26, tzinfo=TZ_MINUS_0700)),  # lokay-m/tw_commercial_group/922.
    ('Mon, 29 Jan 2001 07:50:00 -0800', (873515534, 873515565), datetime.datetime(2001, 1, 29, 7, 50, 0, tzinfo=TZ_MINUS_0800)),  # love-p/_sent_mail/823.
    ('Fri, 2 Feb 2001 01:57:00 -0800', (877015019, 877015049), datetime.datetime(2001, 2, 2, 1, 57, 0, tzinfo=TZ_MINUS_0800)),  # love-p/discussion_threads/355.
    ('Tue, 30 Oct 2001 07:47:32 -0800', (880751098, 880751129), datetime.datetime(2001, 10, 30, 7, 47, 32, tzinfo=TZ_MINUS_0800)),  # love-p/sent_items/696.
    ('Thu, 24 Jan 2002 06:50:15 -0800', (886891798, 886891829), datetime.datetime(2002, 1, 24, 6, 50, 15, tzinfo=TZ_MINUS_0800)),  # maggi-m/deleted_items/237.
    ('Tue, 30 Jan 2001 07:52:00 -0800', (890771293, 890771324), datetime.datetime(2001, 1, 30, 7, 52, 0, tzinfo=TZ_MINUS_0800)),  # mann-k/_sent_mail/1825.
    ('Tue, 29 Aug 2000 11:06:00 -0700', (894283958, 894283989), datetime.datetime(2000, 8, 29, 11, 6, 0, tzinfo=TZ_MINUS_0700)),  # mann-k/_sent_mail/3659.
    ('Mon, 30 Oct 2000 08:28:00 -0800', (898042459, 898042490), datetime.datetime(2000, 10, 30, 8, 28, 0, tzinfo=TZ_MINUS_0800)),  # mann-k/all_documents/1677.
    ('Tue, 6 Feb 2001 10:12:00 -0800', (901849442, 901849472), datetime.datetime(2001, 2, 6, 10, 12, 0, tzinfo=TZ_MINUS_0800)),  # mann-k/all_documents/3507.
    ('Tue, 1 May 2001 07:58:00 -0700', (905837625, 905837655), datetime.datetime(2001, 5, 1, 7, 58, 0, tzinfo=TZ_MINUS_0700)),  # mann-k/all_documents/5343.
    ('Fri, 15 Sep 2000 09:29:00 -0700', (910040425, 910040456), datetime.datetime(2000, 9, 15, 9, 29, 0, tzinfo=TZ_MINUS_0700)),  # mann-k/chicago/71.
    ('Mon, 12 Feb 2001 09:31:00 -0800', (913945694, 913945725), datetime.datetime(2001, 2, 12, 9, 31, 0, tzinfo=TZ_MINUS_0800)),  # mann-k/discussion_threads/2526.
    ('Thu, 24 May 2001 12:11:00 -0700', (918138920, 918138951), datetime.datetime(2001, 5, 24, 12, 11, 0, tzinfo=TZ_MINUS_0700)),  # mann-k/discussion_threads/4361.
    ('Tue, 27 Nov 2001 13:35:58 -0800', (922442760, 922442791), datetime.datetime(2001, 11, 27, 13, 35, 58, tzinfo=TZ_MINUS_0800)),  # mann-k/inbox/373.
    ('Wed, 6 Dec 2000 00:47:00 -0800', (926360470, 926360500), datetime.datetime(2000, 12, 6, 0, 47, 0, tzinfo=TZ_MINUS_0800)),  # mann-k/sent/1726.
    ('Mon, 31 Jul 2000 02:49:00 -0700', (929934984, 929935015), datetime.datetime(2000, 7, 31, 2, 49, 0, tzinfo=TZ_MINUS_0700)),  # mann-k/sent/356.
    ('Mon, 26 Mar 2001 23:42:00 -0800', (933665209, 933665240), datetime.datetime(2001, 3, 26, 23, 42, 0, tzinfo=TZ_MINUS_0800)),  # mann-k/yazoo_city/22.
    ('Wed, 30 Jan 2002 14:35:25 -0800', (948306172, 948306203), datetime.datetime(2002, 1, 30, 14, 35, 25, tzinfo=TZ_MINUS_0800)),  # may-l/inbox/38.
    ('Thu, 17 May 2001 12:45:00 -0700', (955132286, 955132317), datetime.datetime(2001, 5, 17, 12, 45, 0, tzinfo=TZ_MINUS_0700)),  # mcconnell-m/_sent_mail/56.
    ('Fri, 9 Feb 2001 05:03:00 -0800', (959766577, 959766607), datetime.datetime(2001, 2, 9, 5, 3, 0, tzinfo=TZ_MINUS_0800)),  # mcconnell-m/discussion_threads/432.
    ('Fri, 11 May 2001 05:50:00 -0700', (964125254, 964125285), datetime.datetime(2001, 5, 11, 5, 50, 0, tzinfo=TZ_MINUS_0700)),  # mckay-b/_sent_mail/30.
    ('Fri, 2 Feb 2001 12:11:00 -0800', (970797918, 970797948), datetime.datetime(2001, 2, 2, 12, 11, 0, tzinfo=TZ_MINUS_0800)),  # mclaughlin-e/all_documents/147.
    ('Wed, 28 Nov 2001 19:41:02 -0800', (975371905, 975371936), datetime.datetime(2001, 11, 28, 19, 41, 2, tzinfo=TZ_MINUS_0800)),  # mclaughlin-e/inbox/217.
    ('Thu, 12 Apr 2001 01:27:00 -0700', (980066378, 980066409), datetime.datetime(2001, 4, 12, 1, 27, 0, tzinfo=TZ_MINUS_0700)),  # merriss-s/discussion_threads/96.
    ('Tue, 20 Mar 2001 07:42:00 -0800', (983874198, 983874229), datetime.datetime(2001, 3, 20, 7, 42, 0, tzinfo=TZ_MINUS_0800)),  # mims-thurston-p/all_documents/35.
    ('Fri, 8 Mar 2002 14:16:54 -0800', (990174101, 990174131), datetime.datetime(2002, 3, 8, 14, 16, 54, tzinfo=TZ_MINUS_0800)),  # motley-m/sent_items/4.
    ('Tue, 8 May 2001 03:13:00 -0700', (995171764, 995171794), datetime.datetime(2001, 5, 8, 3, 13, 0, tzinfo=TZ_MINUS_0700)),  # neal-s/discussion_threads/350.
    ('Tue, 31 Aug 1999 04:01:00 -0700', (999550175, 999550206), datetime.datetime(1999, 8, 31, 4, 1, 0, tzinfo=TZ_MINUS_0700)),  # nemec-g/all_documents/171.
    ('Mon, 26 Mar 2001 01:25:00 -0800', (1003213572, 1003213603), datetime.datetime(2001, 3, 26, 1, 25, 0, tzinfo=TZ_MINUS_0800)),  # nemec-g/all_documents/5517.
    ('Thu, 13 Dec 2001 10:31:54 -0800', (1007603200, 1007603231), datetime.datetime(2001, 12, 13, 10, 31, 54, tzinfo=TZ_MINUS_0800)),  # nemec-g/inbox/1421.
    ('Mon, 12 Mar 2001 15:16:00 -0800', (1012472296, 1012472327), datetime.datetime(2001, 3, 12, 15, 16, 0, tzinfo=TZ_MINUS_0800)),  # nemec-g/notes_inbox/1950.
    ('Tue, 20 Mar 2001 07:09:00 -0800', (1016405088, 1016405119), datetime.datetime(2001, 3, 20, 7, 9, 0, tzinfo=TZ_MINUS_0800)),  # nemec-g/sent/2274.
    ('Tue, 20 Nov 2001 14:19:51 -0800', (1019917346, 1019917377), datetime.datetime(2001, 11, 20, 14, 19, 51, tzinfo=TZ_MINUS_0800)),  # panus-s/deleted_items/343.
    ('Thu, 14 Mar 2002 13:07:13 -0800', (1025231635, 1025231666), datetime.datetime(2002, 3, 14, 13, 7, 13, tzinfo=TZ_MINUS_0800)),  # parks-j/sent_items/228.
    ('Fri, 27 Apr 2001 03:27:00 -0700', (1028382502, 1028382533), datetime.datetime(2001, 4, 27, 3, 27, 0, tzinfo=TZ_MINUS_0700)),  # perlingiere-d/all_documents/2695.
    ('Thu, 8 Mar 2001 01:39:00 -0800', (1032099421, 1032099451), datetime.datetime(2001, 3, 8, 1, 39, 0, tzinfo=TZ_MINUS_0800)),  # perlingiere-d/sent/2182.
    ('Fri, 19 Oct 2001 08:49:05 -0700', (1035155741, 1035155772), datetime.datetime(2001, 10, 19, 8, 49, 5, tzinfo=TZ_MINUS_0700)),  # pimenov-v/deleted_items/260.
    ('Mon, 15 Oct 2001 10:15:43 -0700', (1041601316, 1041601347), datetime.datetime(2001, 10, 15, 10, 15, 43, tzinfo=TZ_MINUS_0700)),  # presto-k/deleted_items/716.
    ('Tue, 23 Oct 2001 00:41:45 -0700', (1047385744, 1047385775), datetime.datetime(2001, 10, 23, 0, 41, 45, tzinfo=TZ_MINUS_0700)),  # quigley-d/deleted_items/218.
    ('Fri, 2 Nov 2001 14:46:22 -0800', (1053677150, 1053677180), datetime.datetime(2001, 11, 2, 14, 46, 22, tzinfo=TZ_MINUS_0800)),  # reitmeyer-j/inbox/379.
    ('Wed, 22 Aug 2001 14:55:00 -0700', (1058924074, 1058924105), datetime.datetime(2001, 8, 22, 14, 55, 0, tzinfo=TZ_MINUS_0700)),  # ring-r/eesirenewableenergy/168.
    ('Fri, 7 Jul 2000 12:06:00 -0700', (1061830518, 1061830548), datetime.datetime(2000, 7, 7, 12, 6, 0, tzinfo=TZ_MINUS_0700)),  # rodrique-r/canada/19.
    ('Thu, 6 Jan 2000 02:13:00 -0800', (1063820174, 1063820204), datetime.datetime(2000, 1, 6, 2, 13, 0, tzinfo=TZ_MINUS_0800)),  # rogers-b/_sent_mail/838.
    ('Thu, 21 Sep 2000 14:36:00 -0700', (1067240957, 1067240988), datetime.datetime(2000, 9, 21, 14, 36, 0, tzinfo=TZ_MINUS_0700)),  # rogers-b/all_documents/879.
    ('Tue, 21 Mar 2000 03:11:00 -0800', (1071376967, 1071376998), datetime.datetime(2000, 3, 21, 3, 11, 0, tzinfo=TZ_MINUS_0800)),  # rogers-b/discussion_threads/421.
    ('Mon, 4 Dec 2000 07:49:00 -0800', (1076227286, 1076227316), datetime.datetime(2000, 12, 4, 7, 49, 0, tzinfo=TZ_MINUS_0800)),  # rogers-b/personal/78.
    ('Mon, 3 Apr 2000 11:39:00 -0700', (1079559478, 1079559508), datetime.datetime(2000, 4, 3, 11, 39, 0, tzinfo=TZ_MINUS_0700)),  # ruscitti-k/discussion_threads/52.
    ('Mon, 14 Aug 2000 05:26:00 -0700', (1084281731, 1084281762), datetime.datetime(2000, 8, 14, 5, 26, 0, tzinfo=TZ_MINUS_0700)),  # sager-e/all_documents/44.
    ('Fri, 8 Dec 2000 02:58:00 -0800', (1089427330, 1089427360), datetime.datetime(2000, 12, 8, 2, 58, 0, tzinfo=TZ_MINUS_0800)),  # sager-e/notes_inbox/455.
    ('Tue, 13 Nov 2001 06:52:05 -0800', (1093421201, 1093421232), datetime.datetime(2001, 11, 13, 6, 52, 5, tzinfo=TZ_MINUS_0800)),  # saibi-e/inbox/1109.
    ('Mon, 9 Jul 2001 10:43:17 -0700', (1099919905, 1099919935), datetime.datetime(2001, 7, 9, 10, 43, 17, tzinfo=TZ_MINUS_0700)),  # salisbury-h/inbox/909.
    ('Fri, 25 May 2001 01:30:00 -0700', (1106153463, 1106153494), datetime.datetime(2001, 5, 25, 1, 30, 0, tzinfo=TZ_MINUS_0700)),  # sanders-r/all_documents/2103.
    ('Wed, 19 Dec 2001 14:28:57 -0800', (1111068046, 1111068077), datetime.datetime(2001, 12, 19, 14, 28, 57, tzinfo=TZ_MINUS_0800)),  # sanders-r/deleted_items/246.
    ('Tue, 24 Apr 2001 02:56:00 -0700', (1117896315, 1117896346), datetime.datetime(2001, 4, 24, 2, 56, 0, tzinfo=TZ_MINUS_0700)),  # sanders-r/sent/1033.
    ('Sun, 12 Nov 2000 08:03:00 -0800', (1122420124, 1122420155), datetime.datetime(2000, 11, 12, 8, 3, 0, tzinfo=TZ_MINUS_0800)),  # sanders-r/tenaska/36.
    ('Mon, 9 Jul 2001 05:53:45 -0700', (1128309259, 1128309289), datetime.datetime(2001, 7, 9, 5, 53, 45, tzinfo=TZ_MINUS_0700)),  # schoolcraft-d/sent_items/150.
    ('Wed, 23 Aug 2000 09:24:00 -0700', (1132766506, 1132766537), datetime.datetime(2000, 8, 23, 9, 24, 0, tzinfo=TZ_MINUS_0700)),  # scott-s/_sent_mail/690.
    ('Wed, 13 Dec 2000 05:16:00 -0800', (1138879717, 1138879748), datetime.datetime(2000, 12, 13, 5, 16, 0, tzinfo=TZ_MINUS_0800)),  # scott-s/all_documents/939.
    ('Wed, 19 Apr 2000 05:43:00 -0700', (1146262063, 1146262094), datetime.datetime(2000, 4, 19, 5, 43, 0, tzinfo=TZ_MINUS_0700)),  # scott-s/discussion_threads/880.
    ('Mon, 18 Sep 2000 09:02:00 -0700', (1153069436, 1153069467), datetime.datetime(2000, 9, 18, 9, 2, 0, tzinfo=TZ_MINUS_0700)),  # scott-s/sent/651.
    ('Thu, 16 Dec 1999 05:03:00 -0800', (1157378033, 1157378064), datetime.datetime(1999, 12, 16, 5, 3, 0, tzinfo=TZ_MINUS_0800)),  # shackleton-s/all_documents/1013.
    ('Wed, 29 Mar 2000 08:42:00 -0800', (1162215509, 1162215540), datetime.datetime(2000, 3, 29, 8, 42, 0, tzinfo=TZ_MINUS_0800)),  # shackleton-s/all_documents/1572.
    ('Fri, 8 Sep 2000 08:45:00 -0700', (1166155273, 1166155303), datetime.datetime(2000, 9, 8, 8, 45, 0, tzinfo=TZ_MINUS_0700)),  # shackleton-s/all_documents/3416.
    ('Thu, 16 Sep 1999 08:55:00 -0700', (1170651722, 1170651753), datetime.datetime(1999, 9, 16, 8, 55, 0, tzinfo=TZ_MINUS_0700)),  # shackleton-s/all_documents/562.
    ('Wed, 12 Jan 2000 07:51:00 -0800', (1175045652, 1175045683), datetime.datetime(2000, 1, 12, 7, 51, 0, tzinfo=TZ_MINUS_0800)),  # shackleton-s/brazil/1.
    ('Mon, 11 Mar 2002 14:55:52 -0800', (1180874855, 1180874886), datetime.datetime(2002, 3, 11, 14, 55, 52, tzinfo=TZ_MINUS_0800)),  # shackleton-s/inbox/794.
    ('Mon, 23 Apr 2001 02:24:00 -0700', (1185507076, 1185507107), datetime.datetime(2001, 4, 23, 2, 24, 0, tzinfo=TZ_MINUS_0700)),  # shackleton-s/notes_inbox/2427.
    ('Thu, 23 Mar 2000 05:20:00 -0800', (1190640637, 1190640668), datetime.datetime(2000, 3, 23, 5, 20, 0, tzinfo=TZ_MINUS_0800)),  # shackleton-s/sent/1111.
    ('Wed, 3 Jan 2001 08:34:00 -0800', (1194124981, 1194125011), datetime.datetime(2001, 1, 3, 8, 34, 0, tzinfo=TZ_MINUS_0800)),  # shackleton-s/sent/5242.
    ('Wed, 20 Mar 2002 11:24:36 -0800', (1198099352, 1198099383), datetime.datetime(2002, 3, 20, 11, 24, 36, tzinfo=TZ_MINUS_0800)),  # shackleton-s/sent_items/488.
    ('Fri, 26 Oct 2001 07:17:58 -0700', (1202876819, 1202876850), datetime.datetime(2001, 10, 26, 7, 17, 58, tzinfo=TZ_MINUS_0700)),  # shankman-j/deleted_items/71.
    ('Mon, 2 Oct 2000 06:32:00 -0700', (1207909931, 1207909961), datetime.datetime(2000, 10, 2, 6, 32, 0, tzinfo=TZ_MINUS_0700)),  # shankman-j/sent/999.
    ('Mon, 17 Sep 2001 06:45:21 -0700', (1215076190, 1215076221), datetime.datetime(2001, 9, 17, 6, 45, 21, tzinfo=TZ_MINUS_0700)),  # shapiro-r/deleted_items/1155.
    ('Thu, 10 May 2001 07:28:00 -0700', (1223743619, 1223743650), datetime.datetime(2001, 5, 10, 7, 28, 0, tzinfo=TZ_MINUS_0700)),  # shapiro-r/discussion_threads/477.
    ('Thu, 1 Mar 2001 09:05:00 -0800', (1231402518, 1231402548), datetime.datetime(2001, 3, 1, 9, 5, 0, tzinfo=TZ_MINUS_0800)),  # shapiro-r/wholesale_markets/29.
    ('Tue, 24 Apr 2001 07:38:03 -0700', (1236081313, 1236081344), datetime.datetime(2001, 4, 24, 7, 38, 3, tzinfo=TZ_MINUS_0700)),  # shively-h/tasks/4.
    ('Sat, 18 Nov 2000 05:01:00 -0800', (1241716826, 1241716857), datetime.datetime(2000, 11, 18, 5, 1, 0, tzinfo=TZ_MINUS_0800)),  # skilling-j/discussion_threads/272.
    ('Fri, 17 Nov 2000 06:42:00 -0800', (1248109226, 1248109257), datetime.datetime(2000, 11, 17, 6, 42, 0, tzinfo=TZ_MINUS_0800)),  # skilling-j/sent/705.
    ('Fri, 25 Jan 2002 07:56:28 -0800', (1252043511, 1252043542), datetime.datetime(2002, 1, 25, 7, 56, 28, tzinfo=TZ_MINUS_0800)),  # solberg-g/deleted_items/250.
    ('Wed, 5 Apr 2000 05:18:00 -0700', (1257950241, 1257950271), datetime.datetime(2000, 4, 5, 5, 18, 0, tzinfo=TZ_MINUS_0700)),  # stclair-c/all_documents/19.
    ('Tue, 9 May 2000 09:48:00 -0700', (1261551046, 1261551076), datetime.datetime(2000, 5, 9, 9, 48, 0, tzinfo=TZ_MINUS_0700)),  # stclair-c/sent/323.
    ('Thu, 4 Oct 2001 16:31:41 -0700', (1267803110, 1267803140), datetime.datetime(2001, 10, 4, 16, 31, 41, tzinfo=TZ_MINUS_0700)),  # steffes-j/granite_ii/1.
    ('Thu, 19 Jul 2001 17:17:00 -0700', (1273987307, 1273987338), datetime.datetime(2001, 7, 19, 17, 17, 0, tzinfo=TZ_MINUS_0700)),  # steffes-j/to_do/2.
    ('Fri, 3 Aug 2001 13:01:59 -0700', (1280378590, 1280378620), datetime.datetime(2001, 8, 3, 13, 1, 59, tzinfo=TZ_MINUS_0700)),  # stokley-c/chris_stokley/sent/336.
    ('Wed, 6 Feb 2002 05:40:35 -0800', (1285740028, 1285740058), datetime.datetime(2002, 2, 6, 5, 40, 35, tzinfo=TZ_MINUS_0800)),  # sturm-f/deleted_items/9.
    ('Tue, 13 Feb 2001 04:29:00 -0800', (1289869956, 1289869987), datetime.datetime(2001, 2, 13, 4, 29, 0, tzinfo=TZ_MINUS_0800)),  # symes-k/_sent_mail/735.
    ('Mon, 26 Mar 2001 06:48:00 -0800', (1294256611, 1294256642), datetime.datetime(2001, 3, 26, 6, 48, 0, tzinfo=TZ_MINUS_0800)),  # symes-k/all_documents/2840.
    ('Tue, 19 Dec 2000 07:01:00 -0800', (1299340191, 1299340222), datetime.datetime(2000, 12, 19, 7, 1, 0, tzinfo=TZ_MINUS_0800)),  # symes-k/deal_communication/deal_discrepancies/198.
    ('Thu, 8 Mar 2001 08:03:00 -0800', (1303005575, 1303005605), datetime.datetime(2001, 3, 8, 8, 3, 0, tzinfo=TZ_MINUS_0800)),  # symes-k/discussion_threads/2259.
    ('Thu, 22 Mar 2001 07:25:00 -0800', (1307646749, 1307646780), datetime.datetime(2001, 3, 22, 7, 25, 0, tzinfo=TZ_MINUS_0800)),  # symes-k/it/84.
    ('Thu, 17 Feb 2000 23:46:00 -0800', (1313355612, 1313355643), datetime.datetime(2000, 2, 17, 23, 46, 0, tzinfo=TZ_MINUS_0800)),  # taylor-m/all_documents/1312.
    ('Tue, 5 Sep 2000 08:01:00 -0700', (1318200834, 1318200864), datetime.datetime(2000, 9, 5, 8, 1, 0, tzinfo=TZ_MINUS_0700)),  # taylor-m/all_documents/3153.
    ('Wed, 14 Mar 2001 04:42:00 -0800', (1323120347, 1323120378), datetime.datetime(2001, 3, 14, 4, 42, 0, tzinfo=TZ_MINUS_0800)),  # taylor-m/all_documents/7951.
    ('Wed, 8 Aug 2001 07:42:20 -0700', (1328198381, 1328198411), datetime.datetime(2001, 8, 8, 7, 42, 20, tzinfo=TZ_MINUS_0700)),  # taylor-m/contacts/10.
    ('Tue, 12 Sep 2000 03:07:00 -0700', (1335396489, 1335396520), datetime.datetime(2000, 9, 12, 3, 7, 0, tzinfo=TZ_MINUS_0700)),  # taylor-m/notes_inbox/1416.
    ('Mon, 12 Jun 2000 10:51:00 -0700', (1340596995, 1340597026), datetime.datetime(2000, 6, 12, 10, 51, 0, tzinfo=TZ_MINUS_0700)),  # taylor-m/notes_inbox/761.
    ('Mon, 18 Oct 1999 04:17:00 -0700', (1345797076, 1345797107), datetime.datetime(1999, 10, 18, 4, 17, 0, tzinfo=TZ_MINUS_0700)),  # taylor-m/sent/547.
    ('Tue, 20 Nov 2001 08:44:05 -0800', (1349846214, 1349846245), datetime.datetime(2001, 11, 20, 8, 44, 5, tzinfo=TZ_MINUS_0800)),  # tholt-j/deleted_items/185.
    ('Fri, 26 Oct 2001 08:12:47 -0700', (1357070430, 1357070461), datetime.datetime(2001, 10, 26, 8, 12, 47, tzinfo=TZ_MINUS_0700)),  # thomas-p/inbox/196.
    ('Tue, 9 Oct 2001 08:07:02 -0700', (1363217657, 1363217687), datetime.datetime(2001, 10, 9, 8, 7, 2, tzinfo=TZ_MINUS_0700)),  # tycholiz-b/sent_items/143.
    ('Thu, 22 Mar 2001 08:43:00 -0800', (1367682991, 1367683022), datetime.datetime(2001, 3, 22, 8, 43, 0, tzinfo=TZ_MINUS_0800)),  # ward-k/palo_alto/2.
    ('Fri, 4 Jan 2002 13:12:21 -0800', (1373466945, 1373466975), datetime.datetime(2002, 1, 4, 13, 12, 21, tzinfo=TZ_MINUS_0800)),  # watson-k/e_mail_bin/667.
    ('Tue, 13 Feb 2001 07:26:00 -0800', (1378058720, 1378058751), datetime.datetime(2001, 2, 13, 7, 26, 0, tzinfo=TZ_MINUS_0800)),  # weldon-c/all_documents/220.
    ('Thu, 25 Oct 2001 14:41:54 -0700', (1383242125, 1383242156), datetime.datetime(2001, 10, 25, 14, 41, 54, tzinfo=TZ_MINUS_0700)),  # whalley-g/deleted_items/13.
    ('Tue, 5 Dec 2000 03:56:00 -0800', (1389927074, 1389927104), datetime.datetime(2000, 12, 5, 3, 56, 0, tzinfo=TZ_MINUS_0800)),  # whalley-l/all_documents/50.
    ('Thu, 21 Jun 2001 10:34:00 -0700', (1395809721, 1395809752), datetime.datetime(2001, 6, 21, 10, 34, 0, tzinfo=TZ_MINUS_0700)),  # whalley-l/notes_inbox/5.
    ('Tue, 13 Mar 2001 05:21:00 -0800', (1400313972, 1400314003), datetime.datetime(2001, 3, 13, 5, 21, 0, tzinfo=TZ_MINUS_0800)),  # white-s/ena_cal/2.
    ('Fri, 12 Oct 2001 10:57:02 -0700', (1403914730, 1403914761), datetime.datetime(2001, 10, 12, 10, 57, 2, tzinfo=TZ_MINUS_0700)),  # whitt-m/inbox/400.
    ('Thu, 9 Aug 2001 08:57:47 -0700', (1409643665, 1409643695), datetime.datetime(2001, 8, 9, 8, 57, 47, tzinfo=TZ_MINUS_0700)),  # williams-w3/bill_williams_iii/347.
    ('Tue, 15 Jan 2002 22:36:48 -0800', (1414130182, 1414130213), datetime.datetime(2002, 1, 15, 22, 36, 48, tzinfo=TZ_MINUS_0800)),  # williams-w3/schedule_crawler/575.
    ('Tue, 6 Mar 2001 16:37:00 -0800', (1419039558, 1419039588), datetime.datetime(2001, 3, 6, 16, 37, 0, tzinfo=TZ_MINUS_0800)),  # wolfe-j/discussion_threads/91.
    ('Thu, 12 Apr 2001 07:36:00 -0700', (1425492680, 1425492711), datetime.datetime(2001, 4, 12, 7, 36, 0, tzinfo=TZ_MINUS_0700)),  # zipper-a/broker_client/21.
    ('Mon, 26 Nov 2001 10:48:43 -0800', (1430124791, 1430124822), datetime.datetime(2001, 11, 26, 10, 48, 43, tzinfo=TZ_MINUS_0800)),  # zufferli-j/sent_items/99.
]

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
    "gold_status": "broad_sample",
    "text": None,
    "expected": MATCHED_TEXT,
    "context_expected": CONTEXT_MATCHED_TEXT_CASES,
    "forbidden": FORBIDDEN,
}
