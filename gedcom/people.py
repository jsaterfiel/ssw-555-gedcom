"""People GEDCOM
Parses person tags from the gedcom data passed to it line by line as they appear in the gedcom files
"""
from datetime import datetime
from person import Person
from prettytable import PrettyTable


class People(object):
    """People class
    Contains logic for processing person (INDI) tags

    Attributes:
        individuals: :list:Person list of Person
    """
    CLASS_IDENTIFIER = "INDIVIDUAL"

    def __init__(self, validation_messages):
        self.individuals = {}
        self._curr_person = None
        self._current_level_1 = None
        self._current_time = datetime.now()
        self._days_in_year = 365.2425
        self._msgs = validation_messages

    def process_line_data(self, data):
        """line data is a dict of the format:
        {
            "level": int,
            "tag": string,
            "args": string,
            "valid": "Y" or "N"
        }
        """
        if data["valid"] == "N":
            raise ValueError

        if data["level"] < 2:
            self._current_level_1 = None

        if data["tag"] == "INDI":
            self._curr_person = Person(data["args"])
            self.individuals.setdefault(data["args"], self._curr_person)

        if data["tag"] == "SEX":
            self._curr_person.set_gender(data["args"])
            self._current_level_1 = "SEX"

        if data["tag"] == "BIRT":
            self._current_level_1 = "BIRT"

        if data["tag"] == "DEAT":
            self._current_level_1 = "DEAT"

        if data["tag"] == "FAMC":
            self._curr_person.add_children_of_family(data["args"])
            self._current_level_1 = "FAMC"

        if data["tag"] == "FAMS":
            self._curr_person.add_spouse_of_family(data["args"])
            self._current_level_1 = "FAMS"

        if data["tag"] == "DEAT":
            self._current_level_1 = "DEAT"

        if data["tag"] == "NAME":
            self._curr_person.set_name(data["args"])
            self._current_level_1 = "NAME"

        if data["tag"] == "DATE":
            if self._current_level_1 == "BIRT":
                self._curr_person.set_date(data["args"], "birth")

            if self._current_level_1 == "DEAT":
                self._curr_person.set_date(data["args"], "death")

    def print_all(self):
        """print all individuals information
        """
        people_keys = sorted(self.individuals.keys())

        p_table = PrettyTable(["ID", "Name", "Gender", "Birthday",
                               "Age", "Alive", "Death", "Child", "Spouse"])
        for idx in people_keys:
            person = self.individuals[idx]
            death_date = "NA"
            if person.get_death_date() is not None:
                death_date = person.get_death_date().date().isoformat()
            birth_date = "NA"
            if person.get_birth_date() is not None:
                birth_date = person.get_birth_date().date().isoformat()

            p_table.add_row([
                person.get_person_id(),
                person.get_name(),
                person.get_gender(),
                birth_date,
                person.get_age(),
                person.get_is_alive(),
                death_date,
                person.get_children_of_families(),
                person.get_spouse_of_families()])
        print(p_table)

    def _is_valid_birth_date(self, person):
        """ checks if birthday occurs after death
        Args:
            person: Person
        """
        if person.get_birth_date() is not None and person.get_death_date() is not None:
            if person.get_death_date() < person.get_birth_date():
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US03",
                                       person.get_person_id(),
                                       person.get_name(),
                                       "Birth date should occur before death of an individual")

    def _is_valid_age(self, person):
        """ checks if age is less than 150
        Args:
            person: Person
        """
        if person.get_age() is not None:
            if person.get_age() > 149:
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US07",
                                       person.get_person_id(),
                                       person.get_name(),
                                       "Age should be less than 150")

    def _is_valid_death_current_dates(self, person):
        """ checks if birthday and death dates occurs before current date
        """
        if person.get_death_date() is not None:
            if person.get_death_date() > self._current_time:
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US01",
                                       person.get_person_id(),
                                       person.get_name(),
                                       "Death date should occur before current date")

    def _is_valid_birth_current_dates(self, person):
        """ checks if birthday occurs after death
        """
        if person.get_birth_date() is not None:
            if person.get_birth_date() > self._current_time:
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US01",
                                       person.get_person_id(),
                                       person.get_name(),
                                       "Birth date should occur before current date")

    def _is_valid_sibling(self, person):
        """ checks if siblings are married to each other
        """
        if len(set(person.get_children_of_families())) and len(set(person.get_spouse_of_families())):
            spouses = set(person.get_spouse_of_families())
            children = set(person.get_children_of_families())

            if spouses.intersection(children):
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US18",
                                       person.get_person_id(),
                                       person.get_name(),
                                       "Siblings should not marry")
                return False

        return True

    def validate(self):
        """run through all validation rules around people
        """
        # ensure the order of results doesn't change between runs
        ind_keys = sorted(self.individuals.keys())
        for idx in ind_keys:
            person = self.individuals[idx]
            self._is_valid_birth_date(person)
            self._is_valid_age(person)
            self._is_valid_birth_current_dates(person)
            self._is_valid_death_current_dates(person)
            self._is_valid_sibling(person)
