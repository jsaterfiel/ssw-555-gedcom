"""Person GEDCOM
Single person object in GEDCOM with helper methods
"""
from datetime import datetime


class Person(object):
    """People class
    Contains logic for processing person (INDI) tags

    Args:
        person_id (string): id of person
    """
    CLASS_IDENTIFIER = "INDIVIDUAL"
    DAYS_IN_YEAR = 365.2425
    CURRENT_TIME = datetime.now()

    def __init__(self, person_id):
        self._person_id = person_id
        self._name = ""
        self._gender = ""
        self._is_alive = True  # Automatically set by having death deate
        self._birth_date = None
        self._death_date = None
        self._child_of_families = []
        self._spouse_of_families = []
        self._age = None  # age calculated automatically

    def get_person_id(self):
        """returns the person id
        Returns:
            string
        """
        return self._person_id

    def get_name(self):
        """returns name
        Returns:
            string
        """
        return self._name

    def set_name(self, name):
        """sets name
        Args:
            name (string): name
        """
        self._name = name

    def get_gender(self):
        """returns gender
        Returns:
            string
        """
        return self._gender

    def set_gender(self, gender):
        """sets gender
        Args:
            gender (string): gender ("M", "F" or None only)
        """
        if(gender == "M" or gender == "F"):
            self._gender = gender

    def get_is_alive(self):
        """returns is_alive
        Returns:
            boolean
        """
        return self._is_alive

    def get_birth_date(self):
        """returns birth date
        Returns:
            datetime
        """
        return self._birth_date

    def get_death_date(self):
        """returns death date
        Returns:
            datetime
        """
        return self._death_date

    def set_date(self, date_string, date_type):
        """creates the datetime object from the passed in string and also sets the person's age
        Args:
            date_string (string): string of the datetime to parse in the format '%d %b %Y'
            date_type (string): birth, death
        """
        if date_type == "birth":
            self._birth_date = datetime.strptime(date_string, '%d %b %Y')
            self._generate_age()
        if date_type == "death":
            self._death_date = datetime.strptime(date_string, '%d %b %Y')
            self._generate_age()
            self._is_alive = False

    def get_children_of_families(self):
        """returns family ids person is a child of
        Returns:
            string[]
        """
        return self._child_of_families

    def add_children_of_family(self, family_id):
        """add a family id the person is a child of
        Args:
            family_id (string): family id the person is a child of
        """
        self._child_of_families.append(family_id)

    def remove_children_of_family(self, family_id):
        """Remove a family id the person is a child of
        Args:
            family_id (string): family id the person is a child of
        """
        self._child_of_families.remove(family_id)

    def get_spouse_of_families(self):
        """returns family ids person is a spouse of
        Returns:
            string[]
        """
        return self._spouse_of_families

    def add_spouse_of_family(self, family_id):
        """add a family id the person is a spouse of
        Args:
            family_id (string): family id the person is a spouse of
        """
        self._spouse_of_families.append(family_id)

    def remove_spouse_of_family(self, family_id):
        """Remove a family id the person is a spouse of
        Args:
            family_id (string): family id the person is a spouse of
        """
        self._spouse_of_families.remove(family_id)

    def get_age(self):
        """returns person's age
        Returns:
            int
        """
        return self._age

    def _generate_age(self):
        """generates age of the person based on their birth and death dates
        """
        if(self._birth_date is None):
            return

        if(self._death_date is not None):
            self._age = int(
                (self._death_date - self._birth_date).days / self.DAYS_IN_YEAR)
        else:
            self._age = int(
                (self.CURRENT_TIME - self._birth_date).days / self.DAYS_IN_YEAR)
