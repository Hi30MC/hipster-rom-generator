import unittest
import io
import sys
from doors.call_tree import log_calls
from doors.call_tree import FormatOptions
from doors.call_tree import CallTree


class DebuggedClass:
    def __init__(self):
        self.call_tree = CallTree()

    def _log(self, message: str):
        self.call_tree.add_message(message)

    @log_calls()
    def simple_method(self, value: int):
        return 42

    @log_calls()
    def method_with_logging(self):
        self._log("Inside method_with_logging")

    @log_calls()
    def nested_calls(self):
        self.simple_method(5)
        self.method_with_logging()

    @log_calls()
    def complex_method(self):
        self._log("Starting operation")
        self.simple_method(4)
        self.method_with_logging()
        self._log("Middle of operation")
        self.simple_method(5)
        self._log("Ending operation")


class TestSeqDebug(unittest.TestCase):
    def setUp(self):
        self.captured_output = io.StringIO()
        self.original_stdout = sys.stdout

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_simple_method_call_is_logged(self):
        obj = DebuggedClass()
        obj.simple_method(4)

        output = obj.call_tree.to_string()
        expected_output = """
simple_method(4)
""".strip()
        self.assertEqual(output.strip(), expected_output)

    def test_method_with_logging_shows_both_call_and_log(self):
        obj = DebuggedClass()
        obj.method_with_logging()

        output = obj.call_tree.to_string()
        expected_output = """
method_with_logging()
⏐ Inside method_with_logging
""".strip()
        self.assertEqual(output.strip(), expected_output)

    def test_nested_calls_show_proper_indentation(self):
        obj = DebuggedClass()
        obj.nested_calls()

        output = obj.call_tree.to_string()
        expected_output = """
nested_calls()
⏐ simple_method(5)
⏐ method_with_logging()
⏐ ⏐ Inside method_with_logging
""".strip()
        self.assertEqual(output.strip(), expected_output)

    def test_complex_method_shows_all_calls_and_logs(self):
        obj = DebuggedClass()
        obj.complex_method()

        output = obj.call_tree.to_string()
        expected_output = """
complex_method()
⏐ Starting operation
⏐ simple_method(4)
⏐ method_with_logging()
⏐ ⏐ Inside method_with_logging
⏐ Middle of operation
⏐ simple_method(5)
⏐ Ending operation
""".strip()
        self.assertEqual(output.strip(), expected_output)

    def test_yaml_formatter(self):
        obj = DebuggedClass()
        obj.complex_method()
        output = obj.call_tree.to_string(FormatOptions.yaml())
        expected_output = """
complex_method():
- Starting operation
- simple_method(4):
- method_with_logging():
  - Inside method_with_logging
- Middle of operation
- simple_method(5):
- Ending operation
        """.strip()
        self.assertEqual(output.strip(), expected_output)


if __name__ == "__main__":
    unittest.main()
