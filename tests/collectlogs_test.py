import unittest

import composer.collectlogs as collectlogs


class SampleLogs(unittest.TestCase):
    daylog = ("= WEDNESDAY APR 1, 2015 =\n"
                    "\n"
                    "CHECKPOINTS:\n"
                    "[x] 7:00am - wake up [10:50]\n"
                    "[x] 7:00am - $open blinds$ [11:00?]\n"
                    "[ ] 7:05am - 20 mins meditation (incl. develop mental picture of the day) []\n"
                    "[x] 7:25am - brush + change [10:50]\n"
                    "[-] 7:00pm - leave for home (read book on train/at home) []\n"
                    "[-] 8:00pm - reach home []\n"
                    "[ ] 11:10pm - update schedule []\n"
                    "[ ] 11:15pm - get stuff ready for morning((1) clothes:shirt,underwear,jeans,jacket,belt; (2) laptop+charger; (3) binder+texts+pen+pencil; (4) headphones) []\n"
                    "[ ] 11:30pm - sleep []\n"
                    "\n"
                    "AGENDA:\n"
                    "[ ] do something\n"
                    "[o] scheduled thing [$MAY 2015$]\n"
                    "\t[ ] subthing\n"
                    "[ ] something else\n"
                    "\t[ ] another thing\n"
                    "\t[x] done\n"
                    "\t[\] partially done\n"
                    "[\] partially done thing\n"
                    "[x] done thing\n"
                    "\n"
                    "DAILYs:\n"
                    "[ ] 40 mins gym\n"
                    "[ ] Make bed\n"
                    "[ ] 3 meals\n"
                    "[ ] floss\n"
                    "[ ] Update schedule [$check on meags$]\n"
                    "\n"
                    "NOTES:\n"
                    "Notes for the day.\n"
                    "\n"
                    "\n"
                    "TIME SPENT ON PLANNER: 10 mins")

    def test_day_log_extraction(self):
        expected_log = "Notes for the day."
        expected_time = "10 mins"
        self.assertEqual(collectlogs.extract_log_time_from_text(self.daylog), (expected_log, expected_time))
