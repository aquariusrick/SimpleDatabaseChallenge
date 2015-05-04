from db import DatabaseCommandParser, DatabaseCommandParserException
import sys

if __name__ == '__main__':
    db = DatabaseCommandParser()
    if sys.stdin.isatty():
        while True:
            try:
                command = raw_input("Enter Command: ")
                result = db.execute(command)
                if result is not None:
                    print result
            except DatabaseCommandParserException as e:
                print e.message
    else:
        lines = sys.stdin.readlines()
        for l in lines:
            try:
                print l.strip()
                result = db.execute(l)
                if result is not None:
                    print result
            except DatabaseCommandParserException as e:
                print e.message
