import datetime
import os
import re
import sys
import csv
import json
from glob import glob

from urllib.parse import urlparse

VALID_URL = regex = re.compile(
    r"^(?:http)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)

BAD_CHARS = ["\r", "\n", "\t", "\\"]


NEW_CATEGORY_CODES = "00-LEGEND-new_category_codes.csv"
LEGACY_CATEGORY_CODES = "00-LEGEND-category_codes.csv"
COUNTRY_CODES = "00-LEGEND-country_codes.csv"


def is_valid_date(d):
    try:
        if datetime.datetime.strptime(d, "%Y-%m-%d").date().isoformat() == d:
            return True
    except Exception:
        pass
    return False


class TestListError(object):
    name = "Test List Error"

    def __init__(self, csv_path, line_number):
        self.csv_path = csv_path
        self.line_number = line_number

    def print(self):
        print("{} (line {}): {}".format(self.csv_path, self.line_number, self.name))


class TestListErrorWithValue(TestListError):
    def __init__(self, value, csv_path, line_number, details=None):
        super(TestListErrorWithValue, self).__init__(csv_path, line_number)
        self.value = value
        self.details = details

    def print(self):
        msg = '{} (line {}): {} "{}"'.format(
            self.csv_path, self.line_number, self.name, self.value
        )
        if self.details:
            msg += " ({})".format(self.details)
        print(msg)


class InvalidHeader(TestListError):
    name = "Invalid Header"


class InvalidColumnNumber(TestListError):
    name = "Invalid Column Number"


class InvalidURL(TestListErrorWithValue):
    name = "Invalid URL"


class InvalidNotes(TestListErrorWithValue):
    name = "Invalid Notes"


class InvalidSource(TestListErrorWithValue):
    name = "Invalid Source"


class DuplicateURL(TestListErrorWithValue):
    name = "Duplicate URL"


class InvalidCategoryCode(TestListErrorWithValue):
    name = "Invalid Category Code"


class InvalidCategoryDesc(TestListErrorWithValue):
    name = "Invalid Category Description"


class InvalidDate(TestListErrorWithValue):
    name = "Invalid Date"


class DuplicateURLWithGlobalList(TestListErrorWithValue):
    name = "Duplicate URL between Local List and Global List"


def get_legacy_description_code(row):
    return row[1], row[0]


def get_new_description_code(row):
    return row[0], row[1]


def load_categories(path, get_description_code=get_new_description_code):
    code_map = {}
    with open(path, "r") as in_file:
        reader = csv.reader(in_file, delimiter=",")
        next(reader)  # skip header
        for row in reader:
            desc, code = get_description_code(row)
            code_map[code] = desc
    return code_map


def load_global_list(path):
    check_list = set()
    with open(path, "r") as in_file:
        reader = csv.reader(in_file, delimiter=",", quotechar="'")
        for idx, row in enumerate(reader):
            if idx != 0 and (len(row) == 6):
                check_list.add(row[0])
    return check_list


VALID_NOTES_JSON_KEYS = ["notes"]


def validate_notes_keys(notes):
    for k in notes.keys():
        assert k in VALID_NOTES_JSON_KEYS, f"invalid notes key {k}"


ERR_NOSLASH = "No trailing slash"


def check(url):
    if not VALID_URL.match(url):
        return "No match"
    elif any([c in url for c in BAD_CHARS]):
        return "Bad chars"
    elif url != url.strip():
        return "Extra spaces at ends"
    elif urlparse(url).path == "":
        return ERR_NOSLASH


TEST_LISTS_HEADER = [
    "url",
    "category_code",
    "category_description",
    "date_added",
    "source",
    "notes",
]


class TestListProcessor:
    def __init__(
        self,
        csv_path,
        category_codes,
        global_urls_bag,
        fix_duplicates=False,
        fix_slash=False,
        fix_notes=False,
    ):
        self.csv_path = csv_path
        self.global_urls_bag = global_urls_bag
        self.fix_duplicates = fix_duplicates
        self.fix_slash = fix_slash
        self.fix_notes = fix_notes
        self.errors = []
        self.category_codes = category_codes

        self.rows = [TEST_LISTS_HEADER]
        self.urls_bag = set()
        self.errors = []
        self.idx = -1

    def open(self):
        return open(self.csv_path, "r", encoding="utf-8")

    def process_row(self, idx, row):
        if len(row) != 6:
            self.errors.append(InvalidColumnNumber(self.csv_path, idx + 2))
            return

        url, cat_code, cat_desc, date_added, source, notes = row
        err = check(url)
        if err:
            self.errors.append(InvalidURL(url, self.csv_path, idx + 2, details=err))
            if err == ERR_NOSLASH and self.fix_slash:
                row[0] = row[0] + "/"

        if notes.startswith("{"):
            try:
                d = json.loads(notes)
                validate_notes_keys(d)
            except AssertionError as exc:
                err = f"{exc} in {notes}"
                self.errors.append(
                    InvalidNotes(err, self.csv_path, idx + 2, details=err)
                )
            except json.decoder.JSONDecodeError:
                self.errors.append(
                    InvalidNotes(notes, self.csv_path, idx + 2, details=err)
                )
        elif self.fix_notes:
            row[5] = json.dumps({"notes": notes})

        if os.path.basename(self.csv_path) != "global.csv":
            if url in self.global_urls_bag:
                self.errors.append(
                    DuplicateURLWithGlobalList(url, self.csv_path, idx + 2)
                )
                if self.fix_duplicates:
                    return

        try:
            cat_description = self.category_codes[cat_code]
        except KeyError:
            self.errors.append(InvalidCategoryCode(cat_code, self.csv_path, idx + 2))
        if cat_description != cat_desc:
            self.errors.append(InvalidCategoryDesc(cat_desc, self.csv_path, idx + 2))
        if url in self.urls_bag:
            if not self.fix_duplicates:
                self.errors.append(DuplicateURL(url, self.csv_path, idx + 2))
            return

        if not is_valid_date(date_added):
            self.errors.append(InvalidDate(date_added, self.csv_path, idx + 2))
        if any([c in notes for c in BAD_CHARS]):
            self.errors.append(InvalidNotes(notes, self.csv_path, idx + 2))
        if any([c in source for c in BAD_CHARS]):
            self.errors.append(InvalidSource(source, self.csv_path, idx + 2))
        self.urls_bag.add(url)

        self.rows.append(row)

    def write_fixed(self):
        with open(self.csv_path + ".fixed", "w") as out_file:
            csv_writer = csv.writer(
                out_file, quoting=csv.QUOTE_MINIMAL, quotechar="'", lineterminator="\n"
            )
            csv_writer.writerows(self.rows)
        os.rename(self.csv_path + ".fixed", self.csv_path)


def lint_lists(lists_path, fix_duplicates=False, fix_slash=False, fix_notes=False):
    all_errors = []
    total_urls = 0
    total_countries = 0

    category_codes = load_categories(
        os.path.join(lists_path, NEW_CATEGORY_CODES), get_new_description_code
    )

    # preload the global list to check against looking for dupes
    global_urls_bag = load_global_list(os.path.join(lists_path, "global.csv"))
    for csv_path in glob(os.path.join(lists_path, "*")):
        if os.path.basename(csv_path).startswith("00-"):
            continue
        if not csv_path.endswith(".csv"):
            continue
        processor = TestListProcessor(
            csv_path,
            category_codes=category_codes,
            global_urls_bag=global_urls_bag,
            fix_duplicates=fix_duplicates,
            fix_notes=fix_notes,
            fix_slash=fix_slash,
        )
        with processor.open() as in_file:
            reader = csv.reader(in_file, delimiter=",", quotechar="'")
            first_line = next(reader)
            if first_line != TEST_LISTS_HEADER:
                processor.errors.append(InvalidHeader(csv_path, 0))

            for idx, row in enumerate(reader):
                processor.process_row(idx, row)

            if fix_slash or fix_duplicates or fix_notes:
                processor.write_fixed()

            print(f"* {processor.csv_path}")
            print(f"  {idx+1} URLs")
            print(f"  {len(processor.errors)} Errors")

            all_errors += processor.errors
            total_urls += idx + 1
            total_countries += 1

    print("----------")
    print("Analyzed {} URLs in {} countries".format(total_urls, total_countries))
    if len(all_errors) == 0:
        print("ALL OK")
        sys.exit(0)

    print("{} errors present".format(len(all_errors)))
    for error in all_errors:
        error.print()
    sys.exit(1)
