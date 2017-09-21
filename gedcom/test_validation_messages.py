"""Test cases for validation messages module
"""
import unittest
import io
import sys
from validation_messages import ValidationMessages
from people import People


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
        self.msgs.add_message(People.CLASS_IDENTIFIER, "US02", "@I7@", "Test Name", "There is an issue here")
        # ensure nothing got added
        output = self.msgs.get_messages()
        self.assertEqual(1, len(output))

    def test_print_all(self):
        """test print all messages
        """
        self.msgs.add_message(People.CLASS_IDENTIFIER, "US02", "@I7@", "Test Name", "There is an issue here")

        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.msgs.print_all()
        sys.stdout = sys.__stdout__
        test_output = """+------------+------------+------+-----------+------------------------+
| Error Type | User Story |  ID  |    Name   |        Message         |
+------------+------------+------+-----------+------------------------+
| INDIVIDUAL |    US02    | @I7@ | Test Name | There is an issue here |
+------------+------------+------+-----------+------------------------+
"""
        self.assertEqual(test_output, output.getvalue())
