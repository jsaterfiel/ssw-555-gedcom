"""GEDCOM project program for SSW-555
"""
import sys
from tags import Tags, TagsError


def run():
    """main function
    """
    file = None
    filename = ""
    tags = Tags()

    if len(sys.argv) < 2:
        sys.exit("Usage: " + sys.argv[0] + " path-to-gedom-file")
    filename = sys.argv[1]

    try:
        file = open(filename)
    except IOError:
        sys.exit("ERROR: file " + sys.argv[1] + "was not found!")

    for line in file:
        try:
            data = tags.processline(line)
        except TagsError as err:
            sys.exit("ERROR: ", err)
        print("{level}|{tag}|{valid}|{args}".format(**data))


run()
