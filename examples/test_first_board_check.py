import json
import unittest

from first_board_check import board_observation, board_rows


class BoardCheckTest(unittest.TestCase):
    def test_exact_match_and_explicit_zero(self):
        rows = [{"key": "nba_summer", "event_count": 4}, {"key": "nba", "event_count": 0}]
        self.assertEqual(board_observation(rows, "nba"), {"status": "listed", "event_count": 0})
        self.assertEqual(board_observation(rows, "n"), {"status": "not_listed", "event_count": None})

    def test_unknown_count(self):
        for count in (None, -1, False, "7"):
            with self.subTest(count=count):
                self.assertEqual(
                    board_observation([{"key": "nba", "event_count": count}], "nba"),
                    {"status": "count_unknown", "event_count": None},
                )

    def test_repeated_sport(self):
        with self.assertRaises(ValueError):
            board_observation([{"key": "nba"}, {"key": "nba"}], "nba")

    def test_current_and_legacy_responses(self):
        rows = [{"key": "nba", "event_count": 2}]
        for response in (
            {"structuredContent": {"result": rows}},
            {"content": [{"type": "text", "text": json.dumps(rows)}]},
            {"content": [{"type": "text", "text": json.dumps(rows[0])}]},
        ):
            self.assertEqual(board_rows(response), rows)
        self.assertEqual(board_rows({"structuredContent": {"result": []}}), [])

    def test_failure_is_distinct_from_empty_board(self):
        for response in (
            {"isError": True, "structuredContent": {"result": []}},
            {"content": []},
            {"content": [{"type": "text"}]},
            {"structuredContent": {"result": [{"event_count": 2}]}},
        ):
            with self.subTest(response=response), self.assertRaises(ValueError):
                board_rows(response)
