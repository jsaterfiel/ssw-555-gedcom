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

    def test_validation_marriage_before_death(self):
        """US05: testing that a marriage occurred before death
        """
        # Family 1 setup (married before death)
        peep1 = Person("@I01@")
        peep1.set_name("Bob /Saget/")
        peep1.set_gender("M")
        peep1.set_birth_date("17 AUG 1987")
        peep1.add_spouse_of_family("@F01@")

        self.peeps.individuals[peep1.get_person_id()] = peep1

        peep2 = Person("@I01@")
        peep2.set_name("Bob /Saget/")
        peep2.set_gender("F")
        peep2.set_birth_date("17 AUG 1990")
        peep2.set_death_date("17 JAN 2014")
        peep2.add_spouse_of_family("@F01@")

        self.peeps.individuals[peep2.get_person_id()] = peep2

        fam1 = Family("@F01@")
        fam1.set_husband_id(peep1.get_person_id())
        fam1.set_wife_id(peep2.get_person_id())
        fam1.set_married_date("10 FEB 2012")

        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup (married after death) FAILURE
        peep3 = Person("@I03@")
        peep3.set_name("Bob /Hope/")
        peep3.set_gender("M")
        peep3.set_birth_date("17 AUG 1987")
        peep3.set_death_date("17 JAN 2010")
        peep3.add_spouse_of_family("@F02@")
        self.peeps.individuals[peep3.get_person_id()] = peep3
        peep4 = Person("@I04@")
        peep4.set_name("Betty /White/")
        peep4.set_gender("F")
        peep4.set_birth_date("17 AUG 1990")
        peep4.add_spouse_of_family("@F02@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        fam2 = Family("@F02@")
        fam2.set_husband_id(peep3.get_person_id())
        fam2.set_wife_id(peep4.get_person_id())
        fam2.set_married_date("10 FEB 2012")
        self.fam.families[fam2.get_family_id()] = fam2

        # Family 3 setup (both alive)
        peep5 = Person("@I05@")
        peep5.set_name("Sammy /Davis jr./")
        peep5.set_gender("M")
        peep5.set_birth_date("17 AUG 1990")
        peep5.add_spouse_of_family("@F03@")
        self.peeps.individuals[peep5.get_person_id()] = peep5
        peep6 = Person("@I06@")
        peep6.set_gender("F")
        peep6.set_name("Tina /Turner/")
        peep6.set_birth_date("17 AUG 1990")
        peep6.add_spouse_of_family("@F03@")
        self.peeps.individuals[peep6.get_person_id()] = peep6
        fam3 = Family("@F03@")
        fam3.set_husband_id(peep5.get_person_id())
        fam3.set_wife_id(peep6.get_person_id())
        fam3.set_married_date("10 FEB 2012")
        self.fam.families[fam3.get_family_id()] = fam3

        # Family 4 setup (both dead before marriage) DOUBLE FAILURE
        peep7 = Person("@I07@")
        peep7.set_name("Paris /Troy/")
        peep7.set_gender("M")
        peep7.set_birth_date("17 AUG 1990")
        peep7.set_death_date("17 AUG 2011")
        peep7.add_spouse_of_family("@F04@")
        self.peeps.individuals[peep7.get_person_id()] = peep7
        peep8 = Person("@I08@")
        peep8.set_name("Helena /Troy/")
        peep8.set_gender("F")
        peep8.set_birth_date("17 AUG 1990")
        peep8.set_death_date("17 AUG 2010")
        peep8.add_spouse_of_family("@F04@")
        self.peeps.individuals[peep8.get_person_id()] = peep8
        fam4 = Family("@F04@")
        fam4.set_husband_id(peep7.get_person_id())
        fam4.set_wife_id(peep8.get_person_id())
        fam4.set_married_date("10 FEB 2012")
        self.fam.families[fam4.get_family_id()] = fam4

        # Family 5 setup no married date
        peep9 = Person("@I09@")
        peep9.set_name("Paris /Troy/")
        peep9.set_gender("M")
        peep9.set_birth_date("17 AUG 1990")
        peep9.set_death_date("17 AUG 2011")
        peep9.add_spouse_of_family("@F05@")
        self.peeps.individuals[peep9.get_person_id()] = peep9
        peep10 = Person("@I10@")
        peep10.set_name("Helena /Troy/")
        peep10.set_gender("F")
        peep10.set_birth_date("17 AUG 1990")
        peep10.set_death_date("17 AUG 2010")
        peep10.add_spouse_of_family("@F05@")
        self.peeps.individuals[peep10.get_person_id()] = peep10
        fam5 = Family("@F05@")
        fam5.set_husband_id(peep9.get_person_id())
        fam5.set_wife_id(peep10.get_person_id())
        self.fam.families[fam5.get_family_id()] = fam5

        # Family 6 setup (no spouses)
        fam6 = Family("@F06@")
        fam6.set_married_date("10 FEB 2012")
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

    def test_validation_divorce_before_death(self):
        """US06: testing that a divorce occurred before death
        """
        # Family 1 setup (divorced before death)
        peep1 = Person("@I01@")
        peep1.set_name("Bob /Saget/")
        peep1.set_gender("M")
        peep1.set_birth_date("17 AUG 1987")
        peep1.add_spouse_of_family("@F01@")
        self.peeps.individuals[peep1.get_person_id()] = peep1
        peep2 = Person("@I02@")
        peep2.set_name("Marylin /Monroe/")
        peep2.set_gender("F")
        peep2.set_birth_date("17 AUG 1990")
        peep2.set_death_date("17 JAN 2014")
        peep2.add_spouse_of_family("@F01@")
        self.peeps.individuals[peep2.get_person_id()] = peep2
        fam1 = Family("@F06@")
        fam1.set_husband_id(peep1.get_person_id())
        fam1.set_wife_id(peep2.get_person_id())
        fam1.set_married_date("10 FEB 2011")
        fam1.set_divorced_date("11 FEB 2012")
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup (divorced after death) FAILURE
        peep3 = Person("@I03@")
        peep3.set_name("Bob /Hope/")
        peep3.set_gender("M")
        peep3.set_birth_date("17 AUG 1987")
        peep3.set_death_date("17 JAN 2010")
        peep3.add_spouse_of_family("@F02@")
        self.peeps.individuals[peep3.get_person_id()] = peep3
        peep4 = Person("@I04@")
        peep4.set_name("Betty /White/")
        peep4.set_gender("F")
        peep4.set_birth_date("17 AUG 1980")
        peep4.set_death_date("17 JAN 2014")
        peep4.add_spouse_of_family("@F02@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        fam2 = Family("@F02@")
        fam2.set_husband_id(peep3.get_person_id())
        fam2.set_wife_id(peep4.get_person_id())
        fam2.set_married_date("10 FEB 2009")
        fam2.set_divorced_date("11 FEB 2012")
        self.fam.families[fam2.get_family_id()] = fam2

        # Family 3 setup (both alive)
        peep5 = Person("@I05@")
        peep5.set_name("Sammy /Davis jr./")
        peep5.set_gender("M")
        peep5.set_birth_date("17 AUG 1990")
        peep5.add_spouse_of_family("@F03@")
        self.peeps.individuals[peep5.get_person_id()] = peep5
        peep6 = Person("@I06@")
        peep6.set_name("Sammy /Davis jr./")
        peep6.set_gender("F")
        peep6.set_birth_date("17 AUG 1990")
        peep6.add_spouse_of_family("@F03@")
        self.peeps.individuals[peep6.get_person_id()] = peep6
        fam3 = Family("@F03@")
        fam3.set_husband_id(peep5.get_person_id())
        fam3.set_wife_id(peep6.get_person_id())
        fam3.set_married_date("10 FEB 2012")
        fam3.set_divorced_date("10 FEB 2014")
        self.fam.families[fam3.get_family_id()] = fam3

        # Family 4 setup (both dead before divorce) DOUBLE FAILURE
        peep7 = Person("@I07@")
        peep7.set_name("Paris /Troy/")
        peep7.set_gender("M")
        peep7.set_birth_date("17 AUG 1980")
        peep7.set_death_date("17 AUG 2011")
        peep7.add_spouse_of_family("@F04@")
        self.peeps.individuals[peep7.get_person_id()] = peep7
        peep8 = Person("@I08@")
        peep8.set_name("Helena /Troy/")
        peep8.set_gender("F")
        peep8.set_birth_date("17 AUG 1980")
        peep8.set_death_date("17 AUG 2010")
        peep8.add_spouse_of_family("@F04@")
        self.peeps.individuals[peep8.get_person_id()] = peep8
        fam4 = Family("@F04@")
        fam4.set_husband_id(peep7.get_person_id())
        fam4.set_wife_id(peep8.get_person_id())
        fam4.set_married_date("10 FEB 2009")
        fam4.set_divorced_date("11 FEB 2015")
        self.fam.families[fam4.get_family_id()] = fam4

        # Family 5 setup no divorced date
        peep9 = Person("@I09@")
        peep9.set_name("Paris /Troy/")
        peep9.set_gender("M")
        peep9.set_birth_date("17 AUG 1980")
        peep9.set_death_date("17 AUG 2011")
        peep9.add_spouse_of_family("@F05@")
        self.peeps.individuals[peep9.get_person_id()] = peep9
        peep10 = Person("@I10@")
        peep10.set_name("Helena /Troy/")
        peep10.set_gender("F")
        peep10.set_birth_date("17 AUG 1980")
        peep10.set_death_date("17 AUG 2010")
        peep10.add_spouse_of_family("@F05@")
        self.peeps.individuals[peep10.get_person_id()] = peep10
        fam5 = Family("@F05@")
        fam5.set_husband_id(peep9.get_person_id())
        fam5.set_wife_id(peep10.get_person_id())
        self.fam.families[fam5.get_family_id()] = fam5

        # Family 6 setup (no spouses)
        fam6 = Family("@F05@")
        fam6.set_married_date("10 FEB 2012")
        fam6.set_divorced_date("10 FEB 2013")
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

    def test_is_valid_married_date(self):
        """ US02: is marriage valid
        """
        # Family 1 invalid married date
        fam1 = Family("@F1@")
        fam1.set_husband_id("@I1@")
        fam1.set_wife_id("@I2@")
        fam1.set_married_date("1 JAN 1960")
        self.fam.families[fam1.get_family_id()] = fam1
        peep1 = Person("@I1@")
        peep1.set_name("Tony /Tiger/")
        peep1.set_gender("M")
        peep1.set_birth_date("1 JAN 1970")
        peep1.add_spouse_of_family(fam1.get_family_id())
        self.peeps.individuals[peep1.get_person_id()] = peep1
        peep2 = Person("@I2@")
        peep2.set_name("Minnie /Mouse/")
        peep2.set_gender("F")
        peep2.set_birth_date("20 JUL 1970")
        peep2.add_spouse_of_family(fam1.get_family_id())
        self.peeps.individuals[peep2.get_person_id()] = peep2

        # Family 2 valid married date
        fam2 = Family("@F2@")
        fam2.set_husband_id("@I3@")
        fam2.set_wife_id("@I4@")
        fam2.set_married_date("1 JAN 1990")
        self.fam.families[fam2.get_family_id()] = fam2
        peep3 = Person("@I3@")
        peep3.set_name("Bob /Tiger/")
        peep3.set_gender("M")
        peep3.set_birth_date("1 JAN 1970")
        peep3.add_spouse_of_family(fam2.get_family_id())
        self.peeps.individuals[peep3.get_person_id()] = peep3
        peep4 = Person("@I4@")
        peep4.set_name("Sally /Mouse/")
        peep4.set_gender("F")
        peep4.set_birth_date("20 JUL 1970")
        peep4.add_spouse_of_family(fam2.get_family_id())
        self.peeps.individuals[peep4.get_person_id()] = peep4

        self.fam.validate()
        results = self.msgs.get_messages()

        self.assertEqual(1, len(results))
        err1 = {
            "error_id": "INDIVIDUAL",
            "user_story": "US02",
            "user_id": peep1.get_person_id(),
            "name": peep1.get_name(),
            "message": "Birth date should occur before marriage of an individual"
        }
        self.assertDictEqual(err1, results[0])

    def test_validation_marriage_before_divorce(self):
        """US04: testing that marriage occurred before divorce
        """
        # Family 1 setup (married before divorced) Pass
        fam1 = Family("@F01@")
        fam1.set_married_date("10 FEB 1980")
        fam1.set_divorced_date("11 FEB 2015")
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup (married after divorced) FAILURE
        fam2 = Family("@F02@")
        fam2.set_married_date("10 FEB 2015")
        fam2.set_divorced_date("10 FEB 2011")
        self.fam.families[fam2.get_family_id()] = fam2

        # Family 3 setup (married before divorced) Failure
        fam3 = Family("@F03@")
        fam3.set_married_date("10 FEB 2016")
        fam3.set_divorced_date("11 FEB 2015")
        self.fam.families[fam3.get_family_id()] = fam3

        # Family 4 setup (marriage after divorce for two previously married individuals) Failure
        fam4 = Family("@F04@")
        fam4.set_married_date("10 FEB 2017")
        fam4.set_divorced_date("11 FEB 2015")
        self.fam.families[fam4.get_family_id()] = fam4

        # Family 5 setup
        fam5 = Family("@F05@")
        fam5.set_married_date("10 FEB 2013")
        fam5.set_divorced_date("11 FEB 2012")
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

    def test_validation_marriage_and_divorce_before_current(self):
        """US01: testing that marriage and divorce dates occurred before current date
        """
        curr = datetime.now()

        # Family 1 setup (married before current) pass
        fam1 = Family("@F03@")
        fam1.set_married_date("19 MAY 1991")
        self.fam.families[fam1.get_family_id()] = fam1

        # Family 2 setup (married after current) fail
        fam2invalid = Family("@F01@")
        fam2invalid.set_married_date("4 OCT " + str(curr.year + 4))
        self.fam.families[fam2invalid.get_family_id()] = fam2invalid

        # Family 3 setup (divorced after current) fail
        fam3invalid = Family("@F02@")
        fam3invalid.set_married_date("6 MAY 1952")
        fam3invalid.set_divorced_date("6 NOV " + str(curr.year + 2))
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

    def test_validation_child_before_parent_death(self):
        """US09: testing that a child birth occurred before parent death
        """
        # Family 1 setup (child 5ish years before mom death) Valid
        peep1 = Person("@I1@")
        peep1.set_name("Philip /Banks/")
        peep1.set_gender("M")
        peep1.set_birth_date("17 AUG 1987")
        peep1.add_spouse_of_family("@F1@")
        self.peeps.individuals[peep1.get_person_id()] = peep1
        peep2 = Person("@I2@")
        peep2.set_name("Vivian /Banks/")
        peep2.set_gender("F")
        peep2.set_birth_date("17 AUG 1990")
        peep2.set_death_date("17 JAN 2014")
        peep2.add_spouse_of_family("@F1@")
        self.peeps.individuals[peep2.get_person_id()] = peep2
        peep3 = Person("@I3@")
        peep3.set_name("Fresh /Prince/")
        peep3.set_gender("M")
        peep3.set_birth_date("17 AUG 2009")
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
        peep4.set_birth_date("17 AUG 1987")
        peep4.set_death_date("17 SEP 2014")
        peep4.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep4.get_person_id()] = peep4
        peep5 = Person("@I5@")
        peep5.set_gender("F")
        peep5.set_name("Pattie /Mayonaise/")
        peep5.set_birth_date("17 AUG 1990")
        peep5.add_spouse_of_family("@F2@")
        self.peeps.individuals[peep5.get_person_id()] = peep5
        peep6 = Person("@I6@")
        peep6.set_gender("F")
        peep6.set_name("Frankie /Funnie/")
        peep6.set_birth_date("17 AUG 2009")
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
        peep7.set_birth_date("17 AUG 1987")
        peep7.set_death_date("17 SEP 2014")
        peep7.add_spouse_of_family("@F3@")
        self.peeps.individuals[peep7.get_person_id()] = peep7
        peep8 = Person("@I8@")
        peep8.set_gender("F")
        peep8.set_name("Margarita /Daniels/")
        peep8.set_birth_date("17 AUG 1990")
        peep8.add_spouse_of_family("@F3@")
        self.peeps.individuals[peep8.get_person_id()] = peep8
        peep9 = Person("@I9@")
        peep9.set_gender("M")
        peep9.set_name("Whiskey /Daniels/")
        peep9.set_birth_date("17 AUG 2016")
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
        peep10.set_birth_date("17 AUG 1987")
        peep10.set_death_date("17 SEP 2014")
        peep10.add_spouse_of_family("@F4@")
        self.peeps.individuals[peep10.get_person_id()] = peep10
        peep11 = Person("@I11@")
        peep11.set_name("Lorraine /McFly/")
        peep11.set_gender("F")
        peep11.set_birth_date("17 AUG 1990")
        peep11.add_spouse_of_family("@F4@")
        self.peeps.individuals[peep11.get_person_id()] = peep11
        peep12 = Person("@I12@")
        peep12.set_gender("M")
        peep12.set_name("Marty /McFly/")
        peep12.set_birth_date("17 DEC 2013")
        peep12.add_children_of_family("@F4@")
        self.peeps.individuals[peep12.get_person_id()] = peep12
        fam4 = Family("@F4@")
        fam4.set_husband_id(peep12.get_person_id())
        fam4.set_wife_id(peep10.get_person_id())
        fam4.add_child(peep11.get_person_id())
        self.fam.families[fam4.get_family_id()] = fam4

        # Family 5 setup (child 9 months and some days but same month before dad death) Invalid
        peep13 = Person("@I13@")
        peep13.set_name("Homer /Simpson/")
        peep13.set_gender("M")
        peep13.set_birth_date("17 AUG 1987")
        peep13.set_death_date("17 SEP 2014")
        peep13.add_spouse_of_family("@F5@")
        self.peeps.individuals[peep13.get_person_id()] = peep13
        peep14 = Person("@I14@")
        peep14.set_name("Marge /Simpson/")
        peep14.set_gender("F")
        peep14.set_birth_date("17 AUG 1990")
        peep14.add_spouse_of_family("@F5@")
        self.peeps.individuals[peep14.get_person_id()] = peep14
        peep15 = Person("@I15@")
        peep15.set_gender("M")
        peep15.set_name("Bart /Simpson/")
        peep15.set_birth_date("1 JAN 2014")
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
        peep19.set_birth_date("17 AUG 1987")
        peep19.set_death_date("17 SEP 2014")
        peep19.add_spouse_of_family("@F6@")
        self.peeps.individuals[peep19.get_person_id()] = peep19
        peep20 = Person("@I20@")
        peep20.set_name("Roseanne /Conner/")
        peep20.set_gender("F")
        peep20.set_birth_date("17 AUG 1990")
        peep20.add_spouse_of_family("@F6@")
        self.peeps.individuals[peep20.get_person_id()] = peep20
        peep21 = Person("@I21@")
        peep21.set_gender("F")
        peep21.set_name("Becky /Conner/")
        peep21.set_birth_date("29 NOV 2013")
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
        peep22.set_birth_date("17 AUG 1987")
        peep22.add_spouse_of_family("@F7@")
        self.peeps.individuals[peep22.get_person_id()] = peep22
        peep23 = Person("@I23@")
        peep23.set_name("Harriette /Winslow/")
        peep23.set_gender("F")
        peep23.set_birth_date("17 AUG 1990")
        peep23.set_death_date("17 AUG 2016")
        peep23.add_spouse_of_family("@F7@")
        self.peeps.individuals[peep23.get_person_id()] = peep23
        peep24 = Person("@I24@")
        peep24.set_name("Laura /Winslow/")
        peep24.set_gender("F")
        peep24.set_birth_date("1 SEP 2016")
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
        peep25.set_birth_date("17 AUG 1987")
        peep25.set_death_date("20 OCT 2014")
        peep25.add_spouse_of_family("@F8@")
        self.peeps.individuals[peep25.get_person_id()] = peep25
        peep26 = Person("@I26@")
        peep26.set_name("Skyler /White/")
        peep26.set_gender("F")
        peep26.set_birth_date("17 AUG 1990")
        peep26.set_death_date("20 OCT 2014")
        peep26.add_spouse_of_family("@F8@")
        self.peeps.individuals[peep26.get_person_id()] = peep26
        peep27 = Person("@I27@")
        peep27.set_name("Walter Jr /White/")
        peep27.set_gender("M")
        peep27.set_birth_date("1 SEP 2016")
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
