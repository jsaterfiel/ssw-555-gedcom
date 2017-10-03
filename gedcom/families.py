"""Families GEDCOM
Parses family tags from the gedcom data passed to it line by line as they appear in the gedcom files
"""
from datetime import datetime
from datetime import timedelta
from prettytable import PrettyTable
from people import People
from family import Family
from person import Person


class Families(object):
    """Families class
    Contains logic for processing family tags

    Attributes:
        families (:list:Family): dict of families
        _curr_family (Family): family of the current processing line
    Args:
        people (:list:People): people used for looking up individuals
    """

    CLASS_IDENTIFIER = "FAMILY"

    def __init__(self, people, validation_messages):
        self.families = {}
        self._curr_family = None
        self._current_level_1 = None
        self._people = people
        self._msgs = validation_messages
        self._current_time = datetime.now()

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

        if data["tag"] == "FAM":
            self._curr_family = Family(data["args"])
            self.families[data["args"]] = self._curr_family

        if data["tag"] == "MARR":
            self._current_level_1 = "MARR"

        if data["tag"] == "DIV":
            self._current_level_1 = "DIV"

        if data["tag"] == "HUSB":
            self._curr_family.set_husband_id(data["args"])
            self._current_level_1 = "HUSB"

        if data["tag"] == "WIFE":
            self._curr_family.set_wife_id(data["args"])
            self._current_level_1 = "WIFE"

        if data["tag"] == "CHIL":
            self._curr_family.add_child(data["args"])
            self._current_level_1 = "CHIL"

        if data["tag"] == "DATE":
            if self._current_level_1 == "MARR":
                self._curr_family.set_married_date(data["args"])
            if self._current_level_1 == "DIV":
                self._curr_family.set_divorced_date(data["args"])

    def print_all(self):
        """print all families information
        """
        fam_keys = sorted(self.families.keys())

        p_table = PrettyTable(["ID", "Married", "Divorced", "Husband ID",
                               "Husband Name", "Wife ID", "Wife Name", "Children"])
        for idx in fam_keys:
            family = self.families[idx]
            married_date = "NA"
            if family.get_married_date() is not None:
                married_date = family.get_married_date().date().isoformat()
            divorced_date = "NA"
            if family.get_divorced_date() is not None:
                divorced_date = family.get_divorced_date().date().isoformat()
            husband_id = "NA"
            husband_name = "NA"
            if family.get_husband_id() is not None:
                husband_id = family.get_husband_id()
                husband_name = self._people.individuals[husband_id].get_name()
            wife_id = "NA"
            wife_name = "NA"
            if family.get_wife_id() is not None:
                wife_id = family.get_wife_id()
                wife_name = self._people.individuals[wife_id].get_name()

            p_table.add_row([
                family.get_family_id(),
                married_date,
                divorced_date,
                husband_id,
                husband_name,
                wife_id,
                wife_name,
                family.get_children()])
        print(p_table)

    def validate(self):
        """run through all the validation rules around families
        """
        # ensure the order of the results doesn't change between runs
        fam_keys = sorted(self.families.keys())
        for idx in fam_keys:
            family = self.families[idx]
            self._validate_death_before_marriage(family)
            self._validate_death_before_divorce(family)
            self._validate_birth_before_marriage(family)
            self._validate_marr_before_div_dates(family)
            self._validate_marr_div_dates(family)
            self._validate_death_of_parents_before_child_birth(family)
            self._validate_parents_not_too_old(family)

    def _validate_birth_before_marriage(self, family):
        """get husband and wife and check birth dates
        Args:
            family (Family): family object
        Returns:
            boolean
        """
        if family.get_married_date() is not None:
            married_date = family.get_married_date()
            if family.get_husband_id() is not None and family.get_husband_id() in self._people.individuals and self._people.individuals[family.get_husband_id()].get_birth_date() is not None:
                if married_date < self._people.individuals[family.get_husband_id()].get_birth_date():
                    self._msgs.add_message(People.CLASS_IDENTIFIER,
                                           "US02",
                                           family.get_husband_id(),
                                           self._people.individuals[family.get_husband_id(
                                           )].get_name(),
                                           "Birth date should occur before marriage of an individual")
                    return False

            if family.get_wife_id() is not None and family.get_wife_id() in self._people.individuals and self._people.individuals[family.get_wife_id()].get_birth_date() is not None:
                if married_date < self._people.individuals[family.get_wife_id()].get_birth_date():
                    self._msgs.add_message(People.CLASS_IDENTIFIER,
                                           "US02",
                                           family.get_wife_id(),
                                           self._people.individuals[family.get_wife_id(
                                           )].get_name(),
                                           "Birth date should occur before marriage of an individual")
                    return False
        return True

    def _validate_death_before_marriage(self, family):
        """US05: validate that death occurred before marriage
        Args:
            family (Family): family object
        """
        key = "US05"
        msg = "marriage after death for "
        if family is None:
            return
        if family.get_married_date() is not None:
            if family.get_husband_id() is not None:
                # check the husband died after marriage
                husb = self._people.individuals[family.get_husband_id()]
                if husb.get_death_date() is not None and family.get_married_date() > husb.get_death_date():
                    # error husband died before marriage
                    self._msgs.add_message(
                        "FAMILY",
                        key,
                        family.get_family_id(),
                        "NA",
                        msg + husb.get_person_id() + " " + husb.get_name())
            if family.get_wife_id() is not None:
                # check the wife died after the marriage
                wife = self._people.individuals[family.get_wife_id()]
                if wife.get_death_date() is not None and family.get_married_date() > wife.get_death_date():
                    # error wife died before marriage
                    self._msgs.add_message(
                        "FAMILY",
                        key,
                        family.get_family_id(),
                        "NA",
                        msg + wife.get_person_id() + " " + wife.get_name())

    def _validate_death_before_divorce(self, family):
        """US06: validate that death occurred before marriage
        Args:
            family (Family): family object
        """
        key = "US06"
        msg = "divorce after death for "
        if family.get_divorced_date() is not None:
            if family.get_husband_id() is not None:
                # check the husband died after divorce
                husb = self._people.individuals[family.get_husband_id()]
                if husb.get_death_date() is not None and family.get_divorced_date() > husb.get_death_date():
                    # error husband died before divorce
                    self._msgs.add_message(
                        "FAMILY",
                        key,
                        family.get_family_id(),
                        "NA",
                        msg + husb.get_person_id() + " " + husb.get_name())
            if family.get_wife_id() is not None:
                # check the wife died after the divorce
                wife = self._people.individuals[family.get_wife_id()]
                if wife.get_death_date() is not None and family.get_divorced_date() > wife.get_death_date():
                    # error wife died before divorce
                    self._msgs.add_message(
                        "FAMILY",
                        key,
                        family.get_family_id(),
                        "NA",
                        msg + wife.get_person_id() + " " + wife.get_name())

    def _validate_death_of_parents_before_child_birth(self, family):
        """US09: validate death of parents before child birth
        """
        key = "US09"
        msg = "parent death before child birth for "
        children = family.get_children()

        for child_id in children:
            chil = self._people.individuals[child_id]
            if family.get_husband_id() is not None:
                # check the husband died after conception of child
                husb = self._people.individuals[family.get_husband_id()]
                if husb.get_death_date() is not None:
                    hub9_date = husb.get_death_date()
                    # Calculate 9 Months Back
                    for i in range(0, 9):
                        hub9_date = hub9_date.replace(day=1)
                        hub9_date = hub9_date - timedelta(days=1)
                        # Calculate Day
                    if hub9_date.day > husb.get_death_date().day:
                        hub9_date = hub9_date.replace(
                            day=husb.get_death_date().day)
                    if hub9_date < chil.get_birth_date():
                        # error husband died at least 9 months before child birth
                        self._msgs.add_message(
                            "FAMILY",
                            key,
                            family.get_family_id(),
                            "NA",
                            msg + husb.get_person_id() + " " + husb.get_name())
            if family.get_wife_id() is not None:
                # check the wife died before the child birth
                wife = self._people.individuals[family.get_wife_id()]
                if wife.get_death_date() is not None and chil.get_birth_date() > wife.get_death_date():
                    # error wife died before child birth
                    self._msgs.add_message(
                        "FAMILY",
                        key,
                        family.get_family_id(),
                        "NA",
                        msg + wife.get_person_id() + " " + wife.get_name())

    def _validate_marr_before_div_dates(self, family):
        """Validate that family marriage date occurs before divorce
        """
        if family.get_divorced_date() is not None:
            if family.get_married_date() is not None:
                if family.get_married_date() > family.get_divorced_date():
                    self._msgs.add_message("FAMILY",
                                           "US04",
                                           family.get_family_id(),
                                           "NA",
                                           "Marriage date should occur before divorce date of a family")
                    return False
        return True

    def _validate_marr_div_dates(self, family):
        """Validate that family marriage and divorce dates occurs before current date
        """
        if family.get_divorced_date() is not None:
            if family.get_divorced_date() > self._current_time:
                self._msgs.add_message("FAMILY",
                                       "US01",
                                       family.get_family_id(),
                                       "NA",
                                       "Divorced date should occur before current date for a family")
                return False

        if family.get_married_date() is not None:
            if family.get_married_date() > self._current_time:
                self._msgs.add_message("FAMILY",
                                       "US01",
                                       family.get_family_id(),
                                       "NA",
                                       "Married date should occur before current date for a family")
            return False
        return True

    def _validate_parents_not_too_old(self, family):
        children = family.get_children()

        if children:
            for child in children:
                child = self._people.individuals[child]  # type: Person
                husband = self._people.individuals[family.get_husband_id()]  # type: Person
                wife = self._people.individuals[family.get_wife_id()]  # type: Person
                if husband.get_age() - child.get_age() >= 80:
                    self._msgs.add_message(self.CLASS_IDENTIFIER,
                                           "US12",
                                           family.get_family_id(),
                                           "NA",
                                           "Father should be less than 80 years older than his children")
                    return False
                if wife.get_age() - child.get_age() >= 60:
                    self._msgs.add_message(self.CLASS_IDENTIFIER,
                                           "US12",
                                           family.get_family_id(),
                                           "NA",
                                           "Mother should be less than 60 years older than her children")
                    return False

        return True
