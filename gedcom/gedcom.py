"""GEDCOM project program for SSW-555
"""
import sys
from .tags import Tags, TagsError
from .families import Families
from .people import People
from validation_messages import ValidationMessages


def run():
    """main function
    """
    file_data = None
    filename = ""
    validation_msgs = ValidationMessages()
    tags = Tags()
    peeps = People(validation_msgs)
    fam = Families(peeps, validation_msgs)

    if len(sys.argv) < 2:
        sys.exit("Usage: " + sys.argv[0] + " path-to-gedom-file")
    filename = sys.argv[1]

    try:
        file_data = open(filename)
    except IOError:
        sys.exit("ERROR: file " + sys.argv[1] + "was not found!")

    for line in file_data:
        try:
            data = tags.processline(line)
            if data["valid"] == "Y":
                fam.process_line_data(data)
                peeps.process_line_data(data)

        except TagsError as err:
            sys.exit("ERROR: ", err)

    if validation_msgs.get_messages():
        print("Validation Messages")
        validation_msgs.print_all()
        print("")

    print("Individuals")
    peeps.print_all()
    print("")

    print("Families")
    fam.print_all()
    print("")


run()
