import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from sm2 import sm2_update, quality_from_correctness


class TestQualityFromCorrectness(unittest.TestCase):

    def test_correct_returns_4(self):
        self.assertEqual(quality_from_correctness(True), 4)

    def test_incorrect_returns_2(self):
        self.assertEqual(quality_from_correctness(False), 2)


class TestSm2Update(unittest.TestCase):

    def setUp(self):
        # Freeze "now" so next_review is deterministic in assertions
        self.fixed_now = datetime(2026, 7, 30, 12, 0, 0)
        patcher = patch("sm2.datetime")
        self.mock_datetime = patcher.start()
        self.mock_datetime.now.return_value = self.fixed_now
        self.addCleanup(patcher.stop)

    def test_first_correct_repetition(self):
        ef, rep, interval, next_review = sm2_update(
            ef=2.5, repetition=0, interval_days=0, quality=4
        )
        self.assertEqual(rep, 1)
        self.assertEqual(interval, 1)
        self.assertAlmostEqual(ef, 2.5, places=4)
        self.assertEqual(next_review, self.fixed_now + timedelta(days=1))

    def test_second_correct_repetition_sets_interval_to_6(self):
        ef, rep, interval, next_review = sm2_update(
            ef=2.5, repetition=1, interval_days=1, quality=4
        )
        self.assertEqual(rep, 2)
        self.assertEqual(interval, 6)
        self.assertEqual(next_review, self.fixed_now + timedelta(days=6))

    def test_third_plus_correct_repetition_multiplies_interval_by_ef(self):
        ef, rep, interval, next_review = sm2_update(
            ef=2.5, repetition=2, interval_days=6, quality=4
        )
        self.assertEqual(rep, 3)
        self.assertEqual(interval, int(6 * 2.5))  # 15
        self.assertEqual(next_review, self.fixed_now + timedelta(days=15))

    def test_incorrect_answer_resets_repetition_and_interval(self):
        ef, rep, interval, next_review = sm2_update(
            ef=2.5, repetition=5, interval_days=30, quality=2
        )
        self.assertEqual(rep, 0)
        self.assertEqual(interval, 1)
        self.assertEqual(next_review, self.fixed_now + timedelta(days=1))

    def test_total_blackout_quality_0_resets(self):
        ef, rep, interval, next_review = sm2_update(
            ef=1.3, repetition=3, interval_days=6, quality=0
        )
        self.assertEqual(rep, 0)
        self.assertEqual(interval, 1)

    def test_ease_factor_never_drops_below_1_3(self):
        ef, rep, interval, next_review = sm2_update(
            ef=1.3, repetition=0, interval_days=0, quality=0
        )
        self.assertGreaterEqual(ef, 1.3)
        self.assertEqual(ef, 1.3)

    def test_ease_factor_increases_on_perfect_quality(self):
        ef, rep, interval, next_review = sm2_update(
            ef=2.5, repetition=5, interval_days=10, quality=5
        )
        self.assertAlmostEqual(ef, 2.6, places=4)
        self.assertEqual(rep, 6)
        self.assertEqual(interval, 25)

    def test_ease_factor_decreases_on_low_but_passing_quality(self):
        ef, rep, interval, next_review = sm2_update(
            ef=2.5, repetition=0, interval_days=0, quality=3
        )
        self.assertLess(ef, 2.5)
        self.assertEqual(rep, 1)
        self.assertEqual(interval, 1)

    def test_quality_boundary_3_counts_as_correct(self):
        ef, rep, interval, next_review = sm2_update(
            ef=2.5, repetition=0, interval_days=0, quality=3
        )
        self.assertEqual(rep, 1)  # repetition incremented, not reset

    def test_interval_is_always_integer(self):
        ef, rep, interval, next_review = sm2_update(
            ef=2.37, repetition=2, interval_days=6, quality=4
        )
        self.assertIsInstance(interval, int)

    def test_return_type_is_tuple_of_four(self):
        result = sm2_update(ef=2.5, repetition=0, interval_days=0, quality=4)
        self.assertEqual(len(result), 4)
        ef, rep, interval, next_review = result
        self.assertIsInstance(ef, float)
        self.assertIsInstance(rep, int)
        self.assertIsInstance(interval, int)
        self.assertIsInstance(next_review, datetime)


if __name__ == "__main__":
    unittest.main()
