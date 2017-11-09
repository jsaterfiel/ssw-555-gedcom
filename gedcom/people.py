"""People GEDCOM
Parses person tags from the gedcom data passed to it line by line as they appear in the gedcom files
"""
from datetime import datetime
from datetime import timedelta
from person import Person
from prettytable import PrettyTable
from family import Family


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
        self._families = None

    def set_families(self, families):
        """sets the Families class that should be used
        """
        self._families = families

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
            # US22
            if data["args"] in self.individuals:
                self._msgs.add_message(self.CLASS_IDENTIFIER, "US22", data["args"],
                                       "NA", "Not unique individual ID " + data["args"] + " ")
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

    def us29_print_deceased(self):
        """"US29
        Prints all deceased individuals
        """
        people = self.individuals
        table = PrettyTable(["ID", "Name", "Alive"])

        for person_id in people:
            # type: Person
            individual = self.individuals[person_id]
            if not individual.get_is_alive():
                table.add_row([individual.get_person_id(), individual.get_name(), individual.get_is_alive()])

        print("Deceased Individuals")
        print(table)

    def print_upcoming_birthdays(self):
        """"US38
        Prints birthdays within the next 30 days
        """
        people = self.individuals
        table = PrettyTable(["ID", "Name", "Birthday"])

        for person_id in people:
            # type: Person
            individual = self.individuals[person_id]
            today = datetime.today()
            individual_birthday = individual.get_birth_date()
            if individual_birthday is not None and individual.get_is_alive():
                individual_current_birthday = datetime(today.year, individual_birthday.month, individual_birthday.day)
                if 0 <= (individual_current_birthday - today).days <= 30:
                    table.add_row([individual.get_person_id(), individual.get_name(), individual_birthday])

        print("Upcoming Birthdays")
        print(table)

    def us31_print_single(self):
        """" US31 list single
        Prints all living individuals who are over 30
        and never been married
        """
        people = self.individuals
        table = PrettyTable(["ID", "Name", "Alive", "Age", "Spouses"])

        for person_id in people:
            # type: Person
            individual = self.individuals[person_id]
            if individual.get_age() is not None:
                if individual.get_is_alive() and individual.get_age() > 30 and not individual.get_spouse_of_families():
                    table.add_row([individual.get_person_id(), individual.get_name(), individual.get_is_alive(),
                                   individual.get_age(), individual.get_spouse_of_families()])

        print("Single Individuals")
        print(table)

    def us35_print_recent_births(self):
        """" US35 Print births in the last 30 days in pretty table
        """
        people = self.individuals
        table = PrettyTable(["ID", "Name", "Birthdate"])

        for person_id in people:
            person = self.individuals[person_id]
            recent_date = self._current_time - timedelta(days=30)
            if person.get_birth_date() is None:
                pass
            if person.get_birth_date() is not None:
                if recent_date < person.get_birth_date() and person.get_birth_date() < self._current_time:
                    table.add_row([person.get_person_id(), person.get_name(), person.get_birth_date()])

        print("Recent Births")
        print(table)

    def us36_print_recent_deaths(self):
        """" US36 Print deaths in the last 30 days in pretty table
        """
        people = self.individuals
        table = PrettyTable(["ID", "Name", "Deathdate"])

        for person_id in people:
            person = self.individuals[person_id]
            recent_date = self._current_time - timedelta(days=30)

            if person.get_death_date() is None:
                pass
            if person.get_death_date() is not None:
                if recent_date < person.get_death_date() and person.get_death_date() < self._current_time:
                    table.add_row([person.get_person_id(), person.get_name(), person.get_death_date()])

        print("Recent Deaths")
        print(table)

    def _us03_is_valid_birth_date(self, person):
        """US03 checks if birthday occurs after death
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

    def _us07_is_valid_age(self, person):
        """US07 checks if age is less than 150
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

    def _us01_is_valid_death_current_dates(self, person):
        """US01 checks if birthday and death dates occurs before current date
        """
        if person.get_death_date() is not None:
            if person.get_death_date() > self._current_time:
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US01",
                                       person.get_person_id(),
                                       person.get_name(),
                                       "Death date should occur before current date")

    def _us01_is_valid_birth_current_dates(self, person):
        """US01 checks if birthday occurs after death
        """
        if person.get_birth_date() is not None:
            if person.get_birth_date() > self._current_time:
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US01",
                                       person.get_person_id(),
                                       person.get_name(),
                                       "Birth date should occur before current date")

    def _us18_is_valid_sibling(self, person):
        """US18 checks if siblings are married to each other
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
            self._us03_is_valid_birth_date(person)
            self._us07_is_valid_age(person)
            self._us01_is_valid_birth_current_dates(person)
            self._us01_is_valid_death_current_dates(person)
            self._us18_is_valid_sibling(person)
            self._us26_validate_corresponding_entries(person)

    def _us26_validate_corresponding_entries(self, person):
        """US26: check that the person's family links exist in the family record
        """
        us_num = "US26"
        peep_id = person.get_person_id()
        name = person.get_name()
        for fam_id in person.get_spouse_of_families():
            fam = None
            if fam_id in self._families.families:
                fam = self._families.families[fam_id]
            if fam is None or fam.get_husband_id() != peep_id and fam.get_wife_id() != peep_id:
                self._msgs.add_message(self.CLASS_IDENTIFIER, us_num, peep_id,
                                       name, "corresponding spouse link missing in family " + fam_id)

        for fam_id in person.get_children_of_families():
            fam = None
            if fam_id in self._families.families:
                fam = self._families.families[fam_id]
            if fam is None or peep_id not in fam.get_children():
                self._msgs.add_message(self.CLASS_IDENTIFIER, us_num, peep_id,
                                       name, "corresponding child link missing in family " + fam_id)
