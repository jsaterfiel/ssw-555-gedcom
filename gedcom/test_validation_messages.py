"""Test cases for validation messages module
"""
import unittest
import io
import sys
from validation_messages import ValidationMessages


class TestValidationMessages(unittest.TestCase):
    """test cases for families class
    Attributes:
        fam (Families): Family test object
    """

    def setUp(self):
        """creates message object
        """
        self.msgs = ValidationMessages()

    def tearDown(self):
        """delete message object
        """
        del self.msgs

    def test_default_init(self):
        """make sure the object is empty on init
        """
        self.assertEqual(0, len(self.msgs.get_messages()))

    def test_add_message(self):
        """ensure message is added
        """
        msg = "Hello world!"
        self.msgs.add_message(msg)
        # ensure nothing got added
        output = self.msgs.get_messages()
        self.assertEqual(1, len(output))
        self.assertEqual(msg, output[0]["message"])

    def test_print_all(self):
        """test print all messages
        """
        self.msgs.add_message("test message 1")
        self.msgs.add_message("test message 2")
        self.msgs.add_message("test message 3")

        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.msgs.print_all()
        sys.stdout = sys.__stdout__
        test_output = """test message 1
test message 2
test message 3
"""
        self.assertEqual(test_output, output.getvalue())
