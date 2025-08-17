import unittest
import io
import sys
from doors.debug import AutoLogMethods, SeqDebug
from doors.debug import strip_color


class ClassUnderTest(SeqDebug, metaclass=AutoLogMethods):
    def __init__(self):
        super().__init__()

    def silent_method(self):
        return 42

    def logging_method(self):
        self._log("Inside logging_method")

    def nested_method(self):
        self.silent_method()  # This won't print
        self.logging_method()  # This will cause both methods to print

    def complex(self):
        self._log("Starting complex operation")

        self.silent_method()
        self.logging_method()
        self._log("Middle of operation")
        self.silent_method()
        self._log("Ending complex operation")


class TestSeqDebug(unittest.TestCase):
    def setUp(self):
        self.captured_output = io.StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.captured_output

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_silent_method_produces_no_output(self):
        test_obj = ClassUnderTest()
        test_obj.silent_method()

        self.assertEqual(len(test_obj._msg_log), 0)
        output = strip_color(self.captured_output.getvalue())
        self.assertEqual(output.strip(), "")

    def test_logging_method_produces_output(self):
        test_obj = ClassUnderTest()
        test_obj.logging_method()

        self.assertGreater(len(test_obj._msg_log), 0)
        output = strip_color(self.captured_output.getvalue())

        expected_output = """0 logging_method()
    1 ⏐ Inside logging_method"""
        self.assertEqual(output.strip(), expected_output)

    def test_nested_method_shows_call_hierarchy(self):
        test_obj = ClassUnderTest()
        test_obj.nested_method()

        self.assertGreater(len(test_obj._msg_log), 0)
        output = strip_color(self.captured_output.getvalue())

        expected_output = """0 nested_method()
    1 ⏐ logging_method()
    2 ⏐ ⏐ Inside logging_method"""
        self.assertEqual(output.strip(), expected_output)

    def test_complex(self):
        test_obj = ClassUnderTest()
        test_obj.complex()

        self.assertGreater(len(test_obj._msg_log), 0)
        output = strip_color(self.captured_output.getvalue())

        expected_output = """0 complex()
    1 ⏐ Starting complex operation
    2 ⏐ logging_method()
    3 ⏐ ⏐ Inside logging_method
    4 ⏐ Middle of operation
    5 ⏐ Ending complex operation"""
        self.assertEqual(output.strip(), expected_output)

    def test_log_message_order(self):
        test_obj = ClassUnderTest()
        test_obj.complex()

        log_content = "\n".join(test_obj._msg_log)
        expected_log_order = [
            "complex()",
            "⏐ Starting complex operation",
            "⏐ logging_method()",
            "⏐ ⏐ Inside logging_method",
            "⏐ Middle of operation",
            "⏐ Ending complex operation",
        ]

        actual_lines = log_content.split("\n")
        self.assertEqual(len(actual_lines), len(expected_log_order))
        for actual, expected in zip(actual_lines, expected_log_order):
            self.assertEqual(actual, expected)

    def test_write_log_functionality(self):
        import tempfile
        import os

        test_obj = ClassUnderTest()
        test_obj.logging_method()

        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            test_obj._write_log(tmp_path)

            # Read back and verify
            with open(tmp_path, "r") as f:
                content = f.read()

            expected_content = """logging_method()
⏐ Inside logging_method"""
            self.assertEqual(content.strip(), expected_content)
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
