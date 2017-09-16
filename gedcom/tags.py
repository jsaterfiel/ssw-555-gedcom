"""Tags module
Handles reading gedom files
"""


class TagsError(Exception):
    """TagsError raised when a line has syntax invalid information
    and the processing cannot continue

    Args:
        message (str): error message
        line (int): line where error occurred
    """

    def __init__(self, message, line):
        super(TagsError, self).__init__(message)
        self.message = message
        self.line = line

    def __str__(self):
        return 'ERROR: %s at line: %i' % (self.message, self.line)


class Tags:
    """Tags class handles parsing the gedom file line by line through
        processLine() function

    Attributes:
        all_tags: list of all the tags
        valid_tags: list of only the valid tags
        invalid_tags: list of only the invalid tags
    """

    VALID_TAGS = {
        "INDI": 0,
        "NAME": 1,
        "SEX": 1,
        "BIRT": 1,
        "DEAT": 1,
        "FAMC": 1,
        "FAMS": 1,
        "FAM": 0,
        "MARR": 1,
        "HUSB": 1,
        "WIFE": 1,
        "CHIL": 1,
        "DIV": 1,
        "DATE": 2,
        "HEAD": 0,
        "TRLR": 0,
        "NOTE": 0
    }

    def __init__(self):
        self.all_tags = []
        self.valid_tags = dict()
        self.invalid_tags = dict()

    def processline(self, line):
        """
        process each line to parse out the data to a dict

        Returns:
            {
                "level": int,
                "tag": string,
               "args": string,
                "valid": "Y" or "N"
            }
        """
        data = {"level": 0, "tag": "", "args": "", "valid": "Y"}
        pieces = line.rstrip().split(" ")

        # Level
        try:
            data["level"] = int(pieces.pop(0))

        except ValueError:
            raise TagsError("Invalid level found for line", line)

        # Tag
        if len(pieces) > 1:
            if pieces[1] == "INDI" or pieces[1] == "FAM":
                data["tag"] = pieces[1]
                data["args"] = pieces[0]

            else:
                data["tag"] = pieces.pop(0)
                data["args"] = ' '.join(pieces)

        else:
            data["tag"] = ' '.join(pieces)

        if data["tag"] not in self.VALID_TAGS:
            data["valid"] = "N"
        else:
            tag_level = self.VALID_TAGS.get(data["tag"])
            if tag_level != data["level"]:
                data["valid"] = "N"

        return data
