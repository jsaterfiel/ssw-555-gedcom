"""Families GEDCOM
Parses
"""

class Families:
    """Families class
    """
    def __init__(self):
        self._families = []

    def process_line_data(self, data):
        """process_line_data will process line data
        """
        self._families.append(data)

    def hello_world(self):
        """hello
        """
        self._families = []
