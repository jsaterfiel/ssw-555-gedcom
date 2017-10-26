"""Families GEDCOM
Parses family tags from the gedcom data passed to it line by line as they appear in the gedcom files
"""
import re
from datetime import datetime
from datetime import timedelta
from time import strftime
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
    DAYS_IN_YEAR = 365.2425

    def __init__(self, people, validation_messages):
        self.families = {}
        self._curr_family = None
        self._current_level_1 = None
        self._people = people
        self._msgs = validation_messages
        self._current_time = datetime.now()
        # parses names in the format Bob /Hope/ where the last name has slashes around it
        self._last_name_regex = re.compile(r'\/(.*)\/')
        self._first_name_regex = re.compile(r'(.*) \/')

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
            children_order = "NA"
            if family.get_children() is not None:
                children = family.get_children()
                child_age = []
            for child_id in children:
                child = self._people.individuals[child_id]
                if child.get_age is None:
                    child_age = 1
                child_age.append(child.get_age())
            keys = children
            values = child_age
            childid_age = dict(zip(keys, values))
            order_childid_age = sorted(
                childid_age.items(), key=lambda t: t[1], reverse=True)
            order_childid_id = [idx for idx, val in order_childid_age]
            children_order = order_childid_id

            p_table.add_row([
                family.get_family_id(),
                married_date,
                divorced_date,
                husband_id,
                husband_name,
                wife_id,
                wife_name,
                children_order])
        print(p_table)

    def validate(self):
        """run through all the validation rules around families
        """
        # ensure the order of the results doesn't change between runs
        fam_keys = sorted(self.families.keys())
        fam_hashs = {}
        for idx in fam_keys:
            family = self.families[idx]
            self._validate_dates(family)
            self._validate_marr_div_dates(family)
            self._validate_death_of_parents_before_child_birth(family)
            self._validate_males_in_family_same_last_name(family)
            self._validate_children_names_and_birthdays_are_different(family)
            self._validate_fewer_than_15_siblings(family)
            self._validate_no_bigamy(family)
            self._validate_corresponding_entries(family)
            self._validate_no_marriage_to_decendants(family)
            self._validate_less_than_5_multi_births(family)
            self._validate_parents_not_too_old(family)
            self._validate_correct_gender_roles(family)
            self._hash_family(family, fam_hashs)

        self._validate_duplicate_families(fam_hashs)

    def _validate_duplicate_families(self, fam_hashs):
        """US24: Go through the hashes of the families and find the ones
        with more than one in the hash
        US24 No more than one family with the same spouses by name
        and the same marriage date should appear in a GEDCOM file.
        """
        fam_keys = sorted(fam_hashs.keys())
        for idx in fam_keys:
            key = fam_hashs[idx]
            dups = key["duplicate_families"]
            if dups:
                 self._msgs.add_message(self.CLASS_IDENTIFIER,
                                        "US24",
                                        key["first_family_id"],
                                        "NA",
                                        "Duplicate families by spouse names and married date: " + ", ".join(dups))

    def _hash_family(self, family, fam_hashs):
        """ hash family values to allow for detecting redundant family setups
        Used for US24 validation.  Must have both spouses and a married date set to get a hash else we have incomplete data to detect a redundant family
        """
        if family.get_husband_id() is None or family.get_wife_id() is None or family.get_married_date() is None:
            return
        fam_hash = self._people.individuals[family.get_husband_id()].get_name() + "|" + self._people.individuals[family.get_wife_id()].get_name() + "|" +family.get_married_date().isoformat()
        if  fam_hash in fam_hashs:
            fam_hashs[fam_hash]["duplicate_families"].append(family.get_family_id())
        else:
            fam_hashs[fam_hash] = {
                "first_family_id": family.get_family_id(),
                "duplicate_families": []
            }

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
                    hus_mar_age = int(
                        (mar_date - hus_bd).days / self.DAYS_IN_YEAR)
                    if hus_mar_age < 14:
                        self._msgs.add_message("FAMILY",
                                               "US10",
                                               fam_id,
                                               "NA",
                                               "marriage before age 14 for " + hus_id + " " + hus_name)
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
                    wif_mar_age = int(
                        (mar_date - wife_bd).days / self.DAYS_IN_YEAR)
                    if wif_mar_age < 14:
                        self._msgs.add_message("FAMILY",
                                               "US10",
                                               fam_id,
                                               "NA",
                                               "marriage before age 14 for " + wife_id + " " + wife_name)
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
                    for _ in range(0, 9):
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

    def _person_check_bigamy(self, person_id, marriage_start, marriage_end):
        """ check bigamy for person
        """
        spouses_h = self._people.individuals[person_id].get_spouse_of_families(
        )
        if spouses_h is not None and len(spouses_h) > 1:
            for item in spouses_h:
                ft = self.families[item]
                ft_hus = ft.get_husband_id()
                ft_wif = ft.get_wife_id()
                ft_som = ft.get_married_date()
                if ft_som is None:
                    return True
                if (marriage_start is None or ft_som > marriage_start) and ft_som < marriage_end:
                    return True
                ft_eom = ft.get_divorced_date()
                if ft_eom is None:
                    ft_eom = self._people.individuals[ft_hus].get_death_date()
                    ft_w_d = self._people.individuals[ft_wif].get_death_date()
                    if ft_w_d is not None:
                        if ft_eom is None or ft_w_d < ft_eom:
                            ft_eom = ft_w_d
                if ft_eom is None:
                    ft_eom = self._current_time
                if ft_eom > marriage_start and ft_eom < marriage_end:
                    return True
        return False

    def _validate_no_bigamy(self, family):
        """US11 No bigamy
        """
        key = "US11"
        msg = "Bigamy for "

        hus = family.get_husband_id()
        wif = family.get_wife_id()

        if hus is None or wif is None:
            return

        som = family.get_married_date()
        eom = family.get_divorced_date()
        if eom is None:
            eom = self._people.individuals[hus].get_death_date()
            w_d = self._people.individuals[wif].get_death_date()
            if w_d is not None:
                if eom is None or w_d < eom:
                    eom = w_d
        if eom is None:
            eom = self._current_time

        hus_result = self._person_check_bigamy(hus, som, eom)

        wif_result = self._person_check_bigamy(wif, som, eom)

        if hus_result is True:
            self._msgs.add_message(
                self.CLASS_IDENTIFIER,
                key,
                family.get_family_id(),
                "NA",
                msg + self._people.individuals[family.get_husband_id()].get_person_id() + " " + self._people.individuals[family.get_husband_id()].get_name())

        if wif_result is True:
            self._msgs.add_message(
                self.CLASS_IDENTIFIER,
                key,
                family.get_family_id(),
                "NA",
                msg + self._people.individuals[family.get_wife_id()].get_person_id() + " " + self._people.individuals[family.get_wife_id()].get_name())

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

    def _validate_children_names_and_birthdays_are_different(self, family):
        """US25 Child in a family must have unique first name and birthday
        otherwise it will be considered a misentry of the same child
        """
        children = family.get_children()
        if children is None:
            return

        children_first_names = dict()
        people_ids = []
        people_ids.extend(children)

        for person_id in people_ids:
            peep = self._people.individuals[person_id]

            name = self._first_name_regex.search(peep.get_name())
            if peep.get_birth_date() is None:
                return
            if name is not None and peep.get_birth_date() is not None:
                children_first_names[name.group(
                    0), peep.get_birth_date()] = True

        if len(children_first_names) < len(people_ids):
            self._msgs.add_message(self.CLASS_IDENTIFIER,
                                   "US25",
                                   family.get_family_id(),
                                   "NA",
                                   "Children in a family must have unique first name and birthday")

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
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US15",
                                       family.get_family_id(),
                                       "NA",
                                       "There should be fewer than 15 siblings in a family")

    def _validate_corresponding_entries(self, family):
        """US26 Corresponding entries(families)
        See US26 in people class for rest of US26 functionality
        """
        us_name = "US26"
        fam_id = family.get_family_id()
        husband_id = family.get_husband_id()
        wife_id = family.get_wife_id()
        child_ids = family.get_children()
        if husband_id is not None:
            husband = self._people.individuals[husband_id]
            if fam_id not in husband.get_spouse_of_families():
                self._msgs.add_message(self.CLASS_IDENTIFIER, us_name, fam_id, "NA",
                                       "corresponding spouse link missing for " + husband_id + " " + husband.get_name())
        if wife_id is not None:
            wife = self._people.individuals[wife_id]
            if fam_id not in wife.get_spouse_of_families():
                self._msgs.add_message(self.CLASS_IDENTIFIER, us_name, fam_id, "NA",
                                       "corresponding spouse link missing for " + wife_id + " " + wife.get_name())
        if child_ids is not None:
            for child_id in child_ids:
                child = self._people.individuals[child_id]
                if fam_id not in child.get_children_of_families():
                    self._msgs.add_message(self.CLASS_IDENTIFIER, us_name, fam_id, "NA",
                                           "corresponding child link missing for " + child_id + " " + child.get_name())

    def _validate_less_than_5_multi_births(self, family):
        """US14 No more than 5 siblings born in a multiple birth in a family"""
        children = family.get_children()
        childbdays = {}

        for child_id in children:
            child = self._people.individuals[child_id]

            if child.get_birth_date() is None:
                continue

            value = childbdays.get(
                child.get_birth_date().date().isoformat(), None)
            if value is not None:
                childbdays[child.get_birth_date().date().isoformat()
                           ] = value + 1
            else:
                childbdays[child.get_birth_date().date().isoformat()] = 1
            for _, value in childbdays.items():
                if value > 5:
                    self._msgs.add_message(self.CLASS_IDENTIFIER,
                                           "US14",
                                           family.get_family_id(),
                                           "NA",
                                           "No more than five siblings should be born at the same time")
                    break

    def _validate_parents_not_too_old(self, family):
        """Validate that husband and wife are not too much older than children
        Returns:
            bool
        """

        children = set(family.get_children())

        if children:
            for child in children:
                # type: Person
                child = self._people.individuals[child]
                if family.get_husband_id() is not None:
                    # type: Person
                    husband = self._people.individuals[family.get_husband_id()]
                    if husband.get_is_alive() and (husband.get_age() - child.get_age() >= 80):
                        self._msgs.add_message(self.CLASS_IDENTIFIER,
                                               "US12",
                                               family.get_family_id(),
                                               "NA",
                                               "Father %s should be less than 80 years older than his child %s" %
                                               (family.get_husband_id(), child.get_person_id()))
                        return False
                if family.get_wife_id() is not None:
                    # type: Person
                    wife = self._people.individuals[family.get_wife_id()]

                    if wife.get_is_alive() and (wife.get_age() - child.get_age() >= 60):
                        self._msgs.add_message(self.CLASS_IDENTIFIER,
                                               "US12",
                                               family.get_family_id(),
                                               "NA",
                                               "Mother %s should be less than 60 years older than her child %s" %
                                               (family.get_wife_id(), child.get_person_id()))
                        return False

        return True

    def _validate_correct_gender_roles(self, family):
        "Validate that the husband and wife roles in family are assigned the correct gender"
        husband_ids = []
        wife_ids = []
        if family.get_husband_id() is not None:
            husband_ids.append(family.get_husband_id())
        for person_id in husband_ids:
            hus_spouse = self._people.individuals[person_id]

            if hus_spouse.get_gender() != "M":
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US21",
                                       family.get_family_id(),
                                       "NA",
                                       "Father %s should be a Male" %
                                       (family.get_husband_id()))
        if family.get_wife_id() is not None:
            wife_ids.append(family.get_wife_id())
        for person_id in wife_ids:
            wif_spouse = self._people.individuals[person_id]

            if wif_spouse.get_gender() != "F":
                self._msgs.add_message(self.CLASS_IDENTIFIER,
                                       "US21",
                                       family.get_family_id(),
                                       "NA",
                                       "Mother %s should be a Female" %
                                       (family.get_wife_id()))
                return False
            return True
