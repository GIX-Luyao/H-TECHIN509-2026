"""Baseline checks: 7 pass, 1 intentionally fails in the supplied starter."""
import unittest
from unittest.mock import patch
from assistant import handle
from backend import NO_CODE
from memory import initial_history


class AssistantChecks(unittest.TestCase):
    def setUp(self):
        self.history = initial_history()

    def test_normal_exchange_is_stored(self):
        answer, done = handle(self.history, "Hello")
        self.assertFalse(done)
        self.assertEqual([m["role"] for m in self.history], ["system", "user", "assistant"])
        self.assertEqual(self.history[-1]["content"], answer)

    def test_reported_recall(self):
        handle(self.history, "My project code is ORBIT-17")
        answer, _ = handle(self.history, "What is my project code?")
        self.assertEqual(answer, "Your project code is ORBIT-17.")

    def test_question_before_fact(self):
        self.assertEqual(handle(self.history, "What is my project code?")[0], NO_CODE)

    def test_show_is_read_only(self):
        handle(self.history, "Hello")
        before = [dict(m) for m in self.history]
        with patch("assistant.reply") as backend:
            output, done = handle(self.history, "/show")
        backend.assert_not_called()
        self.assertIn("[user] Hello", output)
        self.assertEqual(self.history, before)
        self.assertFalse(done)

    def test_reset_preserves_system(self):
        system = dict(self.history[0])
        handle(self.history, "Hello")
        with patch("assistant.reply") as backend:
            _, done = handle(self.history, "/reset")
        backend.assert_not_called()
        self.assertEqual(self.history, [system])
        self.assertFalse(done)

    def test_reset_forgets_fact(self):
        handle(self.history, "My project code is ORBIT-17")
        handle(self.history, "/reset")
        self.assertEqual(handle(self.history, "What is my project code?")[0], NO_CODE)

    def test_exit_is_read_only(self):
        before = [dict(m) for m in self.history]
        with patch("assistant.reply") as backend:
            _, done = handle(self.history, "/exit")
        backend.assert_not_called()
        self.assertTrue(done)
        self.assertEqual(self.history, before)

    def test_blank_is_read_only(self):
        before = [dict(m) for m in self.history]
        with patch("assistant.reply") as backend:
            self.assertEqual(handle(self.history, "   "), ("", False))
        backend.assert_not_called()
        self.assertEqual(self.history, before)


if __name__ == "__main__":
    unittest.main()
