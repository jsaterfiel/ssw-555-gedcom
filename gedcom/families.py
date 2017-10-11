"""Families GEDCOM
Parses family tags from the gedcom data passed to it line by line as they appear in the gedcom files
"""
import re
from datetime import datetime
from datetime import timedelta
from prettytable import PrettyTable
from people import People
from family import Family


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
        # parses names in the format Bob /Hope/ where the last name has slashes around it
        self._last_name_regex = re.compile(r'\/(.*)\/')

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
                self._curr_family.set_date(data["args"], "married")
            if self._current_level_1 == "DIV":
                self._curr_family.set_date(data["args"], "divorced")

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
            self._validate_dates(family)
            self._validate_marr_div_dates(family)
            self._validate_death_of_parents_before_child_birth(family)
            self._validate_males_in_family_same_last_name(family)
            self._validate_fewer_than_15_siblings(family)
            self._validate_no_marriage_to_decendants(family)

    def _validate_dates(self, family):
        """ validating dates
        """
        if family.get_family_id() is not None and family.get_married_date() is not None:
            fam_id = family.get_family_id()
            mar_date = family.get_married_date()
            if family.get_divorced_date() is not None:
                div_date = family.get_divorced_date()
                if mar_date > div_date:
                    self._msgs.add_message("FAMILY",
                                           "US04",
                                           fam_id,
                                           "NA",
                                           "Marriage date should occur before divorce date of a family")
            # Husband Dates
            if family.get_husband_id() is not None and family.get_wife_id() is not None:
                hus_id = family.get_husband_id()
                wife_id = family.get_wife_id()
                if self._people.individuals[family.get_husband_id()].get_birth_date() is not None and self._people.individuals[family.get_husband_id()].get_name() is not None:
                    hus_bd = self._people.individuals[family.get_husband_id(
                    )].get_birth_date()
                    hus_name = self._people.individuals[family.get_husband_id(
                    )].get_name()
                    if mar_date < hus_bd:
                        self._msgs.add_message(People.CLASS_IDENTIFIER,
                                               "US02",
                                               hus_id,
                                               hus_name,
                                               "Birth date should occur before marriage of an individual")
                    if self._people.individuals[family.get_husband_id()].get_death_date() is not None:
                        hus_dd = self._people.individuals[family.get_husband_id(
                        )].get_death_date()
                        if mar_date > hus_dd:
                            self._msgs.add_message("FAMILY",
                                                   "US05",
                                                   fam_id,
                                                   "NA",
                                                   "marriage after death for " + hus_id + " " + hus_name)
                        if family.get_divorced_date() is not None:
                            div_date = family.get_divorced_date()
                            if div_date > hus_dd:
                                self._msgs.add_message("FAMILY",
                                                       "US06",
                                                       fam_id,
                                                       "NA",
                                                       "divorce after death for " + hus_id + " " + hus_name)
        # Wife Dates
                if self._people.individuals[family.get_wife_id()].get_birth_date() is not None and self._people.individuals[family.get_wife_id()].get_name() is not None:
                    wife_bd = self._people.individuals[family.get_wife_id(
                    )].get_birth_date()
                    wife_name = self._people.individuals[family.get_wife_id(
                    )].get_name()
                    if mar_date < wife_bd:
                        self._msgs.add_message(People.CLASS_IDENTIFIER,
                                               "US02",
                                               wife_id,
                                               wife_name,
                                               "Birth date should occur before marriage of an individual")
                    if self._people.individuals[family.get_wife_id()].get_death_date() is not None:
                        wife_dd = self._people.individuals[family.get_wife_id(
                        )].get_death_date()
                        if mar_date > wife_dd:
                            self._msgs.add_message("FAMILY",
                                                   "US05",
                                                   fam_id,
                                                   "NA",
                                                   "marriage after death for " + wife_id + " " + wife_name)
                        if family.get_divorced_date() is not None:
                            div_date = family.get_divorced_date()
                            if div_date > wife_dd:
                                self._msgs.add_message("FAMILY",
                                                       "US06",
                                                       fam_id,
                                                       "NA",
                                                       "divorce after death for " + wife_id + " " + wife_name)

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
                        self.CLASS_IDENTIFIER,
                        key,
                        family.get_family_id(),
                        "NA",
                        msg + wife.get_person_id() + " " + wife.get_name())

    def _validate_no_marriage_to_decendants(self, family):
        """US17 No marriage to decendants
        """
        if family.get_children() is None:
            return

        if family.get_husband_id() is not None:
            self._check_family_for_decendant_marriage(
                family, family.get_husband_id(), True)

        if family.get_wife_id() is not None:
            self._check_family_for_decendant_marriage(
                family, family.get_wife_id(), True)

    def _check_family_for_decendant_marriage(self, family, person_id, ignore_current_family):
        """recursive function to go through families to see if a particular person_id was reused
        Is a part of US17
        """
        if ignore_current_family is False:
            if family.get_wife_id() == person_id or family.get_husband_id() == person_id:
                person = self._people.individuals[person_id]
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US17",
                                       family.get_family_id(),
                                       "NA",
                                       "No marriage to decendants. " + person_id + " " + person.get_name())

        children = family.get_children()
        if children is None:
            return

        for child_id in family.get_children():
            child = self._people.individuals[child_id]
            fams = child.get_spouse_of_families()
            if fams is None:
                return
            for fam_id in fams:
                fam = self.families[fam_id]
                self._check_family_for_decendant_marriage(
                    fam, person_id, False)

    def _validate_males_in_family_same_last_name(self, family):
        """US16 All males in a family have the same last name
        """
        children = family.get_children()
        if children is None:
            return

        male_last_names = dict()
        people_ids = []
        people_ids.extend(children)

        if family.get_husband_id() is not None:
            people_ids.append(family.get_husband_id())

        for person_id in people_ids:
            peep = self._people.individuals[person_id]

            if peep.get_gender() != "M":
                continue

            result = self._last_name_regex.search(peep.get_name())
            if result is not None:
                male_last_names[result.group(1)] = True

        if len(male_last_names) > 1:
            self._msgs.add_message(self.CLASS_IDENTIFIER,
                                   "US16",
                                   family.get_family_id(),
                                   "NA",
                                   "All males in a family must have the same last name")

    def _validate_fewer_than_15_siblings(self, family):
        """US15 There should be fewer than 15 siblings in a family
        """
        children = family.get_children()
        if children is not None:
            if len(children) >= 15:
                self._msgs.add_message("FAMILY",
                                       "US15",
                                       family.get_family_id(),
                                       "NA",
                                       "There should be fewer than 15 siblings in a family")
