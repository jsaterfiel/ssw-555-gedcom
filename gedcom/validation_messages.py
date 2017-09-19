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

    def add_message(self, identifier: str, name: str, message: str):
        """add a new message.  Make sure to include the id of the person or family.
        If it's a person include their name

        Args:
            identifier: (str) identifier string
            name: (str) name of individual or family
            message: (str) validation error message
        """
        self._messages.append({
            "id": identifier,
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
        messages = sorted(self._messages, key=lambda msg: msg['id'])

        pretty_table = PrettyTable(["ID", "Name", "Message"])
        for message in messages:
            pretty_table.add_row([message["id"], message["name"], message["message"]])

        print(pretty_table)
