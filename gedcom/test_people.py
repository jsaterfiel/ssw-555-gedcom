"""Test cases for people module
"""
import unittest
import io
import sys
from datetime import datetime
from people import People
from person import Person
from validation_messages import ValidationMessages
from families import Families


class TestPeople(unittest.TestCase):
    """test cases for families class
    Attributes:
        fam (Families): Family test object
    """

    def setUp(self):
        """creates setup objects
        """
        self.msgs = ValidationMessages()
        self.peeps = People(self.msgs)
        self.fam = Families(self.peeps, self.msgs)

    def tearDown(self):
        """delete setup objects
        """
        del self.peeps
        del self.fam
        del self.msgs

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
        test_person = Person(data["args"])
        result = self.peeps.individuals[data["args"]]
        self.assertEqual(test_person.get_person_id(), result.get_person_id())

    def test_unique_id(self):
        """US22 unique ID for people
        """
        person1 = {
            "level": 0,
            "tag": "INDI",
            "args": "@I1@",
            "valid": "Y"
        }
        self.peeps.process_line_data(person1)
        person2 = {
            "level": 0,
            "tag": "INDI",
            "args": "@I1@",
            "valid": "Y"
        }
        self.peeps.process_line_data(person2)
        self.assertEqual(1, len(self.peeps.individuals))

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
        result1 = self.peeps.individuals[person1["args"]]
        self.assertEqual(person1["args"], result1.get_person_id())

        result2 = self.peeps.individuals[person2["args"]]
        self.assertEqual(person2["args"], result2.get_person_id())

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
            person_name["args"], self.peeps.individuals[person["args"]].get_name())

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
            gender["args"], self.peeps.individuals[person["args"]].get_gender())

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
            date_obj, self.peeps.individuals[data["args"]].get_birth_date())
        age = int((datetime.now().date() - date_obj.date()).days / 365.2425)
        self.assertEqual(age, self.peeps.individuals[data["args"]].get_age())

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
            date_obj, self.peeps.individuals[data["args"]].get_death_date())
        self.assertIsNone(self.peeps.individuals[data["args"]].get_age())

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
        self.assertEqual(9, self.peeps.individuals[data["args"]].get_age())

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
        self.assertEqual(9, self.peeps.individuals[data["args"]].get_age())

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
            child1["args"], self.peeps.individuals[person["args"]].get_children_of_families()[0])
        child2 = {
            "level": 1,
            "tag": "FAMC",
            "args": "@F10@",
            "valid": "Y"
        }
        self.peeps.process_line_data(child2)
        self.assertEqual(
            child2["args"], self.peeps.individuals[person["args"]].get_children_of_families()[1])

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
            fam1["args"], self.peeps.individuals[person["args"]].get_spouse_of_families()[0])
        fam2 = {
            "level": 1,
            "tag": "FAMS",
            "args": "@F10@",
            "valid": "Y"
        }
        self.peeps.process_line_data(fam2)
        self.assertEqual(
            fam2["args"], self.peeps.individuals[person["args"]].get_spouse_of_families()[1])

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

    def test_us03_is_valid_birth_date(self):
        """US03 test case for valid birth dates
        """
        valid_person = Person("@I3@")
        valid_person.set_name("Margo /Hemmingway/")
        valid_person.set_gender("F")
        valid_person.set_date("8 APR 1954", "birth")
        valid_person.set_date("5 NOV 2011", "death")
        self.peeps.individuals[valid_person.get_person_id()] = valid_person

        self.peeps.validate()

        self.assertEqual(0, len(self.msgs.get_messages()))

        invalid_person = Person("@I4@")
        invalid_person.set_gender("F")
        invalid_person.set_name("Gergina /Hemmingway/")
        invalid_person.set_date("8 APR 1954", "death")
        invalid_person.set_date("5 NOV 2011", "birth")
        self.peeps.individuals[invalid_person.get_person_id()] = invalid_person

        self.peeps.validate()

        test_messages = self.msgs.get_messages()

        self.assertEqual(1, len(test_messages))

        valid_error_message = {
            'error_id': People.CLASS_IDENTIFIER,
            'user_story': 'US03',
            'user_id': invalid_person.get_person_id(),
            'name': invalid_person.get_name(),
            'message': 'Birth date should occur before death of an individual'
        }

        self.assertDictEqual(valid_error_message, test_messages[0])

    def test_us07_not_too_old(self):
        """US07: test is the person's age is less than 150
        """
        valid_person = Person("@I3@")
        valid_person.set_name("Bubbles /Bambi/")
        valid_person.set_date("1 JAN 1960", "birth")
        self.peeps.individuals[valid_person.get_person_id()] = valid_person

        invalid_person = Person("@I4@")
        invalid_person.set_name("Margo /Hemmingway/")
        invalid_person.set_date("1 JAN 2000", "death")  # 151 years old
        invalid_person.set_date("1 JAN 1849", "birth")
        self.peeps.individuals[invalid_person.get_person_id()] = invalid_person

        invalid_person2 = Person("@I5@")
        invalid_person2.set_name("Betty /Hemmingway/")
        invalid_person2.set_date("2 JAN 2000", "death")  # 150 years old
        invalid_person2.set_date("1 JAN 1850", "birth")
        self.peeps.individuals[invalid_person2.get_person_id()
                               ] = invalid_person2

        invalid_person3 = Person("@I6@")
        invalid_person3.set_name("Moses /Hemmingway/")
        invalid_person3.set_date("1 JAN 2000", "death")  # 200 years old
        invalid_person3.set_date("1 JAN 1800", "birth")
        self.peeps.individuals[invalid_person3.get_person_id()
                               ] = invalid_person3
        valid_person2 = Person("@I7@")
        valid_person2.set_name("Salty /Hemmingway/")
        valid_person2.set_date("1 JAN 2000", "death")  # 149 years old
        valid_person2.set_date("1 JAN 1851", "birth")
        self.peeps.individuals[valid_person2.get_person_id()
                               ] = valid_person2

        self.peeps.validate()

        output = self.msgs.get_messages()
        self.assertEqual(3, len(output))

        error1 = {
            "error_id": "INDIVIDUAL",
            "message": "Age should be less than 150",
            "name": invalid_person.get_name(),
            "user_id": invalid_person.get_person_id(),
            "user_story": "US07"
        }
        self.assertDictEqual(error1, output[0])
        error2 = {
            "error_id": "INDIVIDUAL",
            "message": "Age should be less than 150",
            "name": invalid_person2.get_name(),
            "user_id": invalid_person2.get_person_id(),
            "user_story": "US07"
        }
        self.assertDictEqual(error2, output[1])
        error3 = {
            "error_id": "INDIVIDUAL",
            "message": "Age should be less than 150",
            "name": invalid_person3.get_name(),
            "user_id": invalid_person3.get_person_id(),
            "user_story": "US07"
        }
        self.assertDictEqual(error3, output[2])

    def test_us01_dates_before_current_date(self):
        """US01: test that all dates are before the current date
        """
        curr = datetime.now()

        date_before_current = Person("@I10@")
        date_before_current.set_name("Link /Tiger/")
        date_before_current.set_date("7 OCT 1940", "birth")
        self.peeps.individuals[date_before_current.get_person_id(
        )] = date_before_current

        date_before_current1 = Person("@I11@")
        date_before_current1.set_name("Zelda /Tiger/")
        date_before_current1.set_date("7 OCT 1942", "birth")
        self.peeps.individuals[date_before_current1.get_person_id(
        )] = date_before_current1

        date_notbefore_current1 = Person("@I3@")
        date_notbefore_current1.set_name("Ernest /Hemmingway/")
        date_notbefore_current1.set_date("4 AUG 1861", "birth")
        date_notbefore_current1.set_date(
            "5 NOV " + str(curr.year + 4), "death")
        self.peeps.individuals[date_notbefore_current1.get_person_id(
        )] = date_notbefore_current1

        date_notbefore_current2 = Person("@I5@")
        date_notbefore_current2.set_name("Rodney /Dangerfield/")
        date_notbefore_current2.set_date(
            "9 OCT " + str(curr.year + 2), "birth")
        self.peeps.individuals[date_notbefore_current2.get_person_id(
        )] = date_notbefore_current2

        self.peeps.validate()

        output = self.msgs.get_messages()
        self.assertEqual(3, len(output))

        error1 = {
            "error_id": "INDIVIDUAL",
            "user_story": "US01",
            "user_id": date_notbefore_current1.get_person_id(),
            "name": date_notbefore_current1.get_name(),
            "message": "Death date should occur before current date"
        }
        self.assertDictEqual(error1, output[1])
        error2 = {
            "error_id": "INDIVIDUAL",
            "user_story": "US01",
            "user_id": date_notbefore_current2.get_person_id(),
            "name": date_notbefore_current2.get_name(),
            "message": "Birth date should occur before current date"
        }
        self.assertDictEqual(error2, output[2])

    def test_us18_is_valid_sibling(self):
        husband = Person("@I3@")
        husband.set_name("Steve /Bambi/")
        husband.add_children_of_family("@F4@")
        husband.add_spouse_of_family("@F4@")
        self.peeps.individuals[husband.get_person_id()] = husband

        wife = Person("@I3@")
        wife.set_name("Bubbles /Bambi/")
        wife.add_children_of_family("@F4@")
        wife.add_spouse_of_family("@F4@")
        self.peeps.individuals[husband.get_person_id()] = wife

        self.assertFalse(self.peeps._us18_is_valid_sibling(wife))
        self.assertFalse(self.peeps._us18_is_valid_sibling(husband))

        wife.remove_children_of_family("@F4@")
        husband.remove_children_of_family("@F4@")

        self.assertTrue(self.peeps._us18_is_valid_sibling(wife))
        self.assertTrue(self.peeps._us18_is_valid_sibling(husband))

    def test_us31_print_single(self):
        """ US31 Unit tests
        """
        single_person = Person("@I3@")
        single_person.set_name("Margo /Hemmingway/")
        single_person.set_gender("F")
        single_person.set_date("8 APR 1954", "birth")
        self.peeps.individuals[single_person.get_person_id()] = single_person

        married_person = Person("@I4@")
        married_person.set_name("David /Hemmingway/")
        married_person.set_gender("M")
        married_person.set_date("8 APR 1939", "birth")
        married_person.add_spouse_of_family("@F1@")
        self.peeps.individuals[married_person.get_person_id()] = married_person

        # Not over 30
        single_person1 = Person("@I5@")
        single_person1.set_name("Dodge /Hemmingway/")
        single_person1.set_gender("M")
        single_person1.set_date("8 APR 1987", "birth")
        self.peeps.individuals[single_person1.get_person_id()] = single_person1

        # Not over 30
        single_person2 = Person("@I6@")
        single_person2.set_name("Dingo /Hemmingway/")
        single_person2.set_gender("M")
        single_person2.set_date("8 APR 1990", "birth")
        self.peeps.individuals[single_person2.get_person_id()] = single_person2

        # Not alive
        single_person3 = Person("@I7@")
        single_person3.set_name("Draftie /Hemmingway/")
        single_person3.set_gender("M")
        single_person3.set_date("8 APR 1967", "birth")
        single_person3.set_date("8 APR 1990", "death")
        self.peeps.individuals[single_person3.get_person_id()] = single_person3

        # No age
        single_person4 = Person("@I8@")
        single_person4.set_name("Dirty /Hemmingway/")
        single_person4.set_gender("M")
        self.peeps.individuals[single_person4.get_person_id()] = single_person4

        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.peeps.us31_print_single()
        sys.stdout = sys.__stdout__
        test_output = """Single Individuals
+------+--------------------+-------+-----+---------+
|  ID  |        Name        | Alive | Age | Spouses |
+------+--------------------+-------+-----+---------+
| @I3@ | Margo /Hemmingway/ |  True |  63 |    []   |
+------+--------------------+-------+-----+---------+
"""
        self.assertEqual(test_output, output.getvalue())

    def test_us29_print_deceased(self):
        """ US29 Unit tests
        """
        deceased_person = Person("@I3@")
        deceased_person.set_name("Margo /Hemmingway/")
        deceased_person.set_gender("F")
        deceased_person.set_date("8 APR 1954", "birth")
        deceased_person.set_date("5 NOV 2011", "death")
        self.peeps.individuals[deceased_person.get_person_id()] = deceased_person

        alive_person = Person("@I4@")
        alive_person.set_name("David /Hemmingway/")
        alive_person.set_gender("M")
        alive_person.set_date("8 APR 1954", "birth")
        self.peeps.individuals[alive_person.get_person_id()] = alive_person

        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.peeps.us29_print_deceased()
        sys.stdout = sys.__stdout__
        test_output = """Deceased Individuals
+------+--------------------+-------+
|  ID  |        Name        | Alive |
+------+--------------------+-------+
| @I3@ | Margo /Hemmingway/ | False |
+------+--------------------+-------+
"""
        self.assertEqual(test_output, output.getvalue())

    def test_us35_print_recent_births(self):
        """ US35 unit test testing recent births
        """
        # valid - pass
        recent_birth = Person("@I11@")
        recent_birth.set_name("Kyrie /Irving/")
        recent_birth.set_gender("M")
        recent_birth.set_date("30 OCT 2017", "birth")
        self.peeps.individuals[recent_birth.get_person_id()] = recent_birth
        # invalid - fail
        not_recent_birth = Person("@I38@")
        not_recent_birth.set_name("LaBron /James/")
        not_recent_birth.set_gender("M")
        not_recent_birth.set_date("30 OCT 1977", "birth")
        self.peeps.individuals[not_recent_birth.get_person_id()] = not_recent_birth

        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.peeps.us35_print_recent_births()
        sys.stdout = sys.__stdout__
        test_output = """Recent Births
+-------+----------------+---------------------+
|   ID  |      Name      |      Birthdate      |
+-------+----------------+---------------------+
| @I11@ | Kyrie /Irving/ | 2017-10-30 00:00:00 |
+-------+----------------+---------------------+
"""

    def test_us36_print_recent_deaths(self):
        """ US36 unit test testing recent deaths
        """
        # valid - pass
        recent_death = Person("@I49@")
        recent_death.set_name("Mike /Jack/")
        recent_death.set_gender("M")
        recent_death.set_date("31 OCT 2017", "death")
        self.peeps.individuals[recent_death.get_person_id()] = recent_death
        # invalid - fail
        not_recent_death = Person("@I38@")
        not_recent_death.set_name("Maya /Angelou/")
        not_recent_death.set_gender("M")
        not_recent_death.set_date("30 OCT 1977", "death")
        self.peeps.individuals[not_recent_death.get_person_id()] = not_recent_death

        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.peeps.us36_print_recent_deaths()
        sys.stdout = sys.__stdout__
        test_output = """Recent Deaths
+-------+----------------+---------------------+
|   ID  |      Name      |      Birthdate      |
+-------+----------------+---------------------+
| @I49@ | Mike / Jack /  | 2017-10-31 00:00:00 |
+-------+----------------+---------------------+
"""

    def test_us_38_print_upcoming_birthdays(self):
        """ US38 Unit tests
        """
        recent_birthday_person = Person("@I3@")
        recent_birthday_person.set_name("Margo /Hemmingway/")
        recent_birthday_person.set_gender("F")
        recent_birthday_person.set_date("20 NOV 1954", "birth")
        self.peeps.individuals[recent_birthday_person.get_person_id()] = recent_birthday_person

        past_birthday_person = Person("@I4@")
        past_birthday_person.set_name("Marge /Hemmingway/")
        past_birthday_person.set_gender("F")
        past_birthday_person.set_date("1 NOV 1960", "birth")
        self.peeps.individuals[past_birthday_person.get_person_id()] = past_birthday_person

        deceased_person = Person("@I5@")
        deceased_person.set_name("David /Hemmingway/")
        deceased_person.set_gender("M")
        deceased_person.set_date("8 APR 1954", "birth")
        deceased_person.set_date("31 OCT 2017", "death")
        self.peeps.individuals[deceased_person.get_person_id()] = deceased_person

        # capture the output
        output = io.StringIO()
        sys.stdout = output
        self.peeps.us_38_print_upcoming_birthdays()
        sys.stdout = sys.__stdout__
        test_output = """Upcoming Birthdays
+------+--------------------+---------------------+
|  ID  |        Name        |       Birthday      |
+------+--------------------+---------------------+
| @I3@ | Margo /Hemmingway/ | 1954-11-20 00:00:00 |
+------+--------------------+---------------------+
"""
        self.assertEqual(test_output, output.getvalue())
