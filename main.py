import argparse
import os
import re


dirs_to_ignore: list[str] = [
    "__pycache__",
    "build",
    "dist",
    "lib",
    "logs",
]

docstring_pattern: re.Pattern = re.compile(r'""".*?"""', re.DOTALL)
identifier_pattern: re.Pattern = re.compile(r"(?<!`)\b[^\W_]\w*__?\b(?!`)")


def main():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--dir", metavar="starting-point", default=".", nargs=1, required=False
    )

    args: argparse.Namespace = parser.parse_args()
    dir: str = args.dir

    for dirpath, dirnames, filenames in os.walk(dir, topdown=True):
        # remove any subfolders that should not be searched
        i = len(dirnames)
        for dirname in reversed(dirnames):
            i -= 1
            if (
                dirname.startswith(".")
                or dirname.startswith("venv")
                or dirname in dirs_to_ignore
            ):
                del dirnames[i]

        # search this folder
        for file in filenames:
            if file.endswith(".py"):
                filepath: str = os.path.join(dirpath, file)
                with open(filepath, "r", encoding="utf8") as file:
                    content: str = file.read()

                for match in docstring_pattern.finditer(content):
                    docstring: str = match.group(0)
                    for var_match in identifier_pattern.finditer(docstring):
                        variable_name: str = var_match.group(0)
                        start: int = match.start() + docstring.find(variable_name)
                        line_number: int = content.count("\n", 0, start) + 1

                        print(f"{filepath}:{line_number}: '{variable_name}' needs backticks")


if __name__ == "__main__":
    main()
