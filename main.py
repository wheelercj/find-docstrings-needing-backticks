import argparse
import os
import re
import sys


dirs_to_ignore: list[str] = [
    "__pycache__",
    "__pypackages__",
    "_build",
    "build",
    "dist",
    "lib",
    "logs",
    "node_modules",
    "site-packages",
]

dir_prefixes_to_ignore: list[str] = [
    ".",
    "venv",
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

    bad_identifier_count: int = 0
    for dirpath, dirnames, filenames in os.walk(dir, topdown=True):
        # remove any subfolders that should not be searched
        i = len(dirnames)
        for dirname in reversed(dirnames):
            i -= 1
            if dirname in dirs_to_ignore:
                del dirnames[i]
            for prefix in dir_prefixes_to_ignore:
                if dirname.startswith(prefix):
                    del dirnames[i]
                    break

        # search this folder
        for file in filenames:
            if file.endswith(".py"):
                filepath: str = os.path.join(dirpath, file)
                with open(filepath, "r", encoding="utf8") as file:
                    content: str = file.read()

                for docstring_match in docstring_pattern.finditer(content):
                    docstring: str = docstring_match.group(0)
                    for identifier_match in identifier_pattern.finditer(docstring):
                        bad_identifier_count += 1

                        identifier_name: str = identifier_match.group(0)
                        start: int = docstring_match.start() + docstring.find(identifier_name)
                        line_number: int = content.count("\n", 0, start) + 1

                        print(f"{filepath}:{line_number}: '{identifier_name}' needs backticks")

    if bad_identifier_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
