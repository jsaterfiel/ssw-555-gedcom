"""Test cases for person module
"""
import unittest
from datetime import datetime
from person import Person


class TestPerson(unittest.TestCase):
    """test cases for person class
    Attributes:
        person (Person): Person test object
    """

    def test_default_values(self):
        """test setting all the values and making sure they come back out (except dates and lists)
        """
        person_id = "@I01@"
        name = "Mickey /Mouse/"
        gender = "M"
        peep = Person(person_id)
        peep.set_name(name)
        peep.set_gender(gender)

        self.assertEqual(person_id, peep.get_person_id())
        self.assertEqual(name, peep.get_name())
        self.assertEqual(gender, peep.get_gender())

    def test_birth_date(self):
        """test birth date
        """
        peep = Person("@I01@")
        birth_date = datetime.strptime(
            "7 SEP 1988", '%d %b %Y')
        peep.set_date("7 SEP 1988", "birth")

        self.assertEqual(birth_date, peep.get_birth_date())

    def test_death_date(self):
        """test death date
        """
        peep = Person("@I01@")
        death_date = datetime.strptime(
            "7 SEP 1988", '%d %b %Y')
        peep.set_date("7 SEP 1988", "death")

        self.assertEqual(death_date, peep.get_death_date())

    def test_age_no_death(self):
        """test age without death but with birth date
        """
        peep = Person("@I01@")
        birth_date = datetime.strptime(
            "7 SEP 1988", '%d %b %Y')
        peep.set_date("7 SEP 1988", "birth")

        expected_age = int(
            (peep.CURRENT_TIME - birth_date).days / peep.DAYS_IN_YEAR)

        self.assertEqual(expected_age, peep.get_age())

    def test_age_with_death(self):
        """test age with death
        """
        peep = Person("@I01@")
        peep.set_date("7 AUG 1988", "birth")
        peep.set_date("7 SEP 1990", "death")

        self.assertEqual(2, peep.get_age())

    def test_is_alive(self):
        """test is alive without death then with death then with birth and death
        """
        peep = Person("@I01@")

        self.assertTrue(peep.get_is_alive())

        peep.set_date("7 SEP 1988", "birth")

        self.assertTrue(peep.get_is_alive())

        peep.set_date("7 SEP 1988", "death")

        self.assertFalse(peep.get_is_alive())

    def test_child_of_families(self):
        """test adding child of families to person
        """
        peep = Person("@I21@")

        fam_1 = "@F01@"
        peep.add_children_of_family(fam_1)

        self.assertEqual(1, len(peep.get_children_of_families()))
        self.assertEqual(fam_1, peep.get_children_of_families()[0])

        fam_2 = "@F02@"
        peep.add_children_of_family(fam_2)
        self.assertEqual(2, len(peep.get_children_of_families()))
        self.assertEqual(fam_2, peep.get_children_of_families()[1])

    def test_spouse_of_families(self):
        """test adding spouse of families to person
        """
        peep = Person("@I21@")

        fam_1 = "@F02@"
        peep.add_spouse_of_family(fam_1)

        self.assertEqual(1, len(peep.get_spouse_of_families()))
        self.assertEqual(fam_1, peep.get_spouse_of_families()[0])

        fam_2 = "@F03@"
        peep.add_spouse_of_family(fam_2)
        self.assertEqual(2, len(peep.get_spouse_of_families()))
        self.assertEqual(fam_2, peep.get_spouse_of_families()[1])

    def test_get_age_at_date(self):
        """test getting a person's age at a specific date
        """
        peep = Person("@I01@")
        test_date = datetime.strptime("1 JAN 2000", '%d %b %Y')
        peep.set_date("1 JAN 1980", "birth")

        self.assertEqual(20, peep.get_age_at_date(test_date))
