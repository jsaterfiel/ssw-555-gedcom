"""ValidationMessages
Used to store validation error messages
"""
from prettytable import PrettyTable


class ValidationMessages(object):
    """ValidationMessages
    Used to store validation error messages
    """

    def __init__(self):
        self._messages = []

    def add_message(self, error_id: str, user_story: str, user_identifier: str, name: str, message: str):
        """add a new message.  Make sure to include the id of the person or family.
        If it's a person include their name

        Args:
            user_identifier: (str) identifier string of the individual or family
            name: (str) name of individual or family
            message: (str) validation error message
            error_id: (str) Class of error that this affects. Either INDIVIDUAL or FAMILY
            user_story: (str) user story id
        """
        self._messages.append({
            "error_id": error_id,
            "user_story": user_story,
            "user_id": user_identifier,
            "name": name,
            "message": message
        })

    def get_messages(self):
        """returns all the messages.  Each message is a dict with an attribute "message".
        """
        return self._messages

    def print_all(self):
        """print all messages sorted by id of individual or family
        """
        messages = sorted(self._messages, key=lambda msg: msg['user_story'])

        pretty_table = PrettyTable(["Error Type", "User Story", "ID", "Name", "Message"])
        for message in messages:
            pretty_table.add_row(
                [message["error_id"], message["user_story"], message["user_id"], message["name"], message["message"]])

        print(pretty_table)
