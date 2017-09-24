"""People GEDCOM
Parses person tags from the gedcom data passed to it line by line as they appear in the gedcom files
"""
from datetime import datetime
from prettytable import PrettyTable
from validation_messages import ValidationMessages


class People(object):
    CLASS_IDENTIFIER = "INDIVIDUAL"

    """People class
    Contains logic for processing person (INDI) tags

    Attributes:
        individuals: list of individuals
    """

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
            self._curr_person = {
                "id": data["args"],
                "name": "",
                "gender": "",
                "is_alive": True,
                "birth_date": None,
                "death_date": None,
                "child_of_families": [],
                "spouse_of_families": [],
                "age": None
            }
            self.individuals.setdefault(data["args"], self._curr_person)

        if data["tag"] == "SEX":
            self._curr_person["gender"] = data["args"]
            self._current_level_1 = "SEX"

        if data["tag"] == "BIRT":
            self._current_level_1 = "BIRT"

        if data["tag"] == "DEAT":
            self._curr_person["is_alive"] = False
            self._current_level_1 = "DEAT"

        if data["tag"] == "FAMC":
            self._curr_person["child_of_families"].append(
                data["args"])
            self._current_level_1 = "FAMC"

        if data["tag"] == "FAMS":
            self._curr_person["spouse_of_families"].append(
                data["args"])
            self._current_level_1 = "FAMS"

        if data["tag"] == "DEAT":
            self._curr_person["is_alive"] = False
            self._current_level_1 = "DEAT"

        if data["tag"] == "NAME":
            self._curr_person["name"] = data["args"]
            self._current_level_1 = "NAME"

        if data["tag"] == "DATE":
            date_obj = datetime.strptime(data["args"], '%d %b %Y')
            if self._current_level_1 == "BIRT":
                self._curr_person["birth_date"] = date_obj
                if self._curr_person["death_date"] is not None:
                    self._curr_person["age"] = int(
                        (self._curr_person["death_date"] - date_obj).days / self._days_in_year)
                else:
                    self._curr_person["age"] = int(
                        (self._current_time - date_obj).days / self._days_in_year)

            if self._current_level_1 == "DEAT":
                self._curr_person["death_date"] = date_obj
                if self._curr_person["birth_date"] is not None and self._is_valid_birth_date():
                    self._curr_person["age"] = int(
                        (date_obj - self._curr_person["birth_date"]).days / self._days_in_year)

    def print_all(self):
        """print all individuals information
        """
        people_keys = sorted(self.individuals.keys())

        p_table = PrettyTable(["ID", "Name", "Gender", "Birthday",
                               "Age", "Alive", "Death", "Child", "Spouse"])
        for idx in people_keys:
            person = self.individuals[idx]
            death_date = "NA"
            if person["death_date"] is not None:
                death_date = person["death_date"].date().isoformat()
            birth_date = "NA"
            if person["birth_date"] is not None:
                birth_date = person["birth_date"].date().isoformat()

            p_table.add_row([
                person["id"],
                person["name"],
                person["gender"],
                birth_date,
                person["age"],
                person["is_alive"],
                death_date,
                person["child_of_families"],
                person["spouse_of_families"]])
        print(p_table)

    def _is_valid_birth_date(self):
        """ checks if birthday occurs after death
        """
        if self._curr_person["birth_date"] is not None and self._curr_person["death_date"]:
            if self._curr_person["death_date"] < self._curr_person["birth_date"]:
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US03",
                                       self._curr_person['id'],
                                       self._curr_person['name'],
                                       "Birth date should occur before death of an individual")
                return False
            else:
                return True

    def _is_valid_age(self, person):
        """ checks if age is less than 150
        """
        if person["age"] is not None:
            if person["age"] > 149:
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US07",
                                       person['id'],
                                       person['name'],
                                       "Age should be less than 150")
                return False
            else:
                return True

    def _is_valid_death_current_dates(self, person):
        """ checks if birthday and death dates occurs before current date
        """
        if person["death_date"] is not None:
            if person["death_date"] > self._current_time:
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US01",
                                       person['id'],
                                       person['name'],
                                       "Death date should occur before current date")
                return False
            else:
                return True

    def _is_valid_birth_current_dates(self, person):
        if person["birth_date"] is not None:
            if person["birth_date"] > self._current_time:
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US01",
                                       person['id'],
                                       person['name'],
                                       "Birth date should occur before current date")
                return False
            else:
                return True

    def validate(self):
        """run through all validation rules around people
        """
        # ensure the order of results doesn't change between runs
        ind_keys = sorted(self.individuals.keys())
        for idx in ind_keys:
            person = self.individuals[idx]
            self._is_valid_age(person)
            self._is_valid_death_current_dates(person)
