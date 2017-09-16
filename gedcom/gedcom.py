"""GEDCOM project program for SSW-555
"""
import sys
from tags import Tags, TagsError
from families import Families
from people import People


def run():
    """main function
    """
    file_data = None
    filename = ""
    tags = Tags()
    peeps = People()
    fam = Families(peeps)

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
    print("Individuals")
    peeps.print_all()
    print("Families")
    fam.print_all()


run()
