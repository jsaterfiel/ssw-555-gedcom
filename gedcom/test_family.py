"""Test cases for family module
"""
import unittest
from datetime import datetime
from family import Family


class TestFamilies(unittest.TestCase):
    """test cases for Family class
    """

    def test_default_data(self):
        """default init data, wife and husband ids
        """
        fam_id = "@F01@"
        husband_id = "@I01@"
        wife_id = "@I02"

        fam = Family(fam_id)
        fam.set_husband_id(husband_id)
        fam.set_wife_id(wife_id)

        self.assertEqual(fam_id, fam.get_family_id())
        self.assertEqual(husband_id, fam.get_husband_id())
        self.assertEqual(wife_id, fam.get_wife_id())

    def test_married_date(self):
        """add married date 28 MAR 2001
        """
        married_date = datetime.strptime(
            "28 MAR 2001", '%d %b %Y')
        fam = Family("@F01@")
        fam.set_date("28 MAR 2001", "married")

        self.assertEqual(married_date, fam.get_married_date())

    def test_divorced_date(self):
        """add divorced date 1 APR 1970
        """
        divorced_date = datetime.strptime(
            "1 APR 1970", '%d %b %Y')
        fam = Family("@F09@")
        fam.set_date("1 APR 1970", "divorced")

        self.assertEqual(divorced_date, fam.get_divorced_date())

    def test_both_dates(self):
        """add both dates together
        """
        fam = Family("@F01@")

        married_date = datetime.strptime(
            "28 MAR 2001", '%d %b %Y')
        fam.set_date("28 MAR 2001", "married")

        divorced_date = datetime.strptime(
            "1 APR 1970", '%d %b %Y')
        fam.set_date("1 APR 1970", "divorced")

        self.assertEqual(married_date, fam.get_married_date())
        self.assertEqual(divorced_date, fam.get_divorced_date())

    def test_add_children(self):
        """test adding children
        """
        fam = Family("@F11@")
        child_id_1 = "@I08@"
        fam.add_child(child_id_1)

        self.assertEqual(1, len(fam.get_children()))
        self.assertEqual(child_id_1, fam.get_children()[0])

        child_id_2 = "@I09@"
        fam.add_child(child_id_2)

        self.assertEqual(2, len(fam.get_children()))
        self.assertEqual(child_id_2, fam.get_children()[1])
