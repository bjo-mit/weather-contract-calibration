import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import kalshi
import model


class ModelTests(unittest.TestCase):
    def test_probabilities_sum_over_partition(self):
        members = [70.0, 72.5, 74.0, 75.5, 77.0]
        p_less = model.prob_event(members, "less", None, 71)
        p_mid = sum(model.prob_event(members, "between", a, a + 1) for a in range(71, 79, 2))
        p_more = model.prob_event(members, "greater", 78, None)
        self.assertAlmostEqual(p_less + p_mid + p_more, 1.0, places=6)

    def test_narrow_kernel_matches_counting(self):
        members = [70, 72, 74, 76, 78]
        p = model.prob_event(members, "greater", 73, None, sd=0.01)
        self.assertAlmostEqual(p, 3 / 5, places=4)

    def test_settlement_rules(self):
        self.assertEqual(kalshi.event_probability("greater", 76, None, 77), 1)
        self.assertEqual(kalshi.event_probability("greater", 76, None, 76), 0)
        self.assertEqual(kalshi.event_probability("less", None, 69, 68), 1)
        self.assertEqual(kalshi.event_probability("less", None, 69, 69), 0)
        self.assertEqual(kalshi.event_probability("between", 75, 76, 76), 1)
        self.assertEqual(kalshi.event_probability("between", 75, 76, 77), 0)

    def test_ticker_parse(self):
        series, date, kind, strike = kalshi.parse_ticker("KXHIGHNY-26OCT09-B75.5")
        self.assertEqual((series, date.isoformat(), kind, strike), ("KXHIGHNY", "2026-10-09", "B", 75.5))
        self.assertIsNone(kalshi.parse_ticker("KXHIGHNY-26OCT09"))


if __name__ == "__main__":
    unittest.main()
