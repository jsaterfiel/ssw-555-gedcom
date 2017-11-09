"""Test cases for families module
"""
import unittest
import io
import sys
from datetime import datetime
from families import Families
from people import People
from person import Person
from family import Family
from validation_messages import ValidationMessages


class TestFamilies(unittest.TestCase):
    """test cases for families class
    Attributes:
        fam (Families): Family test object
        peeps (People): People test object
        msgs (ValidationMessages): Validation messages test object
    """

    def setUp(self):
        """creates test objects
        """
        self.msgs = ValidationMessages()
        self.peeps = People(self.msgs)
        self.fam = Families(self.peeps, self.msgs)
        self.peeps.set_families(self.fam)

    def tearDown(self):
        """delete test objects
        """
        del self.fam
        del self.peeps
        del self.msgs

    def test_default_init(self):
        """make sure the object is empty on init
        """
        self.assertEqual(0, len(self.fam.families))

    def test_ignore_bad_tags(self):
        """ensure bad tags aren't being processed
        """
        # raw line:
        # 1 BLAH sdfsd
        data = {
            "level": 1,
            "tag": "BLAH",
            "args": "sdfsd",
            "valid": "N"
        }
        with self.assertRaises(ValueError):
            self.fam.process_line_data(data)
        # ensure nothing got added
        self.assertEqual(0, len(self.fam.families))

    def test_add_family(self):
        """test cases for detecting the family tag and adding it to the list of families
        """
        # raw line:
        # 0 @F6@ FAM
        data = {
            "level": 0,
            "tag": "FAM",
            "args": "@F6@",
            "valid": "Y"
        }
        self.fam.process_line_data(data)
        # add a family
        self.assertEqual(1, len(self.fam.families))
        # test family dict setup
        test_fam = Family(data["args"])
        result = self.fam.families[data["args"]]
        self.assertEqual(test_fam.get_family_id(), result.get_family_id())

    def test_correct_family_tag(self):
        """Ensuring the FAM tag can only be used to add a family
        """
        # raw line:
        # 0 @F6@ FAM
        data = {
            "level": 0,
            "tag": "INDI",
            "args": "@F6@",
            "valid": "Y"
        }
        self.fam.process_line_data(data)
        # add a family
        self.assertEqual(0, len(self.fam.families))

    def test_add_multiple_families(self):
        """adding mulitiple families to make sure they are both read in
        """
        # raw line:
        # 0 @F6@ FAM
        fam1 = {
            "level": 0,
            "tag": "FAM",
            "args": "@F6@",
            "valid": "Y"
        }
        self.fam.process_line_data(fam1)
        # raw line:
        # 0 @A6@ FAM
        fam2 = {
            "level": 0,
            "tag": "FAM",
            "args": "@A6@",
            "valid": "Y"
        }
        self.fam.process_line_data(fam2)
        # add a family
        self.assertEqual(2, len(self.fam.families))
        # test family exist
        test_fam1 = Family(fam1["args"])
        result1 = self.fam.families[fam1["args"]]

        self.assertEqual(test_fam1.get_family_id(), result1.get_family_id())

        test_fam2 = Family(fam2["args"])
        result2 = self.fam.families[fam2["args"]]
        self.assertEqual(test_fam2.get_family_id(), result2.get_family_id())

    def test_detect_married_date(self):
        """able to read the date for a married event
        """
        # raw line:
        # 0 @F6@ FAM
        data = {
            "level": 0,
            "tag": "FAM",
            "args": "@F6@",
            "valid": "Y"
        }
        self.fam.process_line_data(data)
        # raw lines:
        # 1 MARR
        # 2 DATE 15 JUN 1970
        mar_tag = {
            "level": 1,
            "tag": "MARR",
            "args": "",
            "valid": "Y"
        }
        self.fam.process_line_data(mar_tag)
        mar_date = {
            "level": 2,
            "tag": "DATE",
            "args": "6 MAY 1952",
            "valid": "Y"
        }
        self.fam.process_line_data(mar_date)
        date_obj = datetime.strptime(mar_date["args"], '%d %b %Y')
        self.assertEqual(
            date_obj, self.fam.families[data["args"]].get_married_date())

    def test_detect_divorced_date(self):
        """able to read the date for a divorced event
        """
        # raw line:
        # 0 @F6@ FAM
        data = {
            "level": 0,
            "tag": "FAM",
            "args": "@F6@",
            "valid": "Y"
        }
        self.fam.process_line_data(data)
        # raw lines:
        # 1 DIV
        # 2 DATE 15 JUN 1970
        div_tag = {
            "level": 1,
            "tag": "DIV",
            "args": "",
            "valid": "Y"
        }
        self.fam.process_line_data(div_tag)
        div_date = {
            "level": 2,
            "tag": "DATE",
            "args": "26 APR 1992",
            "valid": "Y"
        }
        self.fam.process_line_data(div_date)
        date_obj = datetime.strptime(div_date["args"], '%d %b %Y')
        self.assertEqual(
            date_obj, self.fam.families[data["args"]].get_divorced_date())

    def test_husband_id_tag(self):
        """testing the husb tag with id
        """
        # raw line:
        # 0 @A6@ FAM
        fam_data = {
            "level": 0,
            "tag": "FAM",
            "args": "@F1@",
            "valid": "Y"
        }
        self.fam.process_line_data(fam_data)
        husband_data = {
            "level": 1,
            "tag": "HUSB",
            "args": "@I10@",
            "valid": "Y"
        }
        self.fam.process_line_data(husband_data)
        self.assertEqual(
            husband_data["args"], self.fam.families[fam_data["args"]].get_husband_id())

    def test_wife_id_tag(self):
        """testing the wife tag with id
        """
        # raw line:
        # 0 @A6@ FAM
        fam_data = {
            "level": 0,
            "tag": "FAM",
            "args": "@F1@",
            "valid": "Y"
        }
        self.fam.process_line_data(fam_data)
        wife_data = {
            "level": 1,
            "tag": "WIFE",
            "args": "@I09@",
            "valid": "Y"
        }
        self.fam.process_line_data(wife_data)
        self.assertEqual(
            wife_data["args"], self.fam.families[fam_data["args"]].get_wife_id())

    def test_children_id_tag(self):
        """testing the child tag with id
        """
        # raw line:
        # 0 @A6@ FAM
        fam_data = {
            "level": 0,
            "tag": "FAM",
            "args": "@F01@",
            "valid": "Y"
        }
        self.fam.process_line_data(fam_data)
        child_data = {
            "level": 1,
            "tag": "CHIL",
            "args": "@I11@",
            "valid": "Y"
        }
        self.fam.process_line_data(child_data)
        self.assertEqual(
            1, len(self.fam.families[fam_data["args"]].get_children()))
        self.assertEqual(
            child_data["args"], self.fam.families[fam_data["args"]].get_children()[0])

    def test_multi_children_id_tags(self):
        """testing the child tag with id
        """
        # raw line:
        # 0 @A6@ FAM
        fam_data = {
            "level": 0,
            "tag": "FAM",
            "args": "@F01@",
            "valid": "Y"
        }
        self.fam.process_line_data(fam_data)
        child1_data = {
            "level": 1,
            "tag": "CHIL",
            "args": "@I11@",
            "valid": "Y"
        }
        self.fam.process_line_data(child1_data)
        child2_data = {
            "level": 1,
            "tag": "CHIL",
            "args": "@I12@",
            "valid": "Y"
        }
        self.fam.process_line_data(child2_data)
        self.assertEqual(
            2, len(self.fam.families[fam_data["args"]].get_children()))
        self.assertEqual(
            child1_data["args"], self.fam.families[fam_data["args"]].get_children()[0])
        self.assertEqual(
            child2_data["args"], self.fam.families[fam_data["args"]].get_children()[1])

    def test_print_all(self):
        """test print all families
        """
        # raw lines:
        # 0 @A6@ FAM
        # 1 DIV
        # 2 DATE 15 JUN 1970
        # 1 HUSB @A4@
        # 1 WIFE @A3@
        # 1 CHIL @I11@
        # 1 CHIL @I12@
        # 1 MARR
        # 2 DATE 15 JUN 1970
        fam_data = {
            "level": 0,
            "tag": "FAM",
            "args": "@F1@",
            "valid": "Y"
        }
        self.fam.process_line_data(fam_data)
        div_tag = {
            "level": 1,
            "tag": "DIV",
            "args": "",
            "valid": "Y"
        }
        self.fam.process_line_data(div_tag)
        div_date = {
            "level": 2,
            "tag": "DATE",
            "args": "26 APR 1992",
            "valid": "Y"
        }
        self.fam.process_line_data(div_date)
        husband_data = {
            "level": 1,
            "tag": "HUSB",
            "args": "@A4@",
            "valid": "Y"
        }
        self.fam.process_line_data(husband_data)
        wife_data = {
            "level": 1,
            "tag": "WIFE",
            "args": "@A3@",
            "valid": "Y"
        }
        self.fam.process_line_data(wife_data)
        child1_data = {
            "level": 1,
            "tag": "CHIL",
            "args": "@I11@",
            "valid": "Y"
        }
        self.fam.process_line_data(child1_data)
        child2_data = {
            "level": 1,
            "tag": "CHIL",
            "args": "@I12@",
            "valid": "Y"
        }
        self.fam.process_line_data(child2_data)
        mar_tag = {
            "level": 1,
            "tag": "MARR",
            "args": "",
            "valid": "Y"
        }
        self.fam.process_line_data(mar_tag)
        mar_date = {
            "level": 2,
            "tag": "DATE",
            "args": "6 MAY 1952",
            "valid": "Y"
        }
        self.fam.process_line_data(mar_date)
        # load up spouses data
        data1 = {
            "level": 0,
            "tag": "INDI",
            "args": "@A3@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data1)
        name_tag1 = {
            "level": 1,
            "tag": "NAME",
            "args": "Jane /Doe/",
            "valid": "Y"
        }
        self.peeps.process_line_data(name_tag1)
        data2 = {
            "level": 0,
            "tag": "INDI",
            "args": "@A4@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data2)
        name_tag2 = {
            "level": 1,
            "tag": "NAME",
            "args": "Jane /Doe/",
            "valid": "Y"
        }
        self.peeps.process_line_data(name_tag2)
        data3 = {
            "level": 0,
            "tag": "INDI",
            "args": "@I11@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data3)
        birth_tag1 = {
            "level": 1,
            "tag": "BIRT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_tag1)
        birth_date1 = {
            "level": 2,
            "tag": "DATE",
            "args": "1 MAY 2001",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_date1)
        data4 = {
            "level": 0,
            "tag": "INDI",
            "args": "@I12@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data4)
        birth_tag2 = {
            "level": 1,
            "tag": "BIRT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_tag2)
        birth_date2 = {
            "level": 2,
            "tag": "DATE",
            "args": "1 MAY 2010",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_date2)
        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.fam.print_all()
        sys.stdout = sys.__stdout__
        test_output = """+------+------------+------------+------------+--------------+---------+------------+--------------------+
|  ID  |  Married   |  Divorced  | Husband ID | Husband Name | Wife ID | Wife Name  |      Children      |
+------+------------+------------+------------+--------------+---------+------------+--------------------+
| @F1@ | 1952-05-06 | 1992-04-26 |    @A4@    |  Jane /Doe/  |   @A3@  | Jane /Doe/ | ['@I11@', '@I12@'] |
+------+------------+------------+------------+--------------+---------+------------+--------------------+
"""
        self.assertEqual(test_output, output.getvalue())

    def test_print_all_no_dates(self):
        """test print all families without dates
        """
        # raw lines:
        # 0 @F1@ FAM
        # 1 HUSB @A4@
        # 1 WIFE @A3@
        fam_data = {
            "level": 0,
            "tag": "FAM",
            "args": "@F1@",
            "valid": "Y"
        }
        self.fam.process_line_data(fam_data)
        husband_data = {
            "level": 1,
            "tag": "HUSB",
            "args": "@A4@",
            "valid": "Y"
        }
        self.fam.process_line_data(husband_data)
        wife_data = {
            "level": 1,
            "tag": "WIFE",
            "args": "@A3@",
            "valid": "Y"
        }
        self.fam.process_line_data(wife_data)
        child1_data = {
            "level": 1,
            "tag": "CHIL",
            "args": "@I11@",
            "valid": "Y"
        }
        self.fam.process_line_data(child1_data)
        child2_data = {
            "level": 1,
            "tag": "CHIL",
            "args": "@I12@",
            "valid": "Y"
        }
        self.fam.process_line_data(child2_data)
        # load up spouses data
        data1 = {
            "level": 0,
            "tag": "INDI",
            "args": "@A3@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data1)
        name_tag1 = {
            "level": 1,
            "tag": "NAME",
            "args": "Jane /Doe/",
            "valid": "Y"
        }
        self.peeps.process_line_data(name_tag1)
        data2 = {
            "level": 0,
            "tag": "INDI",
            "args": "@A4@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data2)
        name_tag2 = {
            "level": 1,
            "tag": "NAME",
            "args": "Jane /Doe/",
            "valid": "Y"
        }
        self.peeps.process_line_data(name_tag2)
        data3 = {
            "level": 0,
            "tag": "INDI",
            "args": "@I11@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data3)
        birth_tag1 = {
            "level": 1,
            "tag": "BIRT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_tag1)
        birth_date1 = {
            "level": 2,
            "tag": "DATE",
            "args": "1 MAY 2001",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_date1)
        data4 = {
            "level": 0,
            "tag": "INDI",
            "args": "@I12@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data4)
        birth_tag2 = {
            "level": 1,
            "tag": "BIRT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_tag2)
        birth_date2 = {
            "level": 2,
            "tag": "DATE",
            "args": "1 MAY 2010",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_date2)
        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.fam.print_all()
        sys.stdout = sys.__stdout__
        test_output = """+------+---------+----------+------------+--------------+---------+------------+--------------------+
|  ID  | Married | Divorced | Husband ID | Husband Name | Wife ID | Wife Name  |      Children      |
+------+---------+----------+------------+--------------+---------+------------+--------------------+
| @F1@ |    NA   |    NA    |    @A4@    |  Jane /Doe/  |   @A3@  | Jane /Doe/ | ['@I11@', '@I12@'] |
+------+---------+----------+------------+--------------+---------+------------+--------------------+
"""
        self.assertEqual(test_output, output.getvalue())

    def test_US28_print_all_ordered_children(self):
        """test print all families with children ordered by age
        """
        # raw data lines:
        # 0 @F1@ FAM
        # 1 DIV
        # 2 DATE 26 APR 2017
        # 1 HUSB @I1@
        # 1 WIFE @I2@
        # 1 CHIL @I18@
        # 1 CHIL @I19@
        # 1 MARR
        # 2 DATE 15 JAN 1993
        fam_data = {
            "level": 0,
            "tag": "FAM",
            "args": "@F1@",
            "valid": "Y"
        }
        self.fam.process_line_data(fam_data)
        div_tag = {
            "level": 1,
            "tag": "DIV",
            "args": "",
            "valid": "Y"
        }
        self.fam.process_line_data(div_tag)
        div_date = {
            "level": 2,
            "tag": "DATE",
            "args": "26 APR 2017",
            "valid": "Y"
        }
        self.fam.process_line_data(div_date)
        husband_data = {
            "level": 1,
            "tag": "HUSB",
            "args": "@I1@",
            "valid": "Y"
        }
        self.fam.process_line_data(husband_data)
        wife_data = {
            "level": 1,
            "tag": "WIFE",
            "args": "@I2@",
            "valid": "Y"
        }
        self.fam.process_line_data(wife_data)
        child1_data = {
            "level": 1,
            "tag": "CHIL",
            "args": "@I18@",
            "valid": "Y"
        }
        self.fam.process_line_data(child1_data)
        child2_data = {
            "level": 1,
            "tag": "CHIL",
            "args": "@I19@",
            "valid": "Y"
        }
        self.fam.process_line_data(child2_data)
        mar_tag = {
            "level": 1,
            "tag": "MARR",
            "args": "",
            "valid": "Y"
        }
        self.fam.process_line_data(mar_tag)
        mar_date = {
            "level": 2,
            "tag": "DATE",
            "args": "15 JAN 1993",
            "valid": "Y"
        }
        self.fam.process_line_data(mar_date)
        # load data for the individuals in family
        data1 = {
            "level": 0,
            "tag": "INDI",
            "args": "@I1@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data1)
        name_tag1 = {
            "level": 1,
            "tag": "NAME",
            "args": "Jane /Doe/",
            "valid": "Y"
        }
        self.peeps.process_line_data(name_tag1)
        data2 = {
            "level": 0,
            "tag": "INDI",
            "args": "@I2@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data2)
        name_tag2 = {
            "level": 1,
            "tag": "NAME",
            "args": "Jane /Doe/",
            "valid": "Y"
        }
        self.peeps.process_line_data(name_tag2)
        data3 = {
            "level": 0,
            "tag": "INDI",
            "args": "@I18@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data3)
        birth_tag1 = {
            "level": 1,
            "tag": "BIRT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_tag1)
        birth_date1 = {
            "level": 2,
            "tag": "DATE",
            "args": "3 OCT 2001",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_date1)
        data4 = {
            "level": 0,
            "tag": "INDI",
            "args": "@I19@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data4)
        birth_tag2 = {
            "level": 1,
            "tag": "BIRT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_tag2)
        birth_date2 = {
            "level": 2,
            "tag": "DATE",
            "args": "1 MAY 2010",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_date2)
        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.fam.print_all()
        sys.stdout = sys.__stdout__
        test_output = """+------+------------+------------+------------+--------------+---------+------------+--------------------+
|  ID  |  Married   |  Divorced  | Husband ID | Husband Name | Wife ID | Wife Name  |      Children      |
+------+------------+------------+------------+--------------+---------+------------+--------------------+
| @F1@ | 1993-01-15 | 2017-04-26 |    @I1@    |  Jane /Doe/  |   @I2@  | Jane /Doe/ | ['@I18@', '@I19@'] |
+------+------------+------------+------------+--------------+---------+------------+--------------------+
"""
        self.assertEqual(test_output, output.getvalue())

    def test_print_all_in_order(self):
        """test print all families in order
        """
        # raw lines:
        # 0 @F6@ FAM
        # 0 @F5@ FAM
        fam_data1 = {
            "level": 0,
            "tag": "FAM",
            "args": "@F6@",
            "valid": "Y"
        }
        self.fam.process_line_data(fam_data1)
        fam_data2 = {
            "level": 0,
            "tag": "FAM",
            "args": "@F5@",
            "valid": "Y"
        }
        self.fam.process_line_data(fam_data2)
        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.fam.print_all()
        sys.stdout = sys.__stdout__
        test_output = """+------+---------+----------+------------+--------------+---------+-----------+----------+
|  ID  | Married | Divorced | Husband ID | Husband Name | Wife ID | Wife Name | Children |
+------+---------+----------+------------+--------------+---------+-----------+----------+
| @F5@ |    NA   |    NA    |     NA     |      NA      |    NA   |     NA    |    []    |
| @F6@ |    NA   |    NA    |     NA     |      NA      |    NA   |     NA    |    []    |
+------+---------+----------+------------+--------------+---------+-----------+----------+
"""
        self.assertEqual(test_output, output.getvalue())

    def test_us05_validation_marriage_before_death(self):
        """US05: testing that a marriage occurred before death
        """
        # Family 1 setup (married before death)
        peep1 = Person("@I01@")
        peep1.set_name("Bob /Saget/")
        peep1.set_gender("M")
        peep1.set_date("17 AUG 1987", "birth")
        peep1.add_spouse_of_family("@F01@")

        self.peeps.individuals[peep1.get_person_id()] = peep1

        peep2 = Person("@I02@")
        peep2.set_name("Barbra /Saget/")
        peep2.set_gender("F")
        peep2.set_date("17 AUG 1990", "birth")
        peep2.set_date("17 JAN 2014", "death")
        peep2.add_spouse_of_family("@F01@")

        self.peeps.individuals[peep2.get_person_id()] = peep2

        fam1 = Family("@F01@")
        fam1.set_husband_id(peep1.get_person_id())
        fam1.set_wife_id(peep2.get_person_id())
        fam1.set_date("10 FEB 2012", "married")

        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup (married after death) FAILURE
        peep3 = Person("@I03@")
        peep3.set_name("Bob /Hope/")
        peep3.set_gender("M")
        peep3.set_date("17 AUG 1987", "birth")
        peep3.set_date("17 JAN 2010", "death")
        peep3.add_spouse_of_family("@F02@")
        self.peeps.individuals[peep3.get_person_id()] = peep3
        peep4 = Person("@I04@")
        peep4.set_name("Betty /White/")
        peep4.set_gender("F")
        peep4.set_date("17 AUG 1990", "birth")
        peep4.add_spouse_of_family("@F02@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        fam2 = Family("@F02@")
        fam2.set_husband_id(peep3.get_person_id())
        fam2.set_wife_id(peep4.get_person_id())
        fam2.set_date("10 FEB 2012", "married")
        self.fam.families[fam2.get_family_id()] = fam2

        # Family 3 setup (both alive)
        peep5 = Person("@I05@")
        peep5.set_name("Sammy /Davis jr./")
        peep5.set_gender("M")
        peep5.set_date("17 AUG 1990", "birth")
        peep5.add_spouse_of_family("@F03@")
        self.peeps.individuals[peep5.get_person_id()] = peep5
        peep6 = Person("@I06@")
        peep6.set_gender("F")
        peep6.set_name("Tina /Turner/")
        peep6.set_date("17 AUG 1990", "birth")
        peep6.add_spouse_of_family("@F03@")
        self.peeps.individuals[peep6.get_person_id()] = peep6
        fam3 = Family("@F03@")
        fam3.set_husband_id(peep5.get_person_id())
        fam3.set_wife_id(peep6.get_person_id())
        fam3.set_date("10 FEB 2012", "married")
        self.fam.families[fam3.get_family_id()] = fam3

        # Family 4 setup (both dead before marriage) DOUBLE FAILURE
        peep7 = Person("@I07@")
        peep7.set_name("Paris /Troy/")
        peep7.set_gender("M")
        peep7.set_date("17 AUG 1990", "birth")
        peep7.set_date("17 AUG 2011", "death")
        peep7.add_spouse_of_family("@F04@")
        self.peeps.individuals[peep7.get_person_id()] = peep7
        peep8 = Person("@I08@")
        peep8.set_name("Helena /Troy/")
        peep8.set_gender("F")
        peep8.set_date("17 AUG 1990", "birth")
        peep8.set_date("17 AUG 2010", "death")
        peep8.add_spouse_of_family("@F04@")
        self.peeps.individuals[peep8.get_person_id()] = peep8
        fam4 = Family("@F04@")
        fam4.set_husband_id(peep7.get_person_id())
        fam4.set_wife_id(peep8.get_person_id())
        fam4.set_date("10 FEB 2012", "married")
        self.fam.families[fam4.get_family_id()] = fam4

        # Family 5 setup no married date
        peep9 = Person("@I09@")
        peep9.set_name("Paris /Troy/")
        peep9.set_gender("M")
        peep9.set_date("17 AUG 1990", "birth")
        peep9.set_date("17 AUG 2011", "death")
        peep9.add_spouse_of_family("@F05@")
        self.peeps.individuals[peep9.get_person_id()] = peep9
        peep10 = Person("@I10@")
        peep10.set_name("Helena /Troy/")
        peep10.set_gender("F")
        peep10.set_date("17 AUG 1990", "birth")
        peep10.set_date("17 AUG 2010", "death")
        peep10.add_spouse_of_family("@F05@")
        self.peeps.individuals[peep10.get_person_id()] = peep10
        fam5 = Family("@F05@")
        fam5.set_husband_id(peep9.get_person_id())
        fam5.set_wife_id(peep10.get_person_id())
        self.fam.families[fam5.get_family_id()] = fam5

        # Family 6 setup (no spouses)
        fam6 = Family("@F06@")
        fam6.set_date("10 FEB 2012", "married")
        self.fam.families[fam6.get_family_id()] = fam6

        self.fam.validate()
        results = self.msgs.get_messages()

        self.assertEqual(3, len(results))
        err1 = {
            "error_id": "FAMILY",
            "user_story": "US05",
            "user_id": fam2.get_family_id(),
            "name": "NA",
            "message": "marriage after death for " + peep3.get_person_id() + " " + peep3.get_name()
        }
        self.assertDictEqual(err1, results[0])
        err2 = {
            "error_id": "FAMILY",
            "user_story": "US05",
            "user_id": fam4.get_family_id(),
            "name": "NA",
            "message": "marriage after death for " + peep7.get_person_id() + " " + peep7.get_name()
        }
        self.assertDictEqual(err2, results[1])
        err3 = {
            "error_id": "FAMILY",
            "user_story": "US05",
            "user_id": fam4.get_family_id(),
            "name": "NA",
            "message": "marriage after death for " + peep8.get_person_id() + " " + peep8.get_name()
        }
        self.assertDictEqual(err3, results[2])

    def test_us26_corresponding_entries(self):
        """US26:testing corresponding entires for family links in links for that individual
        and that the person links are correct for the families
        """
        # Family checks
        peep1 = Person("@I01@")  # INVALID missing spouse of family link
        peep1.set_name("Bob /Saget/")
        peep1.set_gender("M")
        peep1.set_date("17 AUG 1987", "birth")
        self.peeps.individuals[peep1.get_person_id()] = peep1
        peep2 = Person("@I02@")  # valid spouse
        peep2.set_name("Marylin /Saget/")
        peep2.set_gender("F")
        peep2.set_date("17 AUG 1990", "birth")
        peep2.add_spouse_of_family("@F01@")
        self.peeps.individuals[peep2.get_person_id()] = peep2
        peep3 = Person("@I03@")  # invalid child
        peep3.set_name("Jannet /Saget/")
        peep3.set_gender("F")
        peep3.set_date("17 AUG 2010", "birth")
        self.peeps.individuals[peep3.get_person_id()] = peep3
        peep4 = Person("@I04@")  # valid child
        peep4.set_name("Jeffrey /Saget/")
        peep4.set_gender("M")
        peep4.set_date("17 AUG 2012", "birth")
        peep4.add_children_of_family("@F01@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        fam1 = Family("@F01@")  # valid family
        fam1.set_husband_id(peep1.get_person_id())
        fam1.set_wife_id(peep2.get_person_id())
        fam1.add_child(peep3.get_person_id())
        fam1.add_child(peep4.get_person_id())
        self.fam.families[fam1.get_family_id()] = fam1

        self.fam.validate()
        results = self.msgs.get_messages()

        self.assertEqual(2, len(results))
        err1 = {
            "error_id": Families.CLASS_IDENTIFIER,
            "user_story": "US26",
            "user_id": fam1.get_family_id(),
            "name": "NA",
            "message": "corresponding spouse link missing for " + peep1.get_person_id() + " " + peep1.get_name()
        }
        self.assertDictEqual(err1, results[0])
        err2 = {
            "error_id": Families.CLASS_IDENTIFIER,
            "user_story": "US26",
            "user_id": fam1.get_family_id(),
            "name": "NA",
            "message": "corresponding child link missing for " + peep3.get_person_id() + " " + peep3.get_name()
        }
        self.assertDictEqual(err2, results[1])

        # Individual checks
        peep4 = Person("@I04@")  # INVALID missing spouse of family link
        peep4.set_name("Bob /Saget/")
        peep4.set_gender("M")
        peep4.set_date("17 AUG 1987", "birth")
        peep4.add_spouse_of_family("@F01@")
        peep4.add_spouse_of_family("@F02@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        peep5 = Person("@I05@")  # Invalid
        peep5.set_name("Marylin /Saget/")
        peep5.set_gender("F")
        peep5.set_date("17 AUG 1990", "birth")
        peep5.add_spouse_of_family("@F02@")
        self.peeps.individuals[peep5.get_person_id()] = peep5
        peep6 = Person("@I06@")  # invalid child
        peep6.set_name("Jannet /Saget/")
        peep6.set_gender("F")
        peep6.set_date("17 AUG 2010", "birth")
        peep6.add_children_of_family("@F02@")
        self.peeps.individuals[peep6.get_person_id()] = peep6
        fam2 = Family("@F02@")
        fam2.set_husband_id(peep4.get_person_id())
        fam2.set_wife_id(peep5.get_person_id())
        self.fam.families[fam2.get_family_id()] = fam2

        self.peeps.validate()
        results = self.msgs.get_messages()

        self.assertEqual(4, len(results))
        err3 = {
            "error_id": People.CLASS_IDENTIFIER,
            "user_story": "US26",
            "user_id": peep4.get_person_id(),
            "name": peep4.get_name(),
            "message": "corresponding spouse link missing in family " + fam1.get_family_id()
        }
        self.assertDictEqual(err3, results[2])
        err4 = {
            "error_id": People.CLASS_IDENTIFIER,
            "user_story": "US26",
            "user_id": peep6.get_person_id(),
            "name": peep6.get_name(),
            "message": "corresponding child link missing in family " + fam2.get_family_id()
        }
        self.assertDictEqual(err4, results[3])

    def test_us06_validation_divorce_before_death(self):
        """US06: testing that a divorce occurred before death
        """
        # Family 1 setup (divorced before death)
        peep1 = Person("@I01@")
        peep1.set_name("Bob /Saget/")
        peep1.set_gender("M")
        peep1.set_date("17 AUG 1987", "birth")
        peep1.add_spouse_of_family("@F06@")
        self.peeps.individuals[peep1.get_person_id()] = peep1
        peep2 = Person("@I02@")
        peep2.set_name("Marylin /Monroe/")
        peep2.set_gender("F")
        peep2.set_date("17 AUG 1990", "birth")
        peep2.set_date("17 JAN 2014", "death")
        peep2.add_spouse_of_family("@F06@")
        self.peeps.individuals[peep2.get_person_id()] = peep2
        fam1 = Family("@F06@")
        fam1.set_husband_id(peep1.get_person_id())
        fam1.set_wife_id(peep2.get_person_id())
        fam1.set_date("10 FEB 2011", "married")
        fam1.set_date("11 FEB 2012", "divorced")
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup (divorced after death) FAILURE
        peep3 = Person("@I03@")
        peep3.set_name("Bob /Hope/")
        peep3.set_gender("M")
        peep3.set_date("17 AUG 1987", "birth")
        peep3.set_date("17 JAN 2010", "death")
        peep3.add_spouse_of_family("@F02@")
        self.peeps.individuals[peep3.get_person_id()] = peep3
        peep4 = Person("@I04@")
        peep4.set_name("Betty /White/")
        peep4.set_gender("F")
        peep4.set_date("17 AUG 1980", "birth")
        peep4.set_date("17 JAN 2014", "death")
        peep4.add_spouse_of_family("@F02@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        fam2 = Family("@F02@")
        fam2.set_husband_id(peep3.get_person_id())
        fam2.set_wife_id(peep4.get_person_id())
        fam2.set_date("10 FEB 2009", "married")
        fam2.set_date("11 FEB 2012", "divorced")
        self.fam.families[fam2.get_family_id()] = fam2

        # Family 3 setup (both alive)
        peep5 = Person("@I05@")
        peep5.set_name("Sammy /Davis jr./")
        peep5.set_gender("M")
        peep5.set_date("17 AUG 1990", "birth")
        peep5.add_spouse_of_family("@F03@")
        self.peeps.individuals[peep5.get_person_id()] = peep5
        peep6 = Person("@I06@")
        peep6.set_name("Sammi /Davis jr./")
        peep6.set_gender("F")
        peep6.set_date("17 AUG 1990", "birth")
        peep6.add_spouse_of_family("@F03@")
        self.peeps.individuals[peep6.get_person_id()] = peep6
        fam3 = Family("@F03@")
        fam3.set_husband_id(peep5.get_person_id())
        fam3.set_wife_id(peep6.get_person_id())
        fam3.set_date("10 FEB 2012", "married")
        fam3.set_date("10 FEB 2014", "divorced")
        self.fam.families[fam3.get_family_id()] = fam3

        # Family 4 setup (both dead before divorce) DOUBLE FAILURE
        peep7 = Person("@I07@")
        peep7.set_name("Paris /Troy/")
        peep7.set_gender("M")
        peep7.set_date("17 AUG 1980", "birth")
        peep7.set_date("17 AUG 2011", "death")
        peep7.add_spouse_of_family("@F04@")
        self.peeps.individuals[peep7.get_person_id()] = peep7
        peep8 = Person("@I08@")
        peep8.set_name("Helena /Troy/")
        peep8.set_gender("F")
        peep8.set_date("17 AUG 1980", "birth")
        peep8.set_date("17 AUG 2010", "death")
        peep8.add_spouse_of_family("@F04@")
        self.peeps.individuals[peep8.get_person_id()] = peep8
        fam4 = Family("@F04@")
        fam4.set_husband_id(peep7.get_person_id())
        fam4.set_wife_id(peep8.get_person_id())
        fam4.set_date("10 FEB 2009", "married")
        fam4.set_date("11 FEB 2015", "divorced")
        self.fam.families[fam4.get_family_id()] = fam4

        # Family 5 setup no divorced date
        peep9 = Person("@I09@")
        peep9.set_name("Matthew /Troy/")
        peep9.set_gender("M")
        peep9.set_date("17 AUG 1980", "birth")
        peep9.set_date("17 AUG 2011", "death")
        peep9.add_spouse_of_family("@F05@")
        self.peeps.individuals[peep9.get_person_id()] = peep9
        peep10 = Person("@I10@")
        peep10.set_name("Heather /Troy/")
        peep10.set_gender("F")
        peep10.set_date("17 AUG 1980", "birth")
        peep10.set_date("17 AUG 2010", "death")
        peep10.add_spouse_of_family("@F05@")
        self.peeps.individuals[peep10.get_person_id()] = peep10
        fam5 = Family("@F05@")
        fam5.set_husband_id(peep9.get_person_id())
        fam5.set_wife_id(peep10.get_person_id())
        self.fam.families[fam5.get_family_id()] = fam5

        # Family 6 setup (no spouses)
        fam6 = Family("@F05@")
        fam6.set_date("10 FEB 2012", "married")
        fam6.set_date("10 FEB 2013", "divorced")
        self.fam.families[fam6.get_family_id()] = fam6

        self.fam.validate()
        results = self.msgs.get_messages()

        self.assertEqual(3, len(results))
        err1 = {
            "error_id": "FAMILY",
            "user_story": "US06",
            "user_id": fam2.get_family_id(),
            "name": "NA",
            "message": "divorce after death for " + peep3.get_person_id() + " " + peep3.get_name()
        }
        self.assertDictEqual(err1, results[0])
        err2 = {
            "error_id": "FAMILY",
            "user_story": "US06",
            "user_id": fam4.get_family_id(),
            "name": "NA",
            "message": "divorce after death for " + peep7.get_person_id() + " " + peep7.get_name()
        }
        self.assertDictEqual(err2, results[1])
        err3 = {
            "error_id": "FAMILY",
            "user_story": "US06",
            "user_id": fam4.get_family_id(),
            "name": "NA",
            "message": "divorce after death for " + peep8.get_person_id() + " " + peep8.get_name()
        }
        self.assertDictEqual(err3, results[2])

    def test_us02_us10_valid_married_date_and_age(self):
        """ US02: is marriage valid. US10: are spouses at
        least 14 when married
        """
        # Family 1 invalid married date
        peep1 = Person("@I1@")
        peep1.set_name("Tony /Tiger/")
        peep1.set_gender("M")
        peep1.set_date("1 JAN 1970", "birth")
        peep1.add_spouse_of_family("@F1@")
        self.peeps.individuals[peep1.get_person_id()] = peep1
        peep2 = Person("@I2@")
        peep2.set_name("Minnie /Mouse/")
        peep2.set_gender("F")
        peep2.set_date("20 JUL 1970", "birth")
        peep2.add_spouse_of_family("@F1@")
        self.peeps.individuals[peep2.get_person_id()] = peep2
        fam1 = Family("@F1@")
        fam1.set_husband_id("@I1@")
        fam1.set_wife_id("@I2@")
        fam1.set_date("1 JAN 1960", "married")
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 valid married date
        peep3 = Person("@I3@")
        peep3.set_name("Bob /Tiger/")
        peep3.set_gender("M")
        peep3.set_date("1 JAN 1970", "birth")
        peep3.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep3.get_person_id()] = peep3
        peep4 = Person("@I4@")
        peep4.set_name("Sally /Mouse/")
        peep4.set_gender("F")
        peep4.set_date("20 JUL 1970", "birth")
        peep4.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        fam2 = Family("@F2@")
        fam2.set_husband_id("@I3@")
        fam2.set_wife_id("@I4@")
        fam2.set_date("1 JAN 1990", "married")
        self.fam.families[fam2.get_family_id()] = fam2

        # Family 9 setup (married: husband age 30, wife age 27) Valid
        peep28 = Person("@I28@")
        peep28.set_name("SpongeBob /SquarePants/")
        peep28.set_gender("M")
        peep28.set_date("17 AUG 1987", "birth")
        peep28.add_spouse_of_family("@F9@")
        self.peeps.individuals[peep28.get_person_id()] = peep28
        peep29 = Person("@I29@")
        peep29.set_name("Sandy /Cheeks/")
        peep29.set_gender("F")
        peep29.set_date("19 AUG 1990", "birth")
        peep29.add_spouse_of_family("@F9@")
        self.peeps.individuals[peep29.get_person_id()] = peep29
        fam9 = Family("@F9@")
        fam9.set_date("4 OCT 2017", "married")
        fam9.set_husband_id(peep28.get_person_id())
        fam9.set_wife_id(peep29.get_person_id())
        self.fam.families[fam9.get_family_id()] = fam9

        # Family 10 setup (married: husband age 14, wife age 14) Valid
        peep30 = Person("@I30@")
        peep30.set_name("Patrick /Star/")
        peep30.set_gender("M")
        peep30.set_date("17 AUG 2003", "birth")
        peep30.add_spouse_of_family("@F10@")
        self.peeps.individuals[peep30.get_person_id()] = peep30
        peep31 = Person("@I31@")
        peep31.set_name("Pearl /Crabs/")
        peep31.set_gender("F")
        peep31.set_date("25 MAY 2003", "birth")
        peep31.add_spouse_of_family("@F10@")
        self.peeps.individuals[peep31.get_person_id()] = peep31
        fam10 = Family("@F10@")
        fam10.set_date("4 OCT 2017", "married")
        fam10.set_husband_id(peep30.get_person_id())
        fam10.set_wife_id(peep31.get_person_id())
        self.fam.families[fam10.get_family_id()] = fam10

        # Family 11 setup (married: husband age 13, wife age 16) Invalid
        peep32 = Person("@I32@")
        peep32.set_name("Gary /Snail/")
        peep32.set_gender("M")
        peep32.set_date("17 AUG 2004", "birth")
        peep32.add_spouse_of_family("@F11@")
        self.peeps.individuals[peep32.get_person_id()] = peep32
        peep33 = Person("@I33@")
        peep33.set_name("Lady /Crustacean/")
        peep33.set_gender("F")
        peep33.set_date("25 AUG 2001", "birth")
        peep33.add_spouse_of_family("@F11@")
        self.peeps.individuals[peep33.get_person_id()] = peep33
        fam11 = Family("@F11@")
        fam11.set_date("4 OCT 2017", "married")
        fam11.set_husband_id(peep32.get_person_id())
        fam11.set_wife_id(peep33.get_person_id())
        self.fam.families[fam11.get_family_id()] = fam11

        # Family 12 setup (married: husband age 16, wife age 13) Invalid
        peep34 = Person("@I34@")
        peep34.set_name("Larry /Lobster/")
        peep34.set_gender("M")
        peep34.set_date("17 AUG 2001", "birth")
        peep34.add_spouse_of_family("@F12@")
        self.peeps.individuals[peep34.get_person_id()] = peep34
        peep35 = Person("@I35@")
        peep35.set_name("Tina /Tuna/")
        peep35.set_gender("F")
        peep35.set_date("25 AUG 2004", "birth")
        peep35.add_spouse_of_family("@F12@")
        self.peeps.individuals[peep35.get_person_id()] = peep35
        fam12 = Family("@F12@")
        fam12.set_husband_id(peep34.get_person_id())
        fam12.set_wife_id(peep35.get_person_id())
        fam12.set_date("4 OCT 2017", "married")
        self.fam.families[fam12.get_family_id()] = fam12

        # Family 13 setup (married: husband age 12, wife age 10) Invalid
        peep36 = Person("@I36@")
        peep36.set_name("Squidward /Tentacles/")
        peep36.set_gender("M")
        peep36.set_date("17 AUG 2005", "birth")
        peep36.add_spouse_of_family("@F13@")
        self.peeps.individuals[peep36.get_person_id()] = peep36
        peep37 = Person("@I37@")
        peep37.set_name("Karen /Tentacles/")
        peep37.set_gender("F")
        peep37.set_date("25 AUG 2007", "birth")
        peep37.add_spouse_of_family("@F13@")
        self.peeps.individuals[peep37.get_person_id()] = peep37
        fam13 = Family("@F13@")
        fam13.set_husband_id(peep36.get_person_id())
        fam13.set_wife_id(peep37.get_person_id())
        fam13.set_date("4 OCT 2017", "married")
        self.fam.families[fam13.get_family_id()] = fam13

        self.fam.validate()
        results = self.msgs.get_messages()

        self.assertEqual(8, len(results))

        err1 = {
            "error_id": "FAMILY",
            "user_story": "US10",
            "user_id": fam11.get_family_id(),
            "name": "NA",
            "message": "marriage before age 14 for " + peep32.get_person_id() + " " +
                       peep32.get_name()
        }
        self.assertDictEqual(err1, results[0])
        err2 = {
            "error_id": "FAMILY",
            "user_story": "US10",
            "user_id": fam12.get_family_id(),
            "name": "NA",
            "message": "marriage before age 14 for " + peep35.get_person_id() + " " +
                       peep35.get_name()
        }
        self.assertDictEqual(err2, results[1])
        err3 = {
            "error_id": "FAMILY",
            "user_story": "US10",
            "user_id": fam13.get_family_id(),
            "name": "NA",
            "message": "marriage before age 14 for " + peep36.get_person_id() + " " +
                       peep36.get_name()
        }
        self.assertDictEqual(err3, results[2])
        err4 = {
            "error_id": "FAMILY",
            "user_story": "US10",
            "user_id": fam13.get_family_id(),
            "name": "NA",
            "message": "marriage before age 14 for " + peep37.get_person_id() + " " +
                       peep37.get_name()
        }
        self.assertDictEqual(err4, results[3])
        err5 = {
            "error_id": "INDIVIDUAL",
            "user_story": "US02",
            "user_id": peep1.get_person_id(),
            "name": peep1.get_name(),
            "message": "Birth date should occur before marriage of an individual"
        }
        self.assertDictEqual(err5, results[4])
        err6 = {
            "error_id": "FAMILY",
            "user_story": "US10",
            "user_id": fam1.get_family_id(),
            "name": "NA",
            "message": "marriage before age 14 for " + peep1.get_person_id() + " " + peep1.get_name()
        }
        self.assertDictEqual(err6, results[5])
        err7 = {
            "error_id": "INDIVIDUAL",
            "user_story": "US02",
            "user_id": peep2.get_person_id(),
            "name": peep2.get_name(),
            "message": "Birth date should occur before marriage of an individual"
        }
        self.assertDictEqual(err7, results[6])
        err8 = {
            "error_id": "FAMILY",
            "user_story": "US10",
            "user_id": fam1.get_family_id(),
            "name": "NA",
            "message": "marriage before age 14 for " + peep2.get_person_id() + " " + peep2.get_name()
        }
        self.assertDictEqual(err8, results[7])

    def test_us04_validation_marriage_before_divorce(self):
        """US04: testing that marriage occurred before divorce
        """
        # Family 1 setup (married before divorced) Pass
        fam1 = Family("@F01@")
        fam1.set_date("10 FEB 1980", "married")
        fam1.set_date("11 FEB 2015", "divorced")
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup (married after divorced) FAILURE
        fam2 = Family("@F02@")
        fam2.set_date("10 FEB 2015", "married")
        fam2.set_date("10 FEB 2011", "divorced")
        self.fam.families[fam2.get_family_id()] = fam2

        # Family 3 setup (married before divorced) Failure
        fam3 = Family("@F03@")
        fam3.set_date("10 FEB 2016", "married")
        fam3.set_date("11 FEB 2015", "divorced")
        self.fam.families[fam3.get_family_id()] = fam3

        # Family 4 setup (marriage after divorce for two previously married individuals) Failure
        fam4 = Family("@F04@")
        fam4.set_date("10 FEB 2017", "married")
        fam4.set_date("11 FEB 2015", "divorced")
        self.fam.families[fam4.get_family_id()] = fam4

        # Family 5 setup
        fam5 = Family("@F05@")
        fam5.set_date("10 FEB 2013", "married")
        fam5.set_date("11 FEB 2012", "divorced")
        self.fam.families[fam5.get_family_id()] = fam5

        self.fam.validate()
        results = self.msgs.get_messages()

        self.assertEqual(4, len(results))
        err1 = {
            "error_id": "FAMILY",
            "user_story": "US04",
            "user_id": fam2.get_family_id(),
            "name": "NA",
            "message": "Marriage date should occur before divorce date of a family"
        }
        self.assertDictEqual(err1, results[0])
        err2 = {
            "error_id": "FAMILY",
            "user_story": "US04",
            "user_id": fam3.get_family_id(),
            "name": "NA",
            "message": "Marriage date should occur before divorce date of a family"
        }
        self.assertDictEqual(err2, results[1])
        err3 = {
            "error_id": "FAMILY",
            "user_story": "US04",
            "user_id": fam4.get_family_id(),
            "name": "NA",
            "message": "Marriage date should occur before divorce date of a family"
        }
        self.assertDictEqual(err3, results[2])
        err4 = {
            "error_id": "FAMILY",
            "user_story": "US04",
            "user_id": fam5.get_family_id(),
            "name": "NA",
            "message": "Marriage date should occur before divorce date of a family"
        }
        self.assertDictEqual(err4, results[3])

    def test_us01_validation_marriage_and_divorce_before_current(self):
        """US01: testing that marriage and divorce dates occurred before current date
        """
        curr = datetime.now()

        # Family 1 setup (married before current) pass
        fam1 = Family("@F03@")
        fam1.set_date("19 MAY 1991", "married")
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup (married after current) fail
        fam2invalid = Family("@F01@")
        fam2invalid.set_date("4 OCT " + str(curr.year + 4), "married")
        self.fam.families[fam2invalid.get_family_id()] = fam2invalid

        # Family 3 setup (divorced after current) fail
        fam3invalid = Family("@F02@")
        fam3invalid.set_date("6 MAY 1952", "married")
        fam3invalid.set_date("6 NOV " + str(curr.year + 2), "divorced")
        self.fam.families[fam3invalid.get_family_id()] = fam3invalid

        self.fam.validate()
        results = self.msgs.get_messages()

        self.assertEqual(2, len(results))
        err1 = {
            "error_id": "FAMILY",
            "user_story": "US01",
            "user_id": fam2invalid.get_family_id(),
            "name": "NA",
            "message": "Married date should occur before current date for a family"
        }
        self.assertDictEqual(err1, results[0])
        err2 = {
            "error_id": "FAMILY",
            "user_story": "US01",
            "user_id": fam3invalid.get_family_id(),
            "name": "NA",
            "message": "Divorced date should occur before current date for a family"
        }
        self.assertDictEqual(err2, results[1])

    def test_us09_validation_child_before_parent_death(self):
        """US09: testing that a child birth occurred before parent death
        """
        # Family 1 setup (child 5ish years before mom death) Valid
        peep1 = Person("@I1@")
        peep1.set_name("Philip /Banks/")
        peep1.set_gender("M")
        peep1.set_date("17 AUG 1987", "birth")
        peep1.add_spouse_of_family("@F1@")
        self.peeps.individuals[peep1.get_person_id()] = peep1
        peep2 = Person("@I2@")
        peep2.set_name("Vivian /Banks/")
        peep2.set_gender("F")
        peep2.set_date("17 AUG 1990", "birth")
        peep2.set_date("17 JAN 2014", "death")
        peep2.add_spouse_of_family("@F1@")
        self.peeps.individuals[peep2.get_person_id()] = peep2
        peep3 = Person("@I3@")
        peep3.set_name("Fresh /Banks/")
        peep3.set_gender("M")
        peep3.set_date("17 AUG 2009", "birth")
        peep3.add_children_of_family("@F1@")
        self.peeps.individuals[peep3.get_person_id()] = peep3
        fam1 = Family("@F1@")
        fam1.set_husband_id(peep1.get_person_id())
        fam1.set_wife_id(peep2.get_person_id())
        fam1.add_child(peep3.get_person_id())
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup (child 5 years before dad death) Valid
        peep4 = Person("@I4@")
        peep4.set_name("Doug /Funnie/")
        peep4.set_gender("M")
        peep4.set_date("17 AUG 1987", "birth")
        peep4.set_date("17 SEP 2014", "death")
        peep4.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        peep5 = Person("@I5@")
        peep5.set_gender("F")
        peep5.set_name("Pattie /Mayonaise/")
        peep5.set_date("17 AUG 1990", "birth")
        peep5.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep5.get_person_id()] = peep5
        peep6 = Person("@I6@")
        peep6.set_gender("F")
        peep6.set_name("Frankie /Funnie/")
        peep6.set_date("17 AUG 2009", "birth")
        peep6.add_children_of_family("@F2@")
        self.peeps.individuals[peep6.get_person_id()] = peep6
        fam2 = Family("@F2@")
        fam2.set_husband_id(peep4.get_person_id())
        fam2.set_wife_id(peep5.get_person_id())
        fam2.add_child(peep6.get_person_id())
        self.fam.families[fam2.get_family_id()] = fam2

        # Family 3 setup (child 2 years after dad death) Invalid
        peep7 = Person("@I7@")
        peep7.set_name("Jack /Daniels/")
        peep7.set_gender("M")
        peep7.set_date("17 AUG 1987", "birth")
        peep7.set_date("17 SEP 2014", "death")
        peep7.add_spouse_of_family("@F3@")
        self.peeps.individuals[peep7.get_person_id()] = peep7
        peep8 = Person("@I8@")
        peep8.set_gender("F")
        peep8.set_name("Margarita /Daniels/")
        peep8.set_date("17 AUG 1990", "birth")
        peep8.add_spouse_of_family("@F3@")
        self.peeps.individuals[peep8.get_person_id()] = peep8
        peep9 = Person("@I9@")
        peep9.set_gender("M")
        peep9.set_name("Whiskey /Daniels/")
        peep9.set_date("17 AUG 2016", "birth")
        peep9.add_children_of_family("@F3@")
        self.peeps.individuals[peep9.get_person_id()] = peep9
        fam3 = Family("@F3@")
        fam3.set_husband_id(peep7.get_person_id())
        fam3.set_wife_id(peep8.get_person_id())
        fam3.add_child(peep9.get_person_id())
        self.fam.families[fam3.get_family_id()] = fam3

        # Family 4 setup (child exactly 9 months before dad death) Valid
        peep10 = Person("@I10@")
        peep10.set_name("George /McFly/")
        peep10.set_gender("M")
        peep10.set_date("17 AUG 1987", "birth")
        peep10.set_date("17 SEP 2014", "death")
        peep10.add_spouse_of_family("@F4@")
        self.peeps.individuals[peep10.get_person_id()] = peep10
        peep11 = Person("@I11@")
        peep11.set_name("Lorraine /McFly/")
        peep11.set_gender("F")
        peep11.set_date("17 AUG 1990", "birth")
        peep11.add_spouse_of_family("@F4@")
        self.peeps.individuals[peep11.get_person_id()] = peep11
        peep12 = Person("@I12@")
        peep12.set_gender("M")
        peep12.set_name("Marty /McFly/")
        peep12.set_date("17 DEC 2013", "birth")
        peep12.add_children_of_family("@F4@")
        self.peeps.individuals[peep12.get_person_id()] = peep12
        fam4 = Family("@F4@")
        fam4.set_husband_id(peep10.get_person_id())
        fam4.set_wife_id(peep11.get_person_id())
        fam4.add_child(peep12.get_person_id())
        self.fam.families[fam4.get_family_id()] = fam4

        # Family 5 setup (child 9 months and some days but same month before dad death) Invalid
        peep13 = Person("@I13@")
        peep13.set_name("Homer /Simpson/")
        peep13.set_gender("M")
        peep13.set_date("17 AUG 1987", "birth")
        peep13.set_date("17 SEP 2014", "death")
        peep13.add_spouse_of_family("@F5@")
        self.peeps.individuals[peep13.get_person_id()] = peep13
        peep14 = Person("@I14@")
        peep14.set_name("Marge /Simpson/")
        peep14.set_gender("F")
        peep14.set_date("17 AUG 1990", "birth")
        peep14.add_spouse_of_family("@F5@")
        self.peeps.individuals[peep14.get_person_id()] = peep14
        peep15 = Person("@I15@")
        peep15.set_gender("M")
        peep15.set_name("Bart /Simpson/")
        peep15.set_date("1 JAN 2014", "birth")
        peep15.add_children_of_family("@F5@")
        self.peeps.individuals[peep15.get_person_id()] = peep15
        fam5 = Family("@F5@")
        fam5.set_husband_id(peep13.get_person_id())
        fam5.set_wife_id(peep14.get_person_id())
        fam5.add_child(peep15.get_person_id())
        self.fam.families[fam5.get_family_id()] = fam5

        # Family 6 setup (child 10 months before dad death) Valid
        peep19 = Person("@I19@")
        peep19.set_name("Dan /Conner/")
        peep19.set_gender("M")
        peep19.set_date("17 AUG 1987", "birth")
        peep19.set_date("17 SEP 2014", "death")
        peep19.add_spouse_of_family("@F6@")
        self.peeps.individuals[peep19.get_person_id()] = peep19
        peep20 = Person("@I20@")
        peep20.set_name("Roseanne /Conner/")
        peep20.set_gender("F")
        peep20.set_date("17 AUG 1990", "birth")
        peep20.add_spouse_of_family("@F6@")
        self.peeps.individuals[peep20.get_person_id()] = peep20
        peep21 = Person("@I21@")
        peep21.set_gender("F")
        peep21.set_name("Becky /Conner/")
        peep21.set_date("29 NOV 2013", "birth")
        peep21.add_children_of_family("@F6@")
        self.peeps.individuals[peep21.get_person_id()] = peep21
        fam6 = Family("@F6@")
        fam6.set_husband_id(peep19.get_person_id())
        fam6.set_wife_id(peep20.get_person_id())
        fam6.add_child(peep21.get_person_id())
        self.fam.families[fam6.get_family_id()] = fam6

        # Family 7 setup (child after mom death) Invalid
        peep22 = Person("@I22@")
        peep22.set_name("Carl /Winslow/")
        peep22.set_gender("M")
        peep22.set_date("17 AUG 1987", "birth")
        peep22.add_spouse_of_family("@F7@")
        self.peeps.individuals[peep22.get_person_id()] = peep22
        peep23 = Person("@I23@")
        peep23.set_name("Harriette /Winslow/")
        peep23.set_gender("F")
        peep23.set_date("17 AUG 1990", "birth")
        peep23.set_date("17 AUG 2016", "death")
        peep23.add_spouse_of_family("@F7@")
        self.peeps.individuals[peep23.get_person_id()] = peep23
        peep24 = Person("@I24@")
        peep24.set_name("Laura /Winslow/")
        peep24.set_gender("F")
        peep24.set_date("1 SEP 2016", "birth")
        peep24.add_children_of_family("@F7@")
        self.peeps.individuals[peep24.get_person_id()] = peep24
        fam7 = Family("@F7@")
        fam7.set_husband_id(peep22.get_person_id())
        fam7.set_wife_id(peep23.get_person_id())
        fam7.add_child(peep24.get_person_id())
        self.fam.families[fam7.get_family_id()] = fam7

        # Family 8 setup (child after mom death and dad death) Invalid
        peep25 = Person("@I25@")
        peep25.set_name("Walter /White/")
        peep25.set_gender("M")
        peep25.set_date("17 AUG 1987", "birth")
        peep25.set_date("20 OCT 2014", "death")
        peep25.add_spouse_of_family("@F8@")
        self.peeps.individuals[peep25.get_person_id()] = peep25
        peep26 = Person("@I26@")
        peep26.set_name("Skyler /White/")
        peep26.set_gender("F")
        peep26.set_date("17 AUG 1990", "birth")
        peep26.set_date("20 OCT 2014", "death")
        peep26.add_spouse_of_family("@F8@")
        self.peeps.individuals[peep26.get_person_id()] = peep26
        peep27 = Person("@I27@")
        peep27.set_name("Walter Jr /White/")
        peep27.set_gender("M")
        peep27.set_date("1 SEP 2016", "birth")
        peep27.add_children_of_family("@F8@")
        self.peeps.individuals[peep27.get_person_id()] = peep27
        fam8 = Family("@F8@")
        fam8.set_husband_id(peep25.get_person_id())
        fam8.set_wife_id(peep26.get_person_id())
        fam8.add_child(peep27.get_person_id())
        self.fam.families[fam8.get_family_id()] = fam8

        self.fam.validate()

        results = self.msgs.get_messages()

        self.assertEqual(5, len(results))
        err1 = {
            "error_id": "FAMILY",
            "user_story": "US09",
            "user_id": fam3.get_family_id(),
            "name": "NA",
            "message": "parent death before child birth for " + peep7.get_person_id() + " " +
                       peep7.get_name()
        }
        self.assertDictEqual(err1, results[0])
        err2 = {
            "error_id": "FAMILY",
            "user_story": "US09",
            "user_id": fam5.get_family_id(),
            "name": "NA",
            "message": "parent death before child birth for " + peep13.get_person_id() + " " +
                       peep13.get_name()
        }
        self.assertDictEqual(err2, results[1])
        err3 = {
            "error_id": "FAMILY",
            "user_story": "US09",
            "user_id": fam7.get_family_id(),
            "name": "NA",
            "message": "parent death before child birth for " + peep23.get_person_id() + " " +
                       peep23.get_name()
        }
        self.assertDictEqual(err3, results[2])
        err4 = {
            "error_id": "FAMILY",
            "user_story": "US09",
            "user_id": fam8.get_family_id(),
            "name": "NA",
            "message": "parent death before child birth for " + peep25.get_person_id() + " " +
                       peep25.get_name()
        }
        self.assertDictEqual(err4, results[3])
        err5 = {
            "error_id": "FAMILY",
            "user_story": "US09",
            "user_id": fam8.get_family_id(),
            "name": "NA",
            "message": "parent death before child birth for " + peep26.get_person_id() + " " +
                       peep26.get_name()
        }
        self.assertDictEqual(err5, results[4])

    def test_us25_validation_children_unique_first_name(self):
        """US25: testing that a child first name is unique
        """
        # Family 1 setup valid
        peep1 = Person("@I1@")
        peep1.set_name("Philip /Banks/")
        peep1.set_gender("M")
        peep1.set_date("17 AUG 1987", "birth")
        peep1.add_spouse_of_family("@F1@")
        self.peeps.individuals[peep1.get_person_id()] = peep1
        peep2 = Person("@I2@")
        peep2.set_name("Vivian /Banks/")
        peep2.set_gender("F")
        peep2.set_date("17 AUG 1990", "birth")
        peep2.set_date("17 JAN 2014", "death")
        peep2.add_spouse_of_family("@F1@")
        self.peeps.individuals[peep2.get_person_id()] = peep2
        peep3 = Person("@I3@")
        peep3.set_name("Freshie /Banks/")
        peep3.set_gender("M")
        peep3.set_date("17 AUG 2009", "birth")
        peep3.add_children_of_family("@F1@")
        self.peeps.individuals[peep3.get_person_id()] = peep3
        peep4 = Person("@I4@")
        peep4.set_name("Frank /Banks/")
        peep4.set_gender("M")
        peep4.set_date("17 AUG 2010", "birth")
        peep4.add_children_of_family("@F1@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        peep5 = Person("@I5@")
        peep5.set_name("Felix /Banks/")
        peep5.set_gender("M")
        peep5.set_date("17 AUG 2011", "birth")
        peep5.add_children_of_family("@F1@")
        self.peeps.individuals[peep5.get_person_id()] = peep5
        fam1 = Family("@F1@")
        fam1.set_husband_id(peep1.get_person_id())
        fam1.set_wife_id(peep2.get_person_id())
        fam1.add_child(peep3.get_person_id())
        fam1.add_child(peep4.get_person_id())
        fam1.add_child(peep5.get_person_id())
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup invalid
        peep6 = Person("@I6@")
        peep6.set_name("Doug /Funnie/")
        peep6.set_gender("M")
        peep6.set_date("17 AUG 1987", "birth")
        peep6.set_date("17 SEP 2014", "death")
        peep6.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep6.get_person_id()] = peep6
        peep7 = Person("@I7@")
        peep7.set_gender("F")
        peep7.set_name("Pattie /Mayonaise/")
        peep7.set_date("17 AUG 1990", "birth")
        peep7.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep7.get_person_id()] = peep7
        peep8 = Person("@I8@")
        peep8.set_gender("F")
        peep8.set_name("Frankie /Funnie/")
        peep8.set_date("17 AUG 2009", "birth")
        peep8.add_children_of_family("@F2@")
        self.peeps.individuals[peep8.get_person_id()] = peep8
        peep9 = Person("@I9@")
        peep9.set_gender("F")
        peep9.set_name("Frankie /Funnie/")
        peep9.set_date("17 AUG 2009", "birth")
        peep9.add_children_of_family("@F2@")
        self.peeps.individuals[peep9.get_person_id()] = peep9
        fam2 = Family("@F2@")
        fam2.set_husband_id(peep6.get_person_id())
        fam2.set_wife_id(peep7.get_person_id())
        fam2.add_child(peep8.get_person_id())
        fam2.add_child(peep9.get_person_id())
        self.fam.families[fam2.get_family_id()] = fam2

        # Family 3 setup valid
        peep10 = Person("@I10@")
        peep10.set_name("Doogie /Howser/")
        peep10.set_gender("M")
        peep10.set_date("17 AUG 1987", "birth")
        peep10.set_date("17 SEP 2014", "death")
        peep10.add_spouse_of_family("@F3@")
        self.peeps.individuals[peep10.get_person_id()] = peep10
        peep11 = Person("@I11@")
        peep11.set_gender("F")
        peep11.set_name("Pennie /Howser/")
        peep11.set_date("17 AUG 1990", "birth")
        peep11.add_spouse_of_family("@F3@")
        self.peeps.individuals[peep11.get_person_id()] = peep11
        peep12 = Person("@I12@")
        peep12.set_gender("F")
        peep12.set_name("Fruity /Howser/")
        peep12.set_date("17 AUG 2008", "birth")
        peep12.add_children_of_family("@F3@")
        self.peeps.individuals[peep12.get_person_id()] = peep12
        peep13 = Person("@I13@")
        peep13.set_gender("F")
        peep13.set_name("Fruity /Howser/")
        peep13.set_date("17 AUG 2009", "birth")
        peep13.add_children_of_family("@F3@")
        self.peeps.individuals[peep13.get_person_id()] = peep13
        fam3 = Family("@F3@")
        fam3.set_husband_id(peep10.get_person_id())
        fam3.set_wife_id(peep11.get_person_id())
        fam3.add_child(peep12.get_person_id())
        fam3.add_child(peep13.get_person_id())
        self.fam.families[fam3.get_family_id()] = fam3

        # Family 4 setup valid
        peep14 = Person("@I14@")
        peep14.set_name("Larry /Howser/")
        peep14.set_gender("M")
        peep14.set_date("17 AUG 1987", "birth")
        peep14.set_date("17 SEP 2014", "death")
        peep14.add_spouse_of_family("@F4@")
        self.peeps.individuals[peep14.get_person_id()] = peep14
        peep15 = Person("@I15@")
        peep15.set_gender("F")
        peep15.set_name("Lucinda /Howser/")
        peep15.set_date("17 AUG 1990", "birth")
        peep15.add_spouse_of_family("@F4@")
        self.peeps.individuals[peep15.get_person_id()] = peep15
        peep16 = Person("@I16@")
        peep16.set_gender("F")
        peep16.set_name("Lila /Howser/")
        peep16.set_date("17 AUG 2009", "birth")
        peep16.add_children_of_family("@F4@")
        self.peeps.individuals[peep16.get_person_id()] = peep16
        peep17 = Person("@I17@")
        peep17.set_gender("F")
        peep17.set_name("Linda /Howser/")
        peep17.set_date("17 AUG 2009", "birth")
        peep17.add_children_of_family("@F4@")
        self.peeps.individuals[peep17.get_person_id()] = peep17
        fam4 = Family("@F4@")
        fam4.set_husband_id(peep14.get_person_id())
        fam4.set_wife_id(peep15.get_person_id())
        fam4.add_child(peep16.get_person_id())
        fam4.add_child(peep17.get_person_id())
        self.fam.families[fam4.get_family_id()] = fam4

        self.fam.validate()

        results = self.msgs.get_messages()
        self.assertEqual(1, len(results))
        err1 = {
            "error_id": Families.CLASS_IDENTIFIER,
            "user_story": "US25",
            "user_id": fam2.get_family_id(),
            "name": "NA",
            "message": "Children in a family must have unique first name and birthday"
        }
        self.assertDictEqual(err1, results[0])

    def test_us16_male_last_names(self):
        """US16 All males in a family have the same last name
        """
        fam1_id = "@F01@"
        fam1_male1 = Person("@F1I1@")
        fam1_male1.set_gender("M")
        fam1_male1.set_name("Bob /Hope/")
        fam1_male1.add_spouse_of_family(fam1_id)
        fam1_male1.set_date("1 JAN 1965", "birth")
        fam1_male2 = Person("@F1I2@")
        fam1_male2.set_gender("M")
        fam1_male2.set_name("Greg /Hope/")
        fam1_male2.set_date("1 JAN 1965", "birth")
        fam1_male2.add_children_of_family(fam1_id)
        fam1_male2.set_date("1 JAN 1965", "birth")
        fam1_female1 = Person("@F1I4@")
        fam1_female1.set_gender("F")
        fam1_female1.set_name("Sally /Fields/")
        fam1_female1.set_date("1 JAN 1965", "birth")
        fam1_female1.add_spouse_of_family(fam1_id)
        fam1 = Family(fam1_id)
        fam1.set_husband_id(fam1_male1.get_person_id())
        fam1.set_wife_id(fam1_female1.get_person_id())
        fam1.add_child(fam1_male2.get_person_id())
        self.peeps.individuals[fam1_female1.get_person_id()] = fam1_female1
        self.peeps.individuals[fam1_male1.get_person_id()] = fam1_male1
        self.peeps.individuals[fam1_male2.get_person_id()] = fam1_male2
        self.fam.families[fam1.get_family_id()] = fam1

        fam2_id = "@F02@"
        fam2 = Family(fam2_id)
        fam2_male1 = Person("@F2I1@")
        fam2_male1.set_gender("M")
        fam2_male1.set_name("Sam /Spade/")
        fam2_male1.set_date("1 JAN 1965", "birth")
        fam2_male1.add_spouse_of_family(fam2_id)
        fam2_female1 = Person("@F2I2@")
        fam2_female1.set_gender("F")
        fam2_female1.set_date("1 JAN 1965", "birth")
        fam2_female1.add_spouse_of_family(fam2_id)
        fam2.set_husband_id(fam2_male1.get_person_id())
        fam2.set_wife_id(fam2_female1.get_person_id())
        self.peeps.individuals[fam2_female1.get_person_id()] = fam2_female1
        self.peeps.individuals[fam2_male1.get_person_id()] = fam2_male1
        self.fam.families[fam2.get_family_id()] = fam2

        self.fam.validate()

        self.assertEqual(0, len(self.msgs.get_messages()))

        fam1_male3 = Person("@F1I3@")
        fam1_male3.set_gender("M")
        fam1_male3.set_name("Al /Bundy/")
        fam1_male3.set_date("1 JAN 1965", "birth")
        fam1_male3.add_children_of_family(fam1_id)
        fam1.add_child(fam1_male3.get_person_id())
        self.peeps.individuals[fam1_male3.get_person_id()] = fam1_male3

        self.fam.validate()

        msgs = self.msgs.get_messages()
        self.assertEqual(1, len(msgs))

        err = {
            "error_id": Families.CLASS_IDENTIFIER,
            "user_story": "US16",
            "user_id": fam1.get_family_id(),
            "name": "NA",
            "message": "All males in a family must have the same last name"
        }
        self.assertDictEqual(err, msgs[0])

    def test_us17_no_marriages_to_descendants(self):
        """US17: test no marriages to decendants
        """
        # Family 1 setup VALID
        peep1 = Person("@I1@")
        peep1.set_name("Philip /Banks/")
        peep1.set_gender("M")
        peep1.set_date("17 AUG 1970", "birth")
        peep1.add_spouse_of_family("@F1@")
        peep1.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep1.get_person_id()] = peep1
        peep2 = Person("@I2@")
        peep2.set_name("Vivian /Banks/")
        peep2.set_gender("F")
        peep2.set_date("17 AUG 1980", "birth")
        peep2.set_date("17 JAN 2000", "death")
        peep2.add_spouse_of_family("@F1@")
        self.peeps.individuals[peep2.get_person_id()] = peep2
        peep3 = Person("@I3@")
        peep3.set_name("Fresh /Banks/")
        peep3.set_gender("F")
        peep3.set_date("17 AUG 1990", "birth")
        peep3.add_children_of_family("@F1@")
        peep3.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep3.get_person_id()] = peep3
        fam1 = Family("@F1@")
        fam1.set_husband_id(peep1.get_person_id())
        fam1.set_wife_id(peep2.get_person_id())
        fam1.add_child(peep3.get_person_id())
        fam1.set_date("20 FEB 1999", "married")
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup (same husband and wife is child from family 1) INVALID
        fam2 = Family("@F2@")
        fam2.set_husband_id(peep1.get_person_id())
        fam2.set_wife_id(peep3.get_person_id())
        fam2.set_date("13 JAN 2016", "married")
        self.fam.families[fam2.get_family_id()] = fam2

        # Family 3 setup VALID
        peep4 = Person("@I4@")
        peep4.set_name("Jack /Daniels/")
        peep4.set_gender("M")
        peep4.set_date("17 AUG 1980", "birth")
        peep4.set_date("17 JAN 2010", "death")
        peep4.add_spouse_of_family("@F3@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        peep5 = Person("@I5@")
        peep5.set_gender("F")
        peep5.set_name("Margarita /Daniels/")
        peep5.set_date("17 AUG 1980", "birth")
        peep5.add_spouse_of_family("@F3@")
        peep5.add_spouse_of_family("@F4@")
        self.peeps.individuals[peep5.get_person_id()] = peep5
        peep6 = Person("@I6@")
        peep6.set_gender("M")
        peep6.set_name("Whiskey /Daniels/")
        peep6.set_date("17 AUG 1999", "birth")
        peep6.add_children_of_family("@F3@")
        peep6.add_spouse_of_family("@F4@")
        self.peeps.individuals[peep6.get_person_id()] = peep6
        fam3 = Family("@F3@")
        fam3.set_husband_id(peep4.get_person_id())
        fam3.set_wife_id(peep5.get_person_id())
        fam3.add_child(peep6.get_person_id())
        fam3.set_date("21 FEB 2000", "married")
        self.fam.families[fam3.get_family_id()] = fam3

        # Family 4 setup (same wife and child from family 3) INVALID
        fam4 = Family("@F4@")
        fam4.set_husband_id(peep6.get_person_id())
        fam4.set_wife_id(peep5.get_person_id())
        fam4.set_date("16 SEP 2015", "married")
        self.fam.families[fam4.get_family_id()] = fam4

        # Family 5 setup VALID
        peep7 = Person("@I7@")
        peep7.set_name("Homer /Simpson/")
        peep7.set_gender("M")
        peep7.set_date("17 AUG 1960", "birth")
        peep7.set_date("17 SEP 2014", "death")
        peep7.add_spouse_of_family("@F5@")
        self.peeps.individuals[peep7.get_person_id()] = peep7
        peep8 = Person("@I8@")
        peep8.set_name("Marge /Simpson/")
        peep8.set_gender("F")
        peep8.set_date("17 AUG 1960", "birth")
        peep8.add_spouse_of_family("@F5@")
        peep8.add_spouse_of_family("@F7@")
        self.peeps.individuals[peep8.get_person_id()] = peep8
        peep9 = Person("@I9@")
        peep9.set_gender("F")
        peep9.set_name("Bartina /Simpson/")
        peep9.set_date("1 JAN 1980", "birth")
        peep9.add_children_of_family("@F5@")
        peep9.add_spouse_of_family("@F6@")
        self.peeps.individuals[peep9.get_person_id()] = peep9
        fam5 = Family("@F5@")
        fam5.set_husband_id(peep7.get_person_id())
        fam5.set_wife_id(peep8.get_person_id())
        fam5.add_child(peep9.get_person_id())
        fam5.set_date("19 FEB 1980", "married")
        fam5.set_date("20 MAR 1981", "divorced")
        self.fam.families[fam5.get_family_id()] = fam5

        # Family 6 setup (decendants of family 5) VALID
        peep10 = Person("@I10@")
        peep10.set_name("Tony /Waldo/")
        peep10.set_gender("M")
        peep10.set_date("17 AUG 1980", "birth")
        peep10.set_date("17 SEP 2014", "death")
        peep10.add_spouse_of_family("@F6@")
        self.peeps.individuals[peep10.get_person_id()] = peep10
        peep11 = Person("@I12@")
        peep11.set_gender("M")
        peep11.set_name("Frank /Waldo/")
        peep11.set_date("1 JAN 1999", "birth")
        peep11.add_children_of_family("@F6@")
        peep11.add_spouse_of_family("@F7@")
        self.peeps.individuals[peep11.get_person_id()] = peep11
        fam6 = Family("@F6@")
        fam6.set_husband_id(peep10.get_person_id())
        fam6.set_wife_id(peep9.get_person_id())
        fam6.add_child(peep11.get_person_id())
        fam6.set_date("20 FEB 2014", "married")
        self.fam.families[fam6.get_family_id()] = fam6

        # Family 7 setup (same wife as family 5) INVALID
        fam7 = Family("@F7@")
        fam7.set_husband_id(peep11.get_person_id())
        fam7.set_wife_id(peep8.get_person_id())
        fam7.set_date("1 JAN 2015", "married")
        self.fam.families[fam7.get_family_id()] = fam7

        self.fam.validate()

        results = self.msgs.get_messages()

        self.assertEqual(3, len(results))

        err1 = {
            "error_id": Families.CLASS_IDENTIFIER,
            "user_story": "US17",
            "user_id": fam2.get_family_id(),
            "name": "NA",
            "message": "No marriage to decendants. @I1@ Philip /Banks/"
        }

        self.assertDictEqual(err1, results[0])

        err2 = {
            "error_id": Families.CLASS_IDENTIFIER,
            "user_story": "US17",
            "user_id": fam4.get_family_id(),
            "name": "NA",
            "message": "No marriage to decendants. @I5@ Margarita /Daniels/"
        }

        self.assertDictEqual(err2, results[1])

        err3 = {
            "error_id": Families.CLASS_IDENTIFIER,
            "user_story": "US17",
            "user_id": fam7.get_family_id(),
            "name": "NA",
            "message": "No marriage to decendants. @I8@ Marge /Simpson/"
        }

        self.assertDictEqual(err3, results[2])

    def test_us15_fewer_than_15_siblings(self):
        """US15 there must be fewer than 15 siblings in a family
        """
        # Family 1 setup with three children - valid
        peep22 = Person("@I22@")
        peep22.set_name("Ashley /Banks/")
        peep22.set_gender("F")
        peep22.set_date("1 SEP 2016", "birth")
        peep22.add_children_of_family("@F1@")
        self.peeps.individuals[peep22.get_person_id()] = peep22
        peep23 = Person("@I23@")
        peep23.set_name("Carlton /Banks/")
        peep23.set_gender("M")
        peep23.set_date("1 SEP 2012", "birth")
        peep23.add_children_of_family("@F1@")
        self.peeps.individuals[peep23.get_person_id()] = peep23
        peep24 = Person("@I24@")
        peep24.set_name("Hilary /Banks/")
        peep24.set_gender("F")
        peep24.set_date("1 SEP 2010", "birth")
        peep24.add_children_of_family("@F1@")
        self.peeps.individuals[peep24.get_person_id()] = peep24
        fam1 = Family("@F1@")
        fam1.add_child(peep22.get_person_id())
        fam1.add_child(peep23.get_person_id())
        fam1.add_child(peep24.get_person_id())
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 set up with 15 children- invalid
        peep25 = Person("@I25@")
        peep25.set_name("Charlie /Chaplin/")
        peep25.add_children_of_family("@F3@")
        self.peeps.individuals[peep25.get_person_id()] = peep25
        peep26 = Person("@I26@")
        peep26.set_name("Hugh /Chaplin/")
        peep26.add_children_of_family("@F3@")
        self.peeps.individuals[peep26.get_person_id()] = peep26
        peep27 = Person("@I27@")
        peep27.set_name("Charlie /Chaplin/")
        peep27.add_children_of_family("@F3@")
        self.peeps.individuals[peep27.get_person_id()] = peep27
        peep28 = Person("@I28@")
        peep28.set_name("Charlie /Chaplin/")
        peep28.add_children_of_family("@F3@")
        self.peeps.individuals[peep28.get_person_id()] = peep28
        peep29 = Person("@I29@")
        peep29.set_name("Charlie /Chaplin/")
        peep29.add_children_of_family("@F3@")
        self.peeps.individuals[peep29.get_person_id()] = peep29
        peep30 = Person("@I30@")
        peep30.set_name("Charlie /Chaplin/")
        peep30.add_children_of_family("@F3@")
        self.peeps.individuals[peep30.get_person_id()] = peep30
        peep31 = Person("@I31@")
        peep31.set_name("Charlie /Chaplin/")
        peep31.add_children_of_family("@F3@")
        self.peeps.individuals[peep31.get_person_id()] = peep31
        peep32 = Person("@I32@")
        peep32.set_name("Charlie /Chaplin/")
        peep32.add_children_of_family("@F3@")
        self.peeps.individuals[peep32.get_person_id()] = peep32
        peep33 = Person("@I33@")
        peep33.set_name("Charlie /Chaplin/")
        peep33.add_children_of_family("@F3@")
        self.peeps.individuals[peep33.get_person_id()] = peep33
        peep34 = Person("@I34@")
        peep34.set_name("Charlie /Chaplin/")
        peep34.add_children_of_family("@F3@")
        self.peeps.individuals[peep34.get_person_id()] = peep34
        peep35 = Person("@I35@")
        peep35.set_name("Charlie /Chaplin/")
        peep35.add_children_of_family("@F3@")
        self.peeps.individuals[peep35.get_person_id()] = peep35
        peep36 = Person("@I36@")
        peep36.set_name("Charlie /Chaplin/")
        peep36.add_children_of_family("@F3@")
        self.peeps.individuals[peep36.get_person_id()] = peep36
        peep37 = Person("@I37@")
        peep37.set_name("Charlie /Chaplin/")
        peep37.add_children_of_family("@F3@")
        self.peeps.individuals[peep37.get_person_id()] = peep37
        peep38 = Person("@I38@")
        peep38.set_name("Charlie /Chaplin/")
        peep38.add_children_of_family("@F3@")
        self.peeps.individuals[peep38.get_person_id()] = peep38
        peep39 = Person("@I39@")
        peep39.set_name("Charlie /Chaplin/")
        peep39.add_children_of_family("@F3@")
        self.peeps.individuals[peep39.get_person_id()] = peep39
        fam3 = Family("@F3@")
        fam3.add_child(peep25.get_person_id())
        fam3.add_child(peep26.get_person_id())
        fam3.add_child(peep27.get_person_id())
        fam3.add_child(peep28.get_person_id())
        fam3.add_child(peep29.get_person_id())
        fam3.add_child(peep30.get_person_id())
        fam3.add_child(peep31.get_person_id())
        fam3.add_child(peep32.get_person_id())
        fam3.add_child(peep33.get_person_id())
        fam3.add_child(peep34.get_person_id())
        fam3.add_child(peep35.get_person_id())
        fam3.add_child(peep36.get_person_id())
        fam3.add_child(peep37.get_person_id())
        fam3.add_child(peep38.get_person_id())
        fam3.add_child(peep39.get_person_id())
        self.fam.families[fam3.get_family_id()] = fam3

        self.fam.validate()

        results = self.msgs.get_messages()

        self.assertEqual(1, len(results))
        err1 = {
            "error_id": "FAMILY",
            "user_story": "US15",
            "user_id": fam3.get_family_id(),
            "name": "NA",
            "message": "There should be fewer than 15 siblings in a family"
        }
        self.assertDictEqual(err1, results[0])

    def test_US22_validation_uniq_family_id(self):
        """US22: testing unique family ids
        look in people for unique people ids portion
        """
        fam_data = {
            "level": 0,
            "tag": "FAM",
            "args": "@F01@",
            "valid": "Y"
        }
        self.fam.process_line_data(fam_data)
        fam_data1 = {
            "level": 0,
            "tag": "FAM",
            "args": "@F01@",
            "valid": "Y"
        }
        self.fam.process_line_data(fam_data1)

    def test_us11_validation_no_bigamy(self):
        """US11: testing no bigamy
        """
        # Family 1 setup
        peep1 = Person("@I1@")
        peep1.set_name("Philip /Banks/")
        peep1.set_gender("M")
        peep1.set_date("17 AUG 1967", "birth")
        peep1.add_spouse_of_family("@F1@")
        peep1.add_spouse_of_family("@F2@")
        peep1.add_spouse_of_family("@F3@")
        self.peeps.individuals[peep1.get_person_id()] = peep1
        peep2 = Person("@I2@")
        peep2.set_name("Vivian /Banks/")
        peep2.set_gender("F")
        peep2.set_date("17 AUG 1970", "birth")
        peep2.set_date("17 JAN 1993", "death")
        peep2.add_spouse_of_family("@F1@")
        peep2.add_spouse_of_family("@F4@")
        self.peeps.individuals[peep2.get_person_id()] = peep2
        fam1 = Family("@F1@")
        fam1.set_husband_id(peep1.get_person_id())
        fam1.set_wife_id(peep2.get_person_id())
        fam1.set_date("20 SEP 1990", "married")
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup
        peep3 = Person("@I3@")
        peep3.set_name("Lily /Banks/")
        peep3.set_gender("F")
        peep3.set_date("20 AUG 1970", "birth")
        peep3.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep3.get_person_id()] = peep3
        fam2 = Family("@F2@")
        fam2.set_husband_id(peep1.get_person_id())
        fam2.set_wife_id(peep3.get_person_id())
        fam2.set_date("20 SEP 1994", "married")
        fam2.set_date("25 AUG 1996", "divorced")
        self.fam.families[fam2.get_family_id()] = fam2

        # Family 3 setup
        peep4 = Person("@I4@")
        peep4.set_name("Millie /Banks/")
        peep4.set_gender("F")
        peep4.set_date("20 AUG 1970", "birth")
        peep4.add_spouse_of_family("@F3@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        fam3 = Family("@F3@")
        fam3.set_husband_id(peep1.get_person_id())
        fam3.set_wife_id(peep4.get_person_id())
        fam3.set_date("20 SEP 1990", "married")
        self.fam.families[fam3.get_family_id()] = fam3

        # Family 4 setup
        peep5 = Person("@I5@")
        peep5.set_name("Mikey /Mild/")
        peep5.set_gender("M")
        peep5.set_date("20 AUG 1970", "birth")
        peep5.add_spouse_of_family("@F4@")
        peep5.add_spouse_of_family("@F5@")
        self.peeps.individuals[peep5.get_person_id()] = peep5
        fam4 = Family("@F4@")
        fam4.set_husband_id(peep5.get_person_id())
        fam4.set_wife_id(peep2.get_person_id())
        self.fam.families[fam4.get_family_id()] = fam4

        # Family 5 setup
        peep6 = Person("@I6@")
        peep6.set_name("Maura /Mild/")
        peep6.set_gender("F")
        peep6.set_date("21 AUG 1970", "birth")
        peep6.add_spouse_of_family("@F5@")
        self.peeps.individuals[peep6.get_person_id()] = peep6
        fam5 = Family("@F5@")
        fam5.set_husband_id(peep5.get_person_id())
        fam5.set_wife_id(peep6.get_person_id())
        self.fam.families[fam5.get_family_id()] = fam5

        # Family 6 setup
        peep7 = Person("@I7@")
        peep7.set_name("Freddy /Banks/")
        peep7.set_gender("M")
        peep7.set_date("17 AUG 1967", "birth")
        peep7.add_spouse_of_family("@F6@")
        peep7.add_spouse_of_family("@F7@")
        self.peeps.individuals[peep7.get_person_id()] = peep7
        peep8 = Person("@I8@")
        peep8.set_name("Carrie /Banks/")
        peep8.set_gender("F")
        peep8.set_date("17 AUG 1970", "birth")
        peep8.add_spouse_of_family("@F6@")
        self.peeps.individuals[peep8.get_person_id()] = peep8
        fam6 = Family("@F6@")
        fam6.set_husband_id(peep7.get_person_id())
        fam6.set_wife_id(peep8.get_person_id())
        fam6.set_date("20 OCT 1990", "married")
        fam6.set_date("29 OCT 1991", "divorced")
        self.fam.families[fam6.get_family_id()] = fam6

        # Family 7
        peep9 = Person("@I9@")
        peep9.set_name("Carrie /Banks/")
        peep9.set_gender("F")
        peep9.set_date("17 JAN 1970", "birth")
        peep9.add_spouse_of_family("@F7@")
        self.peeps.individuals[peep9.get_person_id()] = peep9
        fam7 = Family("@F7@")
        fam7.set_husband_id(peep7.get_person_id())
        fam7.set_wife_id(peep9.get_person_id())
        fam7.set_date("19 OCT 2000", "married")
        self.fam.families[fam7.get_family_id()] = fam7
        self.fam.validate()

        results = self.msgs.get_messages()
        self.assertEqual(5, len(results))
        err1 = {
            "error_id": "FAMILY",
            "user_story": "US11",
            "user_id": fam1.get_family_id(),
            "name": "NA",
            "message": "Bigamy for " + peep2.get_person_id() + " " +
                       peep2.get_name()
        }
        self.assertDictEqual(err1, results[0])
        err2 = {
            "error_id": "FAMILY",
            "user_story": "US11",
            "user_id": fam3.get_family_id(),
            "name": "NA",
            "message": "Bigamy for " + peep1.get_person_id() + " " +
                       peep1.get_name()
        }
        self.assertDictEqual(err2, results[1])
        err3 = {
            "error_id": "FAMILY",
            "user_story": "US11",
            "user_id": fam4.get_family_id(),
            "name": "NA",
            "message": "Bigamy for " + peep5.get_person_id() + " " +
                       peep5.get_name()
        }
        self.assertDictEqual(err3, results[2])
        err4 = {
            "error_id": "FAMILY",
            "user_story": "US11",
            "user_id": fam4.get_family_id(),
            "name": "NA",
            "message": "Bigamy for " + peep2.get_person_id() + " " +
                       peep2.get_name()
        }
        self.assertDictEqual(err4, results[3])
        err5 = {
            "error_id": "FAMILY",
            "user_story": "US11",
            "user_id": fam5.get_family_id(),
            "name": "NA",
            "message": "Bigamy for " + peep5.get_person_id() + " " +
                       peep5.get_name()
        }
        self.assertDictEqual(err5, results[4])

    def test_us32_print_multiple_births(self):
        """US32 print multiple births test
        """
        # family set up - 3 births at a time - valid
        peep24 = Person("@I24@")
        peep24.set_name("Buddy /Chaplin/")
        peep24.set_date("5 JAN 1970", "birth")
        peep24.add_children_of_family("@F1@")
        self.peeps.individuals[peep24.get_person_id()] = peep24
        peep25 = Person("@I25@")
        peep25.set_name("GreenDay /Chaplin/")
        peep25.set_date("1 JAN 1970", "birth")
        peep25.add_children_of_family("@F1@")
        self.peeps.individuals[peep25.get_person_id()] = peep25
        peep26 = Person("@I26@")
        peep26.set_name("Panic /Chaplin/")
        peep26.set_date("1 JAN 1970", "birth")
        peep26.add_children_of_family("@F1@")
        self.peeps.individuals[peep26.get_person_id()] = peep26
        peep27 = Person("@I27@")
        peep27.set_name("Maroon /Chaplin/")
        peep27.set_date("1 JAN 1970", "birth")
        peep27.add_children_of_family("@F1@")
        self.peeps.individuals[peep27.get_person_id()] = peep27
        fam1 = Family("@F1@")
        fam1.add_child(peep24.get_person_id())
        fam1.add_child(peep25.get_person_id())
        fam1.add_child(peep26.get_person_id())
        fam1.add_child(peep27.get_person_id())
        self.fam.families[fam1.get_family_id()] = fam1
        self.maxDiff = None
        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.fam.us32_print_multiple_births()
        sys.stdout = sys.__stdout__
        test_output = """Multiple Births
+-------+--------------------+-----------+---------------------+
|   ID  |        Name        | Family ID |       Birthday      |
+-------+--------------------+-----------+---------------------+
| @I25@ | GreenDay /Chaplin/ |    @F1@   | 1970-01-01 00:00:00 |
| @I26@ |  Panic /Chaplin/   |    @F1@   | 1970-01-01 00:00:00 |
| @I27@ |  Maroon /Chaplin/  |    @F1@   | 1970-01-01 00:00:00 |
+-------+--------------------+-----------+---------------------+
"""
        self.assertEqual(test_output, output.getvalue())

    def test_us14_fewer_than_5_siblings(self):
        """US14 No more than 5 siblings born in a multiple birth in a family
        """
        # family set up - 3 births at a time - valid
        peep25 = Person("@I25@")
        peep25.set_name("GreenDay /Chaplin/")
        peep25.set_date("1 JAN 1970", "birth")
        peep25.add_children_of_family("@F1@")
        self.peeps.individuals[peep25.get_person_id()] = peep25
        peep26 = Person("@I26@")
        peep26.set_name("Panic /Chaplin/")
        peep26.set_date("1 JAN 1970", "birth")
        peep26.add_children_of_family("@F1@")
        self.peeps.individuals[peep26.get_person_id()] = peep26
        peep27 = Person("@I27@")
        peep27.set_name("Maroon /Chaplin/")
        peep27.set_date("1 JAN 1970", "birth")
        peep27.add_children_of_family("@F1@")
        self.peeps.individuals[peep27.get_person_id()] = peep27
        fam1 = Family("@F1@")
        fam1.add_child(peep25.get_person_id())
        fam1.add_child(peep26.get_person_id())
        fam1.add_child(peep27.get_person_id())
        self.fam.families[fam1.get_family_id()] = fam1

        # family set up - 6 births at same time - invalid
        peep28 = Person("@I28@")
        peep28.set_name("Charlie1 /Chaplin/")
        peep28.set_date("1 JAN 1970", "birth")
        peep28.add_children_of_family("@F3@")
        self.peeps.individuals[peep28.get_person_id()] = peep28
        peep29 = Person("@I29@")
        peep29.set_name("Hugh2 /Chaplin/")
        peep29.set_date("1 JAN 1970", "birth")
        peep29.add_children_of_family("@F3@")
        self.peeps.individuals[peep29.get_person_id()] = peep29
        peep30 = Person("@I30@")
        peep30.set_name("Jacob3 /Chaplin/")
        peep30.set_date("1 JAN 1970", "birth")
        peep30.add_children_of_family("@F3@")
        self.peeps.individuals[peep30.get_person_id()] = peep30
        peep31 = Person("@I31@")
        peep31.set_name("William4 /Chaplin/")
        peep31.set_date("1 JAN 1970", "birth")
        peep31.add_children_of_family("@F3@")
        self.peeps.individuals[peep31.get_person_id()] = peep31
        peep32 = Person("@I32@")
        peep32.set_name("Coolie5 /Chaplin/")
        peep32.set_date("1 JAN 1970", "birth")
        peep32.add_children_of_family("@F3@")
        self.peeps.individuals[peep32.get_person_id()] = peep32
        peep33 = Person("@I33@")
        peep33.set_name("JackJack6 /Chaplin/")
        peep33.set_date("1 JAN 1970", "birth")
        peep33.add_children_of_family("@F3@")
        self.peeps.individuals[peep33.get_person_id()] = peep33

        fam3 = Family("@F3@")
        fam3.add_child(peep28.get_person_id())
        fam3.add_child(peep29.get_person_id())
        fam3.add_child(peep30.get_person_id())
        fam3.add_child(peep31.get_person_id())
        fam3.add_child(peep32.get_person_id())
        fam3.add_child(peep33.get_person_id())
        self.fam.families[fam3.get_family_id()] = fam3

        self.fam.validate()

        results = self.msgs.get_messages()
        self.assertEqual(1, len(results))
        err1 = {
            "error_id": "FAMILY",
            "user_story": "US14",
            "user_id": fam3.get_family_id(),
            "name": "NA",
            "message": "No more than five siblings should be born at the same time"
        }
        self.assertDictEqual(err1, results[0])

    def test_us12_validate_parents_not_too_old(self):
        # US12 Create a test family for each unit test
        test_family = Family("@F1@")
        test_family.set_husband_id("@I1@")
        test_family.set_wife_id("@I2@")
        test_family.set_date("1 JAN 1990", "married")
        test_family.add_child("@I3@")
        self.fam.families[test_family.get_family_id()] = test_family
        test_husband = Person("@I1@")
        test_husband.set_name("Tony /Tiger/")
        test_husband.set_gender("M")
        test_husband.set_date("1 JAN 1965", "birth")
        test_husband.add_spouse_of_family(test_family.get_family_id())
        self.peeps.individuals[test_husband.get_person_id()] = test_husband
        test_wife = Person("@I2@")
        test_wife.set_name("Minnie /Mouse/")
        test_wife.set_gender("F")
        test_wife.set_date("20 JUL 1966", "birth")
        test_wife.add_spouse_of_family(test_family.get_family_id())
        self.peeps.individuals[test_wife.get_person_id()] = test_wife
        test_child = Person("@I3@")
        test_child.set_name("Mickey /Mouse/")
        test_child.set_gender("M")
        test_child.set_date("20 NOV 1992", "birth")
        test_child.add_children_of_family(test_family.get_family_id())
        self.peeps.individuals[test_child.get_person_id()] = test_child
        """ US12: Test if parents are too old
        """
        test_family = self.fam.families["@F1@"]  # type: Family
        self.assertTrue(self.fam._us12_validate_parents_not_too_old(test_family))
        self.assertEqual(len(self.msgs._messages), 0)

        # type: Person
        husband = self.peeps.individuals[test_family.get_husband_id()]
        husband.set_date("17 AUG 1900", "birth")
        self.assertFalse(self.fam._us12_validate_parents_not_too_old(test_family))
        self.assertEqual(len(self.msgs.get_messages()), 1)

        # type: Person
        wife = self.peeps.individuals[test_family.get_wife_id()]
        husband.set_date("1 JAN 1965", "birth")
        wife.set_date("18 AUG 1900", "birth")
        self.assertFalse(self.fam._us12_validate_parents_not_too_old(test_family))
        self.assertEqual(len(self.msgs.get_messages()), 2)

    def test_us24_unique_families_by_spouses(self):
        """US24 No more than one family with the same spouses by name
        and the same marriage date should appear in a GEDCOM file.
        """
        # Family 1 setup - valid
        peep1 = Person("@I1@")
        peep1.set_name("Bob /Dole/")
        peep1.set_gender("M")
        peep1.add_spouse_of_family("@F1@")
        self.peeps.individuals[peep1.get_person_id()] = peep1
        peep2 = Person("@I2@")
        peep2.set_name("Sally /Fields/")
        peep2.set_gender("F")
        peep2.add_spouse_of_family("@F1@")
        self.peeps.individuals[peep2.get_person_id()] = peep2
        fam1 = Family("@F1@")
        fam1.set_husband_id(peep1.get_person_id())
        fam1.set_wife_id(peep2.get_person_id())
        fam1.set_date("1 Jun 2000", "married")
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup INVALID
        peep3 = Person("@I3@")
        peep3.set_name("Bob /Dole/")
        peep3.set_gender("M")
        peep3.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep3.get_person_id()] = peep3
        peep4 = Person("@I4@")
        peep4.set_name("Sally /Fields/")
        peep4.set_gender("F")
        peep4.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        fam2 = Family("@F2@")
        fam2.set_husband_id(peep3.get_person_id())
        fam2.set_wife_id(peep4.get_person_id())
        fam2.set_date("1 Jun 2000", "married")
        self.fam.families[fam2.get_family_id()] = fam2

        self.fam.validate()

        results = self.msgs.get_messages()

        self.assertEqual(1, len(results))
        err1 = {
            "error_id": Families.CLASS_IDENTIFIER,
            "user_story": "US24",
            "user_id": fam1.get_family_id(),
            "name": "NA",
            "message": "Duplicate families by spouse names and married date: " + fam2.get_family_id()
        }
        self.assertDictEqual(err1, results[0])

    def test_us21_correct_gender_role(self):
        """US21 Gender roles should correctly be assigned for husband and wife
        """
        # Family 1 setup - valid
        peep1 = Person("@I1@")
        peep1.set_name("Drake /Minaj/")
        peep1.set_gender("M")
        peep1.set_date("17 Jan 1980", "birth")
        peep1.add_spouse_of_family("@F1@")
        self.peeps.individuals[peep1.get_person_id()] = peep1
        peep2 = Person("@I2@")
        peep2.set_name("Cardi /Minaj/")
        peep2.set_gender("F")
        peep2.set_date("17 Dec 1980", "birth")
        peep2.set_date("20 Dec 2015", "death")
        peep2.add_spouse_of_family("@F1@")
        self.peeps.individuals[peep2.get_person_id()] = peep2
        fam1 = Family("@F1@")
        fam1.set_husband_id(peep1.get_person_id())
        fam1.set_wife_id(peep2.get_person_id())
        fam1.set_date("20 Jun 2000", "married")
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup INVALID
        peep3 = Person("@I3@")
        peep3.set_name("Travis /Jacobs/")
        peep3.set_gender("F")
        peep3.set_date("17 Jan 1980", "birth")
        peep3.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep3.get_person_id()] = peep3
        peep4 = Person("@I4@")
        peep4.set_name("Nicki /Jacobs/")
        peep4.set_gender("M")
        peep4.set_date("17 Dec 1980", "birth")
        peep4.set_date("20 Dec 2015", "death")
        peep4.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        fam2 = Family("@F2@")
        fam2.set_husband_id(peep3.get_person_id())
        fam2.set_wife_id(peep4.get_person_id())
        fam2.set_date("20 Jun 2000", "married")
        self.fam.families[fam2.get_family_id()] = fam2

        self.fam.validate()

        results = self.msgs.get_messages()
        self.assertEqual(2, len(results))
        err1 = {
            "error_id": "FAMILY",
            "user_story": "US21",
            "user_id": fam2.get_family_id(),
            "name": "NA",
            "message": "Father " + peep3.get_person_id() + " should be a Male"
        }
        self.assertDictEqual(err1, results[0])
        err2 = {
            "error_id": "FAMILY",
            "user_story": "US21",
            "user_id": fam2.get_family_id(),
            "name": "NA",
            "message": "Mother " + peep4.get_person_id() + " should be a Female"
        }
        self.assertDictEqual(err2, results[1])

    def test_us33_print_orphaned(self):
        """ US33 print orphaned list test
        """
        # no children
        test_family = Family("@F1@")
        test_family.set_husband_id("@I1@")
        test_family.set_wife_id("@I2@")
        self.fam.families[test_family.get_family_id()] = test_family
        test_husband = Person("@I1@")
        test_husband.set_name("Tony /Tiger/")
        test_husband.set_gender("M")
        test_husband.set_date("1 JAN 2017", "death")
        test_husband.add_spouse_of_family(test_family.get_family_id())
        self.peeps.individuals[test_husband.get_person_id()] = test_husband
        test_wife = Person("@I2@")
        test_wife.set_name("Minnie /Mouse/")
        test_wife.set_gender("F")
        test_wife.set_date("1 JAN 2017", "death")
        test_wife.add_spouse_of_family(test_family.get_family_id())
        self.peeps.individuals[test_wife.get_person_id()] = test_wife

        # 1 child
        test_family = Family("@F2@")
        test_family.set_husband_id("@I3@")
        test_family.set_wife_id("@I4@")
        test_family.add_child("@I5@")
        test_family.add_child("@I6@")
        test_family.add_child("@I7@")
        self.fam.families[test_family.get_family_id()] = test_family
        test_husband = Person("@I3@")
        test_husband.set_name("Sam /Tiger/")
        test_husband.set_gender("M")
        test_husband.set_date("1 JAN 2017", "death")
        test_husband.add_spouse_of_family(test_family.get_family_id())
        self.peeps.individuals[test_husband.get_person_id()] = test_husband
        test_wife = Person("@I4@")
        test_wife.set_name("Mary /Mouse/")
        test_wife.set_gender("F")
        test_wife.set_date("1 JAN 2017", "death")
        test_wife.add_spouse_of_family(test_family.get_family_id())
        self.peeps.individuals[test_wife.get_person_id()] = test_wife
        test_child = Person("@I5@")
        test_child.set_name("Bonnie /Mouse/")
        test_child.set_gender("F")
        test_child.set_date("1 JAN 2015", "birth")
        test_child.add_children_of_family(test_family.get_family_id())
        self.peeps.individuals[test_child.get_person_id()] = test_child
        test_child = Person("@I6@")
        test_child.set_name("David /Mouse/")
        test_child.set_gender("M")
        test_child.set_date("1 JAN 1990", "birth")
        test_child.add_children_of_family(test_family.get_family_id())
        self.peeps.individuals[test_child.get_person_id()] = test_child
        test_child = Person("@I7@")
        test_child.set_name("Doug /Mouse/")
        test_child.set_gender("M")
        test_child.set_date("1 JAN 2017", "death")
        test_child.add_children_of_family(test_family.get_family_id())
        self.peeps.individuals[test_child.get_person_id()] = test_child

        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.fam.us33_print_orphans()
        sys.stdout = sys.__stdout__
        test_output = """Orphans
+------+----------------+-----+
|  ID  |      Name      | Age |
+------+----------------+-----+
| @I5@ | Bonnie /Mouse/ |  2  |
+------+----------------+-----+
"""
        self.assertEqual(test_output, output.getvalue())

    def test_us30_print_married(self):
        """ US30 Unit tests
        """
        test_family = Family("@F1@")
        test_family.set_husband_id("@I1@")
        test_family.set_wife_id("@I2@")
        test_family.set_date("1 JAN 1990", "married")
        test_family.add_child("@I3@")
        self.fam.families[test_family.get_family_id()] = test_family
        test_husband = Person("@I1@")
        test_husband.set_name("Tony /Tiger/")
        test_husband.set_gender("M")
        test_husband.set_date("1 JAN 1965", "birth")
        test_husband.add_spouse_of_family(test_family.get_family_id())
        self.peeps.individuals[test_husband.get_person_id()] = test_husband
        test_wife = Person("@I2@")
        test_wife.set_name("Minnie /Mouse/")
        test_wife.set_gender("F")
        test_wife.set_date("20 JUL 1966", "birth")
        test_wife.add_spouse_of_family(test_family.get_family_id())
        self.peeps.individuals[test_wife.get_person_id()] = test_wife

        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.fam.us30_print_married()
        sys.stdout = sys.__stdout__
        test_output = """Married Individuals
+------+----------------+---------+
|  ID  |      Name      | Married |
+------+----------------+---------+
| @I1@ |  Tony /Tiger/  |   True  |
| @I2@ | Minnie /Mouse/ |   True  |
+------+----------------+---------+
"""
        self.assertEqual(test_output, output.getvalue())

    def test_print_upcoming_anniversaries(self):
        """ US39 Unit tests
        """
        test_family = Family("@F1@")
        test_family.set_husband_id("@I1@")
        test_family.set_wife_id("@I2@")
        test_family.set_date("1 DEC 1990", "married")
        test_family.add_child("@I3@")
        self.fam.families[test_family.get_family_id()] = test_family
        test_husband = Person("@I1@")
        test_husband.set_name("Tony /Tiger/")
        test_husband.set_gender("M")
        test_husband.set_date("1 JAN 1965", "birth")
        test_husband.add_spouse_of_family(test_family.get_family_id())
        self.peeps.individuals[test_husband.get_person_id()] = test_husband
        test_wife = Person("@I2@")
        test_wife.set_name("Minnie /Mouse/")
        test_wife.set_gender("F")
        test_wife.set_date("20 JUL 1966", "birth")
        test_wife.add_spouse_of_family(test_family.get_family_id())
        self.peeps.individuals[test_wife.get_person_id()] = test_wife

        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.fam.print_upcoming_anniversaries()
        sys.stdout = sys.__stdout__
        test_output = """Upcoming Anniversaries
+------+--------------+----------------+---------------------+
|  ID  |   Husband    |      Wife      |     Anniversary     |
+------+--------------+----------------+---------------------+
| @F1@ | Tony /Tiger/ | Minnie /Mouse/ | 1990-12-01 00:00:00 |
+------+--------------+----------------+---------------------+
"""
        self.assertEqual(test_output, output.getvalue())