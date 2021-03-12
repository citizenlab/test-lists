#!/usr/bin/env python

from __future__ import print_function

import argparse
import datetime
import os
import re
import sys
import csv
from glob import glob

try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse

VALID_URL = regex = re.compile(
        r'^(?:http)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

BAD_CHARS = ["\r", "\n", "\t", "\\"]

CATEGORY_CODES = {}
COUNTRY_CODES = {}

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
    name = 'Test List Error'
    def __init__(self, csv_path, line_number):
        self.csv_path = csv_path
        self.line_number = line_number

    def print(self):
        print('{} (line {}): {}'.format(
            self.csv_path, self.line_number, self.name
        ))

class TestListErrorWithValue(TestListError):
    def __init__(self, value, csv_path, line_number):
        super(TestListErrorWithValue, self).__init__(csv_path, line_number)
        self.value = value

    def print(self):
        print('{} (line {}): {} "{}"'.format(
            self.csv_path, self.line_number, self.name, self.value
        ))

class InvalidColumnNumber(TestListError):
    name = 'Invalid Column Number'

class InvalidURL(TestListErrorWithValue):
    name = 'Invalid URL'

class InvalidNotes(TestListErrorWithValue):
    name = 'Invalid Notes'

class InvalidSource(TestListErrorWithValue):
    name = 'Invalid Source'

class DuplicateURL(TestListErrorWithValue):
    name = 'Duplicate URL'

class InvalidCategoryCode(TestListErrorWithValue):
    name = 'Invalid Category Code'

class InvalidCategoryDesc(TestListErrorWithValue):
    name = 'Invalid Category Description'

class InvalidDate(TestListErrorWithValue):
    name = 'Invalid Date'

class DuplicateURLWithGlobalList(TestListErrorWithValue):
    name = "Duplicate URL between Local List and Global List"

def get_legacy_description_code(row):
    return row[1], row[0]

def get_new_description_code(row):
    return row[0], row[1]

def load_categories(path, get_description_code=get_new_description_code):
    code_map = {}
    with open(path, 'r') as in_file:
        reader = csv.reader(in_file, delimiter=',')
        next(reader) # skip header
        for row in reader:
            desc, code = get_description_code(row)
            code_map[code] = desc
    return code_map

def load_global_list(path):
    check_list = set()
    with open(path, 'r') as in_file:
        reader = csv.reader(in_file, delimiter=',')
        for idx, row in enumerate(reader):
            if idx != 0 and (len(row) == 6):
                check_list.add(row[0])
    return check_list

def main(lists_path, fix_duplicates=False, fix_slash=False):
    all_errors = []
    total_urls = 0
    total_countries = 0
    CATEGORY_CODES = load_categories(
        os.path.join(lists_path, NEW_CATEGORY_CODES),
        get_new_description_code
    )
    header = ['url', 'category_code', 'category_description',
              'date_added', 'source', 'notes']
    # preload the global list to check against looking for dupes
    global_urls_bag = load_global_list(os.path.join(lists_path, "global.csv"))
    for csv_path in glob(os.path.join(lists_path, "*")):
        if os.path.basename(csv_path).startswith('00-'):
            continue
        if not csv_path.endswith('.csv'):
            continue
        with open(csv_path, 'r') as in_file:
            reader = csv.reader(in_file, delimiter=',')
            next(reader) # skip header
            urls_bag = set()
            errors = []
            rows = []
            duplicates = 0
            without_slash = 0
            idx = -1
            for idx, row in enumerate(reader):
                if len(row) != 6:
                    errors.append(
                        InvalidColumnNumber(csv_path, idx+2)
                    )
                    continue
                url, cat_code, cat_desc, date_added, source, notes = row
                if not VALID_URL.match(url) or any([c in url for c in BAD_CHARS]):
                    errors.append(
                        InvalidURL(url, csv_path, idx+2)
                    )
                if url != url.strip():
                    errors.append(
                        InvalidURL(url, csv_path, idx+2)
                    )
                url_p = urlparse(url)
                if url_p.path == "":
                    without_slash += 1
                    errors.append(
                        InvalidURL(url, csv_path, idx+2)
                    )
                    row[0] = row[0] + "/"
                if os.path.basename(csv_path) != "global.csv":
                    if url in global_urls_bag:
                        errors.append(
                            DuplicateURLWithGlobalList(url, csv_path, idx+2)
                        )
                        if fix_duplicates:
                            duplicates += 1
                            continue

                try:
                    cat_description = CATEGORY_CODES[cat_code]
                except KeyError:
                    errors.append(
                        InvalidCategoryCode(cat_code, csv_path, idx+2)
                    )
                if cat_description != cat_desc:
                    errors.append(
                        InvalidCategoryDesc(cat_desc, csv_path, idx+2)
                    )
                if url in urls_bag:
                    if not fix_duplicates:
                        errors.append(
                            DuplicateURL(url, csv_path, idx+2)
                        )
                    duplicates += 1
                    continue
                if not is_valid_date(date_added):
                    errors.append(
                        InvalidDate(date_added, csv_path, idx+2)
                    )
                if any([c in notes for c in BAD_CHARS]):
                    errors.append(
                        InvalidNotes(notes, csv_path, idx+2)
                    )
                if any([c in source for c in BAD_CHARS]):
                    errors.append(
                        InvalidSource(source, csv_path, idx+2)
                    )
                urls_bag.add(url)
                rows.append(row)
            print('* {}'.format(csv_path))
            print('  {} URLs'.format(idx+1))
            print('  {} Errors'.format(len(errors)))
            all_errors += errors
            total_urls += idx+1
            total_countries += 1

        if fix_slash and without_slash > 0:
            print('Fixing slash in %s' % csv_path)
            rows.insert(0, header)
            with open(csv_path + '.fixed', 'w') as out_file:
                csv_writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
                csv_writer.writerows(rows)
            os.rename(csv_path + '.fixed', csv_path)

        if fix_duplicates and duplicates > 0:
            rows.sort(key=lambda x: x[0].split('//')[1])
            rows.insert(0, header)
            with open(csv_path + '.fixed', 'w') as out_file:
                csv_writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
                csv_writer.writerows(rows)
            print('Sorting %s - Found %d duplicates' % (csv_path, duplicates))
            os.rename(csv_path + '.fixed', csv_path)

    print('----------')
    print('Analyzed {} URLs in {} countries'.format(total_urls, total_countries))
    if len(all_errors) == 0:
        print('ALL OK')
        sys.exit(0)

    print("{} errors present".format(len(all_errors)))
    for error in all_errors:
        error.print()
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check that the test lists are OK')
    parser.add_argument('lists_path', metavar='LISTS_PATH', help='path to the test list')
    parser.add_argument('--fix-duplicates', action='store_true')
    parser.add_argument('--fix-slash', action='store_true')

    args = parser.parse_args()
    main(args.lists_path, fix_duplicates=args.fix_duplicates, fix_slash=args.fix_slash)
