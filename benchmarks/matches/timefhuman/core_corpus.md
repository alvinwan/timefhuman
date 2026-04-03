# timefhuman · core_corpus

- Source: /tmp/datefinder/bench/corpus_core.txt
- Total matches: 13

| # | match | normalized | span | context |
| ---: | --- | --- | --- | --- |
| 1 | January 4th, 2017 at 8:00pm | datetime.datetime(2017, 1, 4, 20, 0) | 19:46 | entries are due by January 4th, 2017 at 8:00pm created 01/15/2005 by ACME Inc. and ass |
| 2 | 01/15/2005 | datetime.date(2005, 1, 15) | 55:65 | by January 4th, 2017 at 8:00pm created 01/15/2005 by ACME Inc. and associates we shipped |
| 3 | 2024-11-03 18:00 | datetime.datetime(2024, 11, 3, 18, 0) | 108:124 | ACME Inc. and associates we shipped on 2024-11-03 18:00 and archived on 2024-11-09 tomorrow at |
| 4 | 2024-11-09 | datetime.date(2024, 11, 9) | 141:151 | ped on 2024-11-03 18:00 and archived on 2024-11-09 tomorrow at noon we start phase two in |
| 5 | tomorrow at noon | datetime.datetime(2018, 8, 5, 12, 0) | 152:168 | -11-03 18:00 and archived on 2024-11-09 tomorrow at noon we start phase two in 3 days we will fi |
| 6 | in 3 days | datetime.timedelta(days=3) | 188:197 | -09 tomorrow at noon we start phase two in 3 days we will finalize results we waited 20 d |
| 7 | 20 days | datetime.timedelta(days=20) | 233:240 | days we will finalize results we waited 20 days for delivery ayer recibimos el pago y m |
| 8 | ayer | datetime.date(2018, 8, 3) | 254:258 | results we waited 20 days for delivery ayer recibimos el pago y mañana enviamos el |
| 9 | mañana | datetime.date(2018, 8, 5) | 279:285 | s for delivery ayer recibimos el pago y mañana enviamos el contrato dans 2 jours la re |
| 10 | dans 2 jours | datetime.timedelta(days=2) | 307:319 | s el pago y mañana enviamos el contrato dans 2 jours la reunion est planifiee 31/08/2012 to |
| 11 | 31/08/2012 to 30/08/2013 | (datetime.date(2012, 8, 31), datetime.date(2013, 8, 30)) | 345:369 | o dans 2 jours la reunion est planifiee 31/08/2012 to 30/08/2013 Date: Tue, 23 Apr 1996 13:28:27 -0400 C |
| 12 | Tue, 23 Apr 1996 13:28:27 -0400 | datetime.datetime(1996, 4, 23, 13, 28, 27, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000))) | 376:407 | lanifiee 31/08/2012 to 30/08/2013 Date: Tue, 23 Apr 1996 13:28:27 -0400 CR is 0 for the past 40 minutes French |
| 13 | for the past 40 minutes | datetime.timedelta(days=-1, seconds=84000) | 416:439 | Tue, 23 Apr 1996 13:28:27 -0400 CR is 0 for the past 40 minutes French 75 is a cocktail and should not |
