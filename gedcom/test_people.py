"""Test cases for people module
"""
import unittest
import io
import sys
from datetime import datetime
from people import People


class TestPeople(unittest.TestCase):
    """test cases for families class
    Attributes:
        fam (Families): Family test object
    """

    def setUp(self):
        """creates family object
        """
        self.peeps = People()

    def tearDown(self):
        """delete family object
        """
        del self.peeps

    def test_default_init(self):
        """make sure the object is empty on init
        """
        self.assertEqual(0, len(self.peeps.individuals))

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
            self.peeps.process_line_data(data)
        # ensure nothing got added
        self.assertEqual(0, len(self.peeps.individuals))

    def test_add_individual(self):
        """test cases for detecting the person tag and adding it to the list of individuals
        """
        # raw line:
        # 0 @I6@ INDI
        data = {
            "level": 0,
            "tag": "INDI",
            "args": "@I6@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data)
        # add a person
        self.assertEqual(1, len(self.peeps.individuals))

        # test person dict setup
        test_person = {
            "id": data["args"]
        }
        self.assertDictContainsSubset(
            test_person, self.peeps.individuals[data["args"]])

    def test_correct_individual_tag(self):
        """Ensuring the INDI tag can only be used to add a person
        """
        # raw line:
        # 0 @I8@ FAM
        data = {
            "level": 0,
            "tag": "FAM",
            "args": "@I8@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data)
        # add a person
        self.assertEqual(0, len(self.peeps.individuals))

    def test_add_multiple_people(self):
        """adding mulitiple people to make sure they are both read in
        """

        # raw lines:
        # 0 @I9@ INDI
        # 0 @A6@ INDI
        person1 = {
            "level": 0,
            "tag": "INDI",
            "args": "@I9@",
            "valid": "Y"
        }
        self.peeps.process_line_data(person1)
        person2 = {
            "level": 0,
            "tag": "INDI",
            "args": "@A6@",
            "valid": "Y"
        }
        self.peeps.process_line_data(person2)
        # add a family
        self.assertEqual(2, len(self.peeps.individuals))

        # test family exist
        test_person1 = {
            "id": person1["args"]
        }
        self.assertDictContainsSubset(
            test_person1, self.peeps.individuals[person1["args"]])
        test_person2 = {
            "id": person2["args"]
        }
        self.assertDictContainsSubset(
            test_person2, self.peeps.individuals[person2["args"]])

    def test_name(self):
        """name test for people
        """
        # raw lines:
        # 0 @I6@ INDI
        # 1 NAME Joe /Smith/
        person = {
            "level": 0,
            "tag": "INDI",
            "args": "@I6@",
            "valid": "Y"
        }
        self.peeps.process_line_data(person)
        person_name = {
            "level": 1,
            "tag": "NAME",
            "args": "Joe /Smith/",
            "valid": "Y"
        }
        self.peeps.process_line_data(person_name)
        self.assertEqual(
            person_name["args"], self.peeps.individuals[person["args"]]["name"])

    def test_gender(self):
        """gender tests for people
        """
        # raw lines:
        # 0 @I6@ INDI
        # 1 SEX M
        person = {
            "level": 0,
            "tag": "INDI",
            "args": "@I6@",
            "valid": "Y"
        }
        self.peeps.process_line_data(person)
        gender = {
            "level": 1,
            "tag": "SEX",
            "args": "M",
            "valid": "Y"
        }
        self.peeps.process_line_data(gender)
        self.assertEqual(
            gender["args"], self.peeps.individuals[person["args"]]["gender"])

    def test_birth_date(self):
        """able to read the birth date for a person and their age
        """
        # raw lines:
        # 0 @A9@ INDI
        # 1 BIRT
        # 2 DATE 15 JUN 1970
        data = {
            "level": 0,
            "tag": "INDI",
            "args": "@A9@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data)
        birth_tag = {
            "level": 1,
            "tag": "BIRT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_tag)
        birth_date = {
            "level": 2,
            "tag": "DATE",
            "args": "15 JUN 1970",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_date)
        date_obj = datetime.strptime(birth_date["args"], '%d %b %Y')
        self.assertEqual(
            date_obj, self.peeps.individuals[data["args"]]["birth_date"])
        age = int((datetime.now().date() - date_obj.date()).days / 365.2425)
        self.assertEqual(age, self.peeps.individuals[data["args"]]["age"])

    def test_death(self):
        """test reading if a person is dead and has no birth date so no age
        """
        # raw lines:
        # 0 @I6@ INDI
        # 1 DEAT
        person = {
            "level": 0,
            "tag": "INDI",
            "args": "@I6@",
            "valid": "Y"
        }
        self.peeps.process_line_data(person)
        death = {
            "level": 1,
            "tag": "DEAT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(death)
        self.assertFalse(self.peeps.individuals[person["args"]]["is_alive"])
        self.assertIsNone(self.peeps.individuals[person["args"]]["age"])

    def test_death_date_no_birth(self):
        """test death date no birth and no age should be set
        """
        # raw lines:
        # 0 @A9@ INDI
        # 1 DEAT
        # 2 DATE 1 APR 1980
        data = {
            "level": 0,
            "tag": "INDI",
            "args": "@A9@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data)
        death_tag = {
            "level": 1,
            "tag": "DEAT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(death_tag)
        death_date = {
            "level": 2,
            "tag": "DATE",
            "args": "1 APR 1980",
            "valid": "Y"
        }
        self.peeps.process_line_data(death_date)
        date_obj = datetime.strptime(death_date["args"], '%d %b %Y')
        self.assertEqual(
            date_obj, self.peeps.individuals[data["args"]]["death_date"])
        self.assertIsNone(self.peeps.individuals[data["args"]]["age"])

    def test_birth_then_death_date(self):
        """test birth then death date with age of 9 years 9 months so 9
        """
        # raw lines:
        # 0 @A9@ INDI
        # 1 BIRT
        # 2 DATE 15 JUN 1970
        # 1 DEAT
        # 2 DATE 1 APR 1980
        data = {
            "level": 0,
            "tag": "INDI",
            "args": "@A9@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data)
        birth_tag = {
            "level": 1,
            "tag": "BIRT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_tag)
        birth_date = {
            "level": 2,
            "tag": "DATE",
            "args": "15 JUN 1970",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_date)
        death_tag = {
            "level": 1,
            "tag": "DEAT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(death_tag)
        death_date = {
            "level": 2,
            "tag": "DATE",
            "args": "1 APR 1980",
            "valid": "Y"
        }
        self.peeps.process_line_data(death_date)
        self.assertEqual(9, self.peeps.individuals[data["args"]]["age"])

    def test_death_then_birth_date(self):
        """test death then birth date with age of 9 years 9 months so 9
        """
        # raw lines:
        # 0 @A9@ INDI
        # 1 DEAT
        # 2 DATE 1 APR 1980
        # 1 BIRT
        # 2 DATE 15 JUN 1970
        data = {
            "level": 0,
            "tag": "INDI",
            "args": "@A9@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data)
        death_tag = {
            "level": 1,
            "tag": "DEAT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(death_tag)
        death_date = {
            "level": 2,
            "tag": "DATE",
            "args": "1 APR 1980",
            "valid": "Y"
        }
        self.peeps.process_line_data(death_date)
        birth_tag = {
            "level": 1,
            "tag": "BIRT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_tag)
        birth_date = {
            "level": 2,
            "tag": "DATE",
            "args": "15 JUN 1970",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_date)
        self.assertEqual(9, self.peeps.individuals[data["args"]]["age"])

    def test_child_of_family(self):
        """test person being a child in a family
        """
        # raw lines:
        # 0 @I6@ INDI
        # 1 FAMC @F09@
        # 1 FAMC @F10@
        person = {
            "level": 0,
            "tag": "INDI",
            "args": "@I6@",
            "valid": "Y"
        }
        self.peeps.process_line_data(person)
        child1 = {
            "level": 1,
            "tag": "FAMC",
            "args": "@F09@",
            "valid": "Y"
        }
        self.peeps.process_line_data(child1)
        self.assertEqual(
            child1["args"], self.peeps.individuals[person["args"]]["child_of_families"][0])
        child2 = {
            "level": 1,
            "tag": "FAMC",
            "args": "@F10@",
            "valid": "Y"
        }
        self.peeps.process_line_data(child2)
        self.assertEqual(
            child2["args"], self.peeps.individuals[person["args"]]["child_of_families"][1])

    def test_spouse_of_family(self):
        """test person being a spouse in a family
        """
        # raw lines:
        # 0 @I6@ INDI
        # 1 FAMS @F09@
        # 1 FAMS @F10@
        person = {
            "level": 0,
            "tag": "INDI",
            "args": "@I6@",
            "valid": "Y"
        }
        self.peeps.process_line_data(person)
        fam1 = {
            "level": 1,
            "tag": "FAMS",
            "args": "@F09@",
            "valid": "Y"
        }
        self.peeps.process_line_data(fam1)
        self.assertEqual(
            fam1["args"], self.peeps.individuals[person["args"]]["spouse_of_families"][0])
        fam2 = {
            "level": 1,
            "tag": "FAMS",
            "args": "@F10@",
            "valid": "Y"
        }
        self.peeps.process_line_data(fam2)
        self.assertEqual(
            fam2["args"], self.peeps.individuals[person["args"]]["spouse_of_families"][1])

    def test_print_all(self):
        """test print all persons
        """
        # raw lines:
        # 0 @A9@ INDI
        # 1 NAME Joe /Smith/
        # 1 SEX M
        # 1 BIRT
        # 2 DATE 15 JUN 1970
        # 1 DEAT
        # 2 DATE 1 APR 1980
        # 1 FAMC @F02@
        # 1 FAMS @F09@
        data = {
            "level": 0,
            "tag": "INDI",
            "args": "@A9@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data)
        name_tag = {
            "level": 1,
            "tag": "NAME",
            "args": "Joe /Smith/",
            "valid": "Y"
        }
        self.peeps.process_line_data(name_tag)
        sex_tag = {
            "level": 1,
            "tag": "SEX",
            "args": "M",
            "valid": "Y"
        }
        self.peeps.process_line_data(sex_tag)
        birth_tag = {
            "level": 1,
            "tag": "BIRT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_tag)
        birth_date = {
            "level": 2,
            "tag": "DATE",
            "args": "15 JUN 1970",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_date)
        death_tag = {
            "level": 1,
            "tag": "DEAT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(death_tag)
        death_date = {
            "level": 2,
            "tag": "DATE",
            "args": "1 APR 1980",
            "valid": "Y"
        }
        self.peeps.process_line_data(death_date)
        child_data = {
            "level": 1,
            "tag": "FAMC",
            "args": "@F02@",
            "valid": "Y"
        }
        self.peeps.process_line_data(child_data)
        spouse_data = {
            "level": 1,
            "tag": "FAMS",
            "args": "@F09@",
            "valid": "Y"
        }
        self.peeps.process_line_data(spouse_data)

        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.peeps.print_all()
        sys.stdout = sys.__stdout__
        test_output = """+------+-------------+--------+------------+-----+-------+------------+-----------+-----------+
|  ID  |     Name    | Gender |  Birthday  | Age | Alive |   Death    |   Child   |   Spouse  |
+------+-------------+--------+------------+-----+-------+------------+-----------+-----------+
| @A9@ | Joe /Smith/ |   M    | 1970-06-15 |  9  | False | 1980-04-01 | ['@F02@'] | ['@F09@'] |
+------+-------------+--------+------------+-----+-------+------------+-----------+-----------+
"""
        self.assertEqual(test_output, output.getvalue())

    def test_print_all_no_dates(self):
        """test print all persons
        """
        # raw lines:
        # 0 @A9@ INDI
        # 1 NAME Joe /Smith/
        # 1 SEX M
        # 1 FAMC @F02@
        # 1 FAMS @F09@
        data = {
            "level": 0,
            "tag": "INDI",
            "args": "@A9@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data)
        name_tag = {
            "level": 1,
            "tag": "NAME",
            "args": "Joe /Smith/",
            "valid": "Y"
        }
        self.peeps.process_line_data(name_tag)
        sex_tag = {
            "level": 1,
            "tag": "SEX",
            "args": "M",
            "valid": "Y"
        }
        self.peeps.process_line_data(sex_tag)
        child_data = {
            "level": 1,
            "tag": "FAMC",
            "args": "@F02@",
            "valid": "Y"
        }
        self.peeps.process_line_data(child_data)
        spouse_data = {
            "level": 1,
            "tag": "FAMS",
            "args": "@F09@",
            "valid": "Y"
        }
        self.peeps.process_line_data(spouse_data)

        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.peeps.print_all()
        sys.stdout = sys.__stdout__
        test_output = """+------+-------------+--------+----------+------+-------+-------+-----------+-----------+
|  ID  |     Name    | Gender | Birthday | Age  | Alive | Death |   Child   |   Spouse  |
+------+-------------+--------+----------+------+-------+-------+-----------+-----------+
| @A9@ | Joe /Smith/ |   M    |    NA    | None |  True |   NA  | ['@F02@'] | ['@F09@'] |
+------+-------------+--------+----------+------+-------+-------+-----------+-----------+
"""
        self.assertEqual(test_output, output.getvalue())

    def test_print_all_in_order(self):
        """test print all persons in order
        """
        # raw lines:
        # 0 @A9@ INDI
        # 1 NAME Joe /Smith/
        # 1 SEX M
        # 0 @A3@ INDI
        # 1 NAME Jane /Doe/
        # 1 SEX F
        # 1 BIRT
        # 2 DATE 10 AUG 1960
        # 1 DEAT
        # 2 DATE 20 DEC 1990
        # 1 FAMC @F04@
        # 1 FAMS @F10@

        # person 1
        data1 = {
            "level": 0,
            "tag": "INDI",
            "args": "@A9@",
            "valid": "Y"
        }
        self.peeps.process_line_data(data1)
        name_tag1 = {
            "level": 1,
            "tag": "NAME",
            "args": "Joe /Smith/",
            "valid": "Y"
        }
        self.peeps.process_line_data(name_tag1)
        sex_tag1 = {
            "level": 1,
            "tag": "SEX",
            "args": "M",
            "valid": "Y"
        }
        self.peeps.process_line_data(sex_tag1)

        # person 2
        data2 = {
            "level": 0,
            "tag": "INDI",
            "args": "@A3@",
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
        sex_tag2 = {
            "level": 1,
            "tag": "SEX",
            "args": "F",
            "valid": "Y"
        }
        self.peeps.process_line_data(sex_tag2)
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
            "args": "10 AUG 1960",
            "valid": "Y"
        }
        self.peeps.process_line_data(birth_date2)
        death_tag2 = {
            "level": 1,
            "tag": "DEAT",
            "args": "",
            "valid": "Y"
        }
        self.peeps.process_line_data(death_tag2)
        death_date2 = {
            "level": 2,
            "tag": "DATE",
            "args": "20 DEC 1990",
            "valid": "Y"
        }
        self.peeps.process_line_data(death_date2)
        child_data2 = {
            "level": 1,
            "tag": "FAMC",
            "args": "@F04@",
            "valid": "Y"
        }
        self.peeps.process_line_data(child_data2)
        spouse_data2 = {
            "level": 1,
            "tag": "FAMS",
            "args": "@F10@",
            "valid": "Y"
        }
        self.peeps.process_line_data(spouse_data2)

        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.peeps.print_all()
        sys.stdout = sys.__stdout__
        test_output = """+------+-------------+--------+------------+------+-------+------------+-----------+-----------+
|  ID  |     Name    | Gender |  Birthday  | Age  | Alive |   Death    |   Child   |   Spouse  |
+------+-------------+--------+------------+------+-------+------------+-----------+-----------+
| @A3@ |  Jane /Doe/ |   F    | 1960-08-10 |  30  | False | 1990-12-20 | ['@F04@'] | ['@F10@'] |
| @A9@ | Joe /Smith/ |   M    |     NA     | None |  True |     NA     |     []    |     []    |
+------+-------------+--------+------------+------+-------+------------+-----------+-----------+
"""
        self.assertEqual(test_output, output.getvalue())
