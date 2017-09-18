"""ValidationMessages
Used to store validation error messages
"""


class ValidationMessages(object):
    """Families class
    Contains logic for processing family tags
    """

    def __init__(self):
        self._messages = []

    def add_message(self, message):
        """add a new message.  Make sure to include the id of the person or family.
        If it's a person include their name

        Args:
            message: (str) validation error message
        """
        self._messages.append({
            "message": message
        })

    def get_messages(self):
        """returns all the messages.  Each message is a dict with an attribute "message".
        """
        return self._messages

    def print_all(self):
        """print all messages
        """
        for msg in self._messages:
            print(msg["message"])
