"""Families GEDCOM
Parses family tags from the gedcom data passed to it line by line as they appear in the gedcom files
"""
from datetime import datetime
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
            if self._current_level_1 == "MARR" and self._is_valid_married_date(date_obj):
                self._curr_family["married_date"] = date_obj
            if self._current_level_1 == "DIV":
                self._curr_family["divorced_date"] = date_obj

    def _is_valid_married_date(self, married_date: datetime):
        """ get husband and wife and check birth dates
        """
        if married_date < self._people.individuals[self._curr_family['husband_id']]['birth_date']:
            self._msgs.add_message(People.CLASS_IDENTIFIER,
                                   "US02",
                                   self._people.individuals[self._curr_family['husband_id']]['id'],
                                   self._people.individuals[self._curr_family['husband_id']]['name'],
                                   "Birth date should occur before marriage of an individual")
            return False
        elif married_date < self._people.individuals[self._curr_family['wife_id']]['birth_date']:
            self._msgs.add_message(People.CLASS_IDENTIFIER,
                                   "US02",
                                   self._people.individuals[self._curr_family['wife_id']]['id'],
                                   self._people.individuals[self._curr_family['wife_id']]['name'],
                                   "Birth date should occur before marriage of an individual")
            return False
        else:
            return True

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
