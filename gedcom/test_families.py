"""Test cases for families module
"""
import unittest
import io
import sys
from datetime import datetime
from families import Families
from people import People
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
        test_fam = {
            "id": data["args"]
        }
        self.assertDictContainsSubset(
            test_fam, self.fam.families[data["args"]])

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
        test_fam1 = {
            "id": fam1["args"]
        }
        self.assertDictContainsSubset(
            test_fam1, self.fam.families[fam1["args"]])
        test_fam2 = {
            "id": fam2["args"]
        }
        self.assertDictContainsSubset(
            test_fam2, self.fam.families[fam2["args"]])

    def test_detect_married_tag(self):
        """test cases for detecting if the family is married
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
        data = {
            "level": 1,
            "tag": "MARR",
            "args": "",
            "valid": "Y"
        }
        self.fam.process_line_data(data)
        # ensure the marrage is recorded for the family we added
        self.assertTrue(self.fam.families["@F6@"]["married"])

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
            date_obj, self.fam.families[data["args"]]["married_date"])

    def test_detect_divorced_tag(self):
        """test cases for detecting if the family is divorced
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
        data = {
            "level": 1,
            "tag": "DIV",
            "args": "",
            "valid": "Y"
        }
        self.fam.process_line_data(data)
        # ensure the marrage is recorded for the family we added
        self.assertTrue(self.fam.families["@F6@"]["divorced"])

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
            date_obj, self.fam.families[data["args"]]["divorced_date"])

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
            husband_data["args"], self.fam.families[fam_data["args"]]["husband_id"])

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
            wife_data["args"], self.fam.families[fam_data["args"]]["wife_id"])

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
            1, len(self.fam.families[fam_data["args"]]["children"]))
        self.assertEqual(
            child_data["args"], self.fam.families[fam_data["args"]]["children"][0])

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
            2, len(self.fam.families[fam_data["args"]]["children"]))
        self.assertEqual(
            child1_data["args"], self.fam.families[fam_data["args"]]["children"][0])
        self.assertEqual(
            child2_data["args"], self.fam.families[fam_data["args"]]["children"][1])

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
        peep1 = {
            "id": "@I01@",
            "name": "Bob /Saget/",
            "gender": "M",
            "is_alive": True,
            "birth_date": datetime(1987, 8, 17, 0, 0, 0),
            "death_date": None,
            "child_of_families": [],
            "spouse_of_families": ["@F01@"],
            "age": 30
        }
        self.peeps.individuals[peep1["id"]] = peep1
        peep2 = {
            "id": "@I02@",
            "gender": "F",
            "name": "Marylin /Monroe/",
            "is_alive": False,
            "birth_date": datetime(1990, 8, 17, 0, 0, 0),
            "death_date": datetime(2014, 1, 17, 0, 0, 0),
            "child_of_families": [],
            "spouse_of_families": ["@F01@"],
            "age": 23
        }
        self.peeps.individuals[peep2["id"]] = peep2
        fam1 = {
            "id": "@F01@",
            "children": [],
            "husband_id": peep1["id"],
            "wife_id": peep2["id"],
            "married_date": datetime(2012, 2, 10, 0, 0, 0),
            "divorced_date": None
        }
        self.fam.families[fam1["id"]] = fam1
        # Family 2 setup (married after death) FAILURE
        peep3 = {
            "id": "@I03@",
            "name": "Bob /Hope/",
            "gender": "M",
            "is_alive": True,
            "birth_date": datetime(1987, 8, 17, 0, 0, 0),
            "death_date": datetime(2010, 1, 17, 0, 0, 0),
            "child_of_families": [],
            "spouse_of_families": ["@F02@"],
            "age": 23
        }
        self.peeps.individuals[peep3["id"]] = peep3
        peep4 = {
            "id": "@I04@",
            "gender": "F",
            "name": "Betty /White/",
            "is_alive": True,
            "birth_date": datetime(1990, 8, 17, 0, 0, 0),
            "death_date": None,
            "child_of_families": [],
            "spouse_of_families": ["@F02@"],
            "age": 27
        }
        self.peeps.individuals[peep4["id"]] = peep4
        fam2 = {
            "id": "@F02@",
            "children": [],
            "husband_id": peep3["id"],
            "wife_id": peep4["id"],
            "married_date": datetime(2012, 2, 10, 0, 0, 0),
            "divorced_date": None
        }
        self.fam.families[fam2["id"]] = fam2
        # Family 3 setup (both alive)
        peep5 = {
            "id": "@I05@",
            "name": "Sammy /Davis jr./",
            "gender": "M",
            "is_alive": True,
            "birth_date": datetime(1990, 8, 17, 0, 0, 0),
            "death_date": None,
            "child_of_families": [],
            "spouse_of_families": ["@F03@"],
            "age": 27
        }
        self.peeps.individuals[peep5["id"]] = peep5
        peep6 = {
            "id": "@I06@",
            "gender": "F",
            "name": "Tina /Turner/",
            "is_alive": True,
            "birth_date": datetime(1990, 8, 17, 0, 0, 0),
            "death_date": None,
            "child_of_families": [],
            "spouse_of_families": ["@F03@"],
            "age": 27
        }
        self.peeps.individuals[peep6["id"]] = peep6
        fam3 = {
            "id": "@F03@",
            "children": [],
            "husband_id": peep5["id"],
            "wife_id": peep6["id"],
            "married_date": datetime(2012, 2, 10, 0, 0, 0),
            "divorced_date": None
        }
        self.fam.families[fam3["id"]] = fam3
        # Family 4 setup (both dead before marriage) DOUBLE FAILURE
        peep7 = {
            "id": "@I07@",
            "name": "Paris /Troy/",
            "gender": "M",
            "is_alive": True,
            "birth_date": datetime(1990, 8, 17, 0, 0, 0),
            "death_date": datetime(2011, 8, 17, 0, 0, 0),
            "child_of_families": [],
            "spouse_of_families": ["@F04@"],
            "age": 21
        }
        self.peeps.individuals[peep7["id"]] = peep7
        peep8 = {
            "id": "@I08@",
            "gender": "F",
            "name": "Helena /Troy/",
            "is_alive": False,
            "birth_date": datetime(1990, 8, 17, 0, 0, 0),
            "death_date": datetime(2010, 8, 17, 0, 0, 0),
            "child_of_families": [],
            "spouse_of_families": ["@F04@"],
            "age": 20
        }
        self.peeps.individuals[peep8["id"]] = peep8
        fam4 = {
            "id": "@F04@",
            "children": [],
            "husband_id": peep7["id"],
            "wife_id": peep8["id"],
            "married_date": datetime(2012, 2, 10, 0, 0, 0),
            "divorced_date": None
        }
        self.fam.families[fam4["id"]] = fam4
        # Family 5 setup no married date
        peep9 = {
            "id": "@I09@",
            "name": "Paris /Troy/",
            "gender": "M",
            "is_alive": True,
            "birth_date": datetime(1990, 8, 17, 0, 0, 0),
            "death_date": datetime(2011, 8, 17, 0, 0, 0),
            "child_of_families": [],
            "spouse_of_families": ["@F04@"],
            "age": 21
        }
        self.peeps.individuals[peep9["id"]] = peep9
        peep10 = {
            "id": "@I10@",
            "gender": "F",
            "name": "Helena /Troy/",
            "is_alive": False,
            "birth_date": datetime(1990, 8, 17, 0, 0, 0),
            "death_date": datetime(2010, 8, 17, 0, 0, 0),
            "child_of_families": [],
            "spouse_of_families": ["@F05@"],
            "age": 20
        }
        self.peeps.individuals[peep10["id"]] = peep10
        fam5 = {
            "id": "@F05@",
            "children": [],
            "husband_id": peep7["id"],
            "wife_id": peep8["id"],
            "married_date": None,
            "divorced_date": None
        }
        self.fam.families[fam5["id"]] = fam5
        # Family 6 setup (no spouses)
        fam6 = {
            "id": "@F06@",
            "children": [],
            "husband_id": None,
            "wife_id": None,
            "married_date": datetime(2012, 2, 10, 0, 0, 0),
            "divorced_date": None
        }
        self.fam.families[fam6["id"]] = fam6

        self.fam.validate()

        results = self.msgs.get_messages()

        self.assertEqual(3, len(results))
        err1 = {
            "error_id": "FAMILY",
            "user_story": "US05",
            "user_id": fam2["id"],
            "name": "NA",
            "message": "marriage after death for " + peep3["id"] + " " + peep3["name"]
        }
        self.assertDictEqual(err1, results[0])
        err2 = {
            "error_id": "FAMILY",
            "user_story": "US05",
            "user_id": fam4["id"],
            "name": "NA",
            "message": "marriage after death for " + peep7["id"] + " " + peep7["name"]
        }
        self.assertDictEqual(err2, results[1])
        err3 = {
            "error_id": "FAMILY",
            "user_story": "US05",
            "user_id": fam4["id"],
            "name": "NA",
            "message": "marriage after death for " + peep8["id"] + " " + peep8["name"]
        }
        self.assertDictEqual(err3, results[2])

    def test_validation_divorce_before_death(self):
        """US05: testing that a divorce occurred before death
        """
        # Family 1 setup (divorced before death)
        peep1 = {
            "id": "@I01@",
            "name": "Bob /Saget/",
            "gender": "M",
            "is_alive": True,
            "birth_date": datetime(1987, 8, 17, 0, 0, 0),
            "death_date": None,
            "child_of_families": [],
            "spouse_of_families": ["@F01@"],
            "age": 30
        }
        self.peeps.individuals[peep1["id"]] = peep1
        peep2 = {
            "id": "@I02@",
            "gender": "F",
            "name": "Marylin /Monroe/",
            "is_alive": False,
            "birth_date": datetime(1990, 8, 17, 0, 0, 0),
            "death_date": datetime(2014, 1, 17, 0, 0, 0),
            "child_of_families": [],
            "spouse_of_families": ["@F01@"],
            "age": 23
        }
        self.peeps.individuals[peep2["id"]] = peep2
        fam1 = {
            "id": "@F01@",
            "children": [],
            "husband_id": peep1["id"],
            "wife_id": peep2["id"],
            "married_date": datetime(2011, 2, 10, 0, 0, 0),
            "divorced_date": datetime(2012, 2, 11, 0, 0, 0)
        }
        self.fam.families[fam1["id"]] = fam1
        # Family 2 setup (divorced after death) FAILURE
        peep3 = {
            "id": "@I03@",
            "name": "Bob /Hope/",
            "gender": "M",
            "is_alive": True,
            "birth_date": datetime(1987, 8, 17, 0, 0, 0),
            "death_date": datetime(2010, 1, 17, 0, 0, 0),
            "child_of_families": [],
            "spouse_of_families": ["@F02@"],
            "age": 23
        }
        self.peeps.individuals[peep3["id"]] = peep3
        peep4 = {
            "id": "@I04@",
            "gender": "F",
            "name": "Betty /White/",
            "is_alive": True,
            "birth_date": datetime(1980, 8, 17, 0, 0, 0),
            "death_date": None,
            "child_of_families": [],
            "spouse_of_families": ["@F02@"],
            "age": 27
        }
        self.peeps.individuals[peep4["id"]] = peep4
        fam2 = {
            "id": "@F02@",
            "children": [],
            "husband_id": peep3["id"],
            "wife_id": peep4["id"],
            "married_date": datetime(2009, 2, 10, 0, 0, 0),
            "divorced_date": datetime(2012, 2, 10, 0, 0, 0)
        }
        self.fam.families[fam2["id"]] = fam2
        # Family 3 setup (both alive)
        peep5 = {
            "id": "@I05@",
            "name": "Sammy /Davis jr./",
            "gender": "M",
            "is_alive": True,
            "birth_date": datetime(1990, 8, 17, 0, 0, 0),
            "death_date": None,
            "child_of_families": [],
            "spouse_of_families": ["@F03@"],
            "age": 27
        }
        self.peeps.individuals[peep5["id"]] = peep5
        peep6 = {
            "id": "@I06@",
            "gender": "F",
            "name": "Tina /Turner/",
            "is_alive": True,
            "birth_date": datetime(1990, 8, 17, 0, 0, 0),
            "death_date": None,
            "child_of_families": [],
            "spouse_of_families": ["@F03@"],
            "age": 27
        }
        self.peeps.individuals[peep6["id"]] = peep6
        fam3 = {
            "id": "@F03@",
            "children": [],
            "husband_id": peep5["id"],
            "wife_id": peep6["id"],
            "married_date": datetime(2012, 2, 10, 0, 0, 0),
            "divorced_date": datetime(2014, 2, 10, 0, 0, 0)
        }
        self.fam.families[fam3["id"]] = fam3
        # Family 4 setup (both dead before divorce) DOUBLE FAILURE
        peep7 = {
            "id": "@I07@",
            "name": "Paris /Troy/",
            "gender": "M",
            "is_alive": True,
            "birth_date": datetime(1980, 8, 17, 0, 0, 0),
            "death_date": datetime(2011, 8, 17, 0, 0, 0),
            "child_of_families": [],
            "spouse_of_families": ["@F04@"],
            "age": 21
        }
        self.peeps.individuals[peep7["id"]] = peep7
        peep8 = {
            "id": "@I08@",
            "gender": "F",
            "name": "Helena /Troy/",
            "is_alive": False,
            "birth_date": datetime(1980, 8, 17, 0, 0, 0),
            "death_date": datetime(2010, 8, 17, 0, 0, 0),
            "child_of_families": [],
            "spouse_of_families": ["@F04@"],
            "age": 20
        }
        self.peeps.individuals[peep8["id"]] = peep8
        fam4 = {
            "id": "@F04@",
            "children": [],
            "husband_id": peep7["id"],
            "wife_id": peep8["id"],
            "married_date": datetime(2009, 2, 10, 0, 0, 0),
            "divorced_date": datetime(2015, 2, 10, 0, 0, 0)
        }
        self.fam.families[fam4["id"]] = fam4
        # Family 5 setup no divorced date
        peep9 = {
            "id": "@I09@",
            "name": "Paris /Troy/",
            "gender": "M",
            "is_alive": True,
            "birth_date": datetime(1980, 8, 17, 0, 0, 0),
            "death_date": datetime(2011, 8, 17, 0, 0, 0),
            "child_of_families": [],
            "spouse_of_families": ["@F04@"],
            "age": 21
        }
        self.peeps.individuals[peep9["id"]] = peep9
        peep10 = {
            "id": "@I10@",
            "gender": "F",
            "name": "Helena /Troy/",
            "is_alive": False,
            "birth_date": datetime(1990, 8, 17, 0, 0, 0),
            "death_date": datetime(2010, 8, 17, 0, 0, 0),
            "child_of_families": [],
            "spouse_of_families": ["@F05@"],
            "age": 20
        }
        self.peeps.individuals[peep10["id"]] = peep10
        fam5 = {
            "id": "@F05@",
            "children": [],
            "husband_id": peep7["id"],
            "wife_id": peep8["id"],
            "married_date": None,
            "divorced_date": None
        }
        self.fam.families[fam5["id"]] = fam5
        # Family 6 setup (no spouses)
        fam6 = {
            "id": "@F06@",
            "children": [],
            "husband_id": None,
            "wife_id": None,
            "married_date": datetime(2012, 2, 10, 0, 0, 0),
            "divorced_date": datetime(2013, 2, 10, 0, 0, 0)
        }
        self.fam.families[fam6["id"]] = fam6

        self.fam.validate()

        results = self.msgs.get_messages()

        self.assertEqual(3, len(results))
        err1 = {
            "error_id": "FAMILY",
            "user_story": "US06",
            "user_id": fam2["id"],
            "name": "NA",
            "message": "divorce after death for " + peep3["id"] + " " + peep3["name"]
        }
        self.assertDictEqual(err1, results[0])
        err2 = {
            "error_id": "FAMILY",
            "user_story": "US06",
            "user_id": fam4["id"],
            "name": "NA",
            "message": "divorce after death for " + peep7["id"] + " " + peep7["name"]
        }
        self.assertDictEqual(err2, results[1])
        err3 = {
            "error_id": "FAMILY",
            "user_story": "US06",
            "user_id": fam4["id"],
            "name": "NA",
            "message": "divorce after death for " + peep8["id"] + " " + peep8["name"]
        }
        self.assertDictEqual(err3, results[2])