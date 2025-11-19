import sys
from parser import Parser

def main():
    if len(sys.argv) < 2:
        print("Please specify an input file.")
        sys.exit(1)

    filename = sys.argv[1]

    code = ""
    with open(filename, "r") as file:
        code = file.read()

    if code:
        parser = Parser(code)
        parser.parse_program()
        print("program compiled successfully")
    else:
        print("Invalid input")

if __name__ == "__main__":
    main()
