"""Family GEDCOM
Single family object in GEDCOM with helper methods
"""
from datetime import datetime


class Family(object):
    """Family class
    Data object for a family

    Args:
        family_id (string): id of family
    """
    CLASS_IDENTIFIER = "FAMILY"

    def __init__(self, family_id):
        self._family_id = family_id
        self._children = []
        self._husband_id = None
        self._wife_id = None
        self._married_date = None
        self._divorced_date = None

    def get_family_id(self):
        """returns the family id
        Returns:
            string
        """
        return self._family_id

    def get_children(self):
        """returns all the children as a list of ids
        Returns:
            string[]
        """
        return self._children

    def add_child(self, child_id):
        """add a single child id
        Args:
            child_id (string): child id
        """
        self._children.append(child_id)

    def get_husband_id(self):
        """returns husband_id
        Returns:
            string
        """
        return self._husband_id

    def set_husband_id(self, husband_id):
        """sets husband_id
        Args:
            husband_id (string): husband id
        """
        self._husband_id = husband_id

    def get_wife_id(self):
        """returns wife_id
        Returns:
            string
        """
        return self._wife_id

    def set_wife_id(self, wife_id):
        """set wife_id
        Args:
            wife_id (string): wife id
        """
        self._wife_id = wife_id

    def get_married_date(self):
        """returns married date
        Returns:
            datetime
        """
        return self._married_date

    def get_divorced_date(self):
        """returns divorced date
        Returns:
            datetime
        """
        return self._divorced_date

    def set_date(self, date_string, date_type):
        """returns the date in datetime convention from a string
        Returns:

        """
        if date_type == "married":
            self._married_date = datetime.strptime(date_string, '%d %b %Y')
        if date_type == "divorced":
            self._divorced_date = datetime.strptime(date_string, '%d %b %Y')
