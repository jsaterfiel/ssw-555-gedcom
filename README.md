# ssw-555-gedcom
A project for SSW-555 dealing with GEDCOM.

## Members
- Chris Boffa
- Chelsea Hinds-Charles
- John Saterfiel
- Courtney Thaden

## Setup
Project is coded in Python 3.6.x (https://www.python.org/downloads/)

Example usage:
```
python3 gedcom/gedcom.py samples/sample_01.ged
```

IDE of choice is VS Code https://code.visualstudio.com/ with the python extension https://marketplace.visualstudio.com/items?itemName=donjayamanne.python

Github Client for Git management https://desktop.github.com/

## Pip Libraries
### Pretty Table
for printing out tabular data in the console
https://code.google.com/archive/p/prettytable/wikis/Tutorial.wiki
```
pip3 install https://pypi.python.org/packages/source/P/PrettyTable/prettytable-0.7.2.tar.bz2
```

### AutoPep8
for auto formatting text on save in IDE
```
pip3 install autopep8
```

## Code Styling
We will be using the standard PEP 8 code styles https://www.python.org/dev/peps/pep-0008

Basics from it to note:
- 4 spaces for tabs
- class names in camelcase MyClass
- method names and attributes in lowercase separated by underscores my_func
- private attributes proceed the name with an underscore _my_private_attr
- all files must have a module doc comment
- classes must document its attributes and arguments in the class doc comment not in the ```__init__``` function

## Code Process
- No changes directly to master branch
- Create a new branch for each ticket worked on
- Only work on one ticket per branch
- Create a pull request to merge the branch to master once work is completed
- Remember to go to the project board (aka sprint board) to update ticket statuses including in progress
- Travis CI/CD will be used for running unit tests before a pull request can be approved
- Team members must participate in code reviews to help other team members out
- Remember to push to origin always so your changes go up to the server

## Unit Testing
Coming soon!
