"""Families GEDCOM
Parses family tags from the gedcom data passed to it line by line as they appear in the gedcom files
"""
from datetime import datetime
from datetime import timedelta
from prettytable import PrettyTable
from people import People
from validation_messages import ValidationMessages


class Families(object):
    CLASS_IDENTIFIER = "FAMILY"

    """Families class
    Contains logic for processing family tags

    Attributes:
        families: dict of families

    Args:
        people (People): people used for looking up individuals
    """

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
            self._curr_family = {
                "id": data["args"],
                "children": [],
                "husband_id": None,
                "wife_id": None,
                "married_date": None,
                "divorced_date": None
            }
            self.families.setdefault(data["args"], self._curr_family)

        if data["tag"] == "MARR":
            self._curr_family["married"] = True
            self._curr_family["married_date"] = None
            self._current_level_1 = "MARR"

        if data["tag"] == "DIV":
            self._curr_family["divorced"] = True
            self._curr_family["divorced_date"] = None
            self._current_level_1 = "DIV"

        if data["tag"] == "HUSB":
            self._curr_family["husband_id"] = data["args"]
            self._current_level_1 = "HUSB"

        if data["tag"] == "WIFE":
            self._curr_family["wife_id"] = data["args"]
            self._current_level_1 = "WIFE"

        if data["tag"] == "CHIL":
            self._curr_family["children"].append(
                data["args"])
            self._current_level_1 = "CHIL"

        if data["tag"] == "DATE":
            date_obj = datetime.strptime(data["args"], '%d %b %Y')
            if self._current_level_1 == "MARR":
                self._curr_family["married_date"] = date_obj
            if self._current_level_1 == "DIV":
                self._curr_family["divorced_date"] = date_obj

    def print_all(self):
        """print all families information
        """
        fam_keys = sorted(self.families.keys())

        p_table = PrettyTable(["ID", "Married", "Divorced", "Husband ID",
                               "Husband Name", "Wife ID", "Wife Name", "Children"])
        for idx in fam_keys:
            family = self.families[idx]
            married_date = "NA"
            if family["married_date"] is not None:
                married_date = family["married_date"].date().isoformat()
            divorced_date = "NA"
            if family["divorced_date"] is not None:
                divorced_date = family["divorced_date"].date().isoformat()
            husband_id = "NA"
            husband_name = "NA"
            if family["husband_id"] is not None:
                husband_id = family["husband_id"]
                husband_name = self._people.individuals[husband_id]["name"]
            wife_id = "NA"
            wife_name = "NA"
            if family["wife_id"] is not None:
                wife_id = family["wife_id"]
                wife_name = self._people.individuals[wife_id]["name"]

            p_table.add_row([
                family["id"],
                married_date,
                divorced_date,
                husband_id,
                husband_name,
                wife_id,
                wife_name,
                family["children"]])
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
            self._validate_marrb4div_dates(family)
            self._validate_marr_div_dates(family)
            self._validate_death_of_parents_before_child_birth(family)

    def _validate_birth_before_marriage(self, family):
        """get husband and wife and check birth dates
        :param family family to validate
        :return boolean if valid
        """
        if family["married_date"] is not None:
            married_date = family["married_date"]
            if family['husband_id'] is not None and family['husband_id'] in self._people.individuals and self._people.individuals[family['husband_id']]['birth_date'] is not None:
                if married_date < self._people.individuals[family['husband_id']]['birth_date']:
                    self._msgs.add_message(People.CLASS_IDENTIFIER,
                                           "US02",
                                           self._people.individuals[family['husband_id']]['id'],
                                           self._people.individuals[family['husband_id']]['name'],
                                           "Birth date should occur before marriage of an individual")
                    return False

            if family['wife_id'] is not None and family['wife_id'] in self._people.individuals and self._people.individuals[family['wife_id']]['birth_date'] is not None:
                if married_date < self._people.individuals[family['wife_id']]['birth_date']:
                    self._msgs.add_message(People.CLASS_IDENTIFIER,
                                           "US02",
                                           self._people.individuals[family['wife_id']]['id'],
                                           self._people.individuals[family['wife_id']]['name'],
                                           "Birth date should occur before marriage of an individual")
                    return False
        return True

    def _validate_death_before_marriage(self, family):
        """US05: validate that death occurred before marriage
        """
        key = "US05"
        msg = "marriage after death for "

        if family["married_date"] is not None:
            if family["husband_id"] is not None:
                # check the husband died after marriage
                husb = self._people.individuals[family["husband_id"]]
                if husb["death_date"] is not None and family["married_date"] > husb["death_date"]:
                    # error husband died before marriage
                    self._msgs.add_message(
                        "FAMILY",
                        key,
                        family["id"],
                        "NA",
                        msg + husb["id"] + " " + husb["name"])
            if family["wife_id"] is not None:
                # check the wife died after the marriage
                wife = self._people.individuals[family["wife_id"]]
                if wife["death_date"] is not None and family["married_date"] > wife["death_date"]:
                    # error wife died before marriage
                    self._msgs.add_message(
                        "FAMILY",
                        key,
                        family["id"],
                        "NA",
                        msg + wife["id"] + " " + wife["name"])

    def _validate_death_before_divorce(self, family):
        """US06: validate that death occurred before marriage
        """
        key = "US06"
        msg = "divorce after death for "

        if family["divorced_date"] is not None:
            if family["husband_id"] is not None:
                # check the husband died after divorce
                husb = self._people.individuals[family["husband_id"]]
                if husb["death_date"] is not None and family["divorced_date"] > husb["death_date"]:
                    # error husband died before divorce
                    self._msgs.add_message(
                        "FAMILY",
                        key,
                        family["id"],
                        "NA",
                        msg + husb["id"] + " " + husb["name"])
            if family["wife_id"] is not None:
                # check the wife died after the divorce
                wife = self._people.individuals[family["wife_id"]]
                if wife["death_date"] is not None and family["divorced_date"] > wife["death_date"]:
                    # error wife died before divorce
                    self._msgs.add_message(
                        "FAMILY",
                        key,
                        family["id"],
                        "NA",
                        msg + wife["id"] + " " + wife["name"])

    def _validate_death_of_parents_before_child_birth(self, family):
        """US09: validate death of parents before child birth
        """
        key = "US09"
        msg = "parent death before child birth for "
        if family["children"] is not None:
            chil = self._people.individuals[family["child_id"]]
            if family["husband_id"] is not None:
                # check the husband died after conception of child
                husb = self._people.individuals[family["husband_id"]]
                if husb["death_date"] is not None:
                    hub9_date = husb["death_date"]
                    # Calculate 9 Months Back
                    for i in range(0, 9):
                        hub9_date = hub9_date.replace(day=1)
                        hub9_date = hub9_date - timedelta(days=1)
                        # Calculate Day
                    if hub9_date.day > husb["death_date"].day:
                        hub9_date = hub9_date.replace(
                            day=husb["death_date"].day)
                    if hub9_date > chil["birth_date"]:
                        # error husband died at least 9 months before child birth
                        self._msgs.add_message(
                            "FAMILY",
                            key,
                            family["id"],
                            "NA",
                            msg + husb["id"] + " " + husb["name"])
            if family["wife_id"] is not None:
                # check the wife died before the child birth
                wife = self._people.individuals[family["wife_id"]]
                if wife["death_date"] is not None and chil["birth_date"] > wife["death_date"]:
                    # error wife died before divorce
                    self._msgs.add_message(
                        "FAMILY",
                        key,
                        family["id"],
                        "NA",
                        msg + wife["id"] + " " + wife["name"])

    def _validate_marrb4div_dates(self, family):
        """Validate that family marriage date occurs before divorce
        """
        if family["divorced_date"] is not None:
            if family["married_date"] is not None:
                if family["married_date"] > family["divorced_date"]:
                    self._msgs.add_message("FAMILY",
                                           "US04",
                                           family["id"],
                                           "NA",
                                           "Marriage date should occur before divorce date of a family")
                    return False
        return True

    def _validate_marr_div_dates(self, family):
        """Validate that family marriage and divorce dates occurs before current date
        """
        if family["divorced_date"] is not None:
            if family["divorced_date"] > self._current_time:
                self._msgs.add_message("FAMILY",
                                       "US01",
                                       family["id"],
                                       "NA",
                                       "Divorced date should occur before current date for a family")
                return False

        if family["married_date"] is not None:
            if family["married_date"] > self._current_time:
                self._msgs.add_message("FAMILY",
                                       "US01",
                                       family["id"],
                                       "NA",
                                       "Married date should occur before current date for a family")
            return False
        return True
