from __future__ import print_function

import datetime
import os
import re
import sys
import csv
from glob import glob

VALID_URL = regex = re.compile(
        r'^(?:http)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

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

class DuplicateURL(TestListErrorWithValue):
    name = 'Duplicate URL'

class InvalidCategoryCode(TestListErrorWithValue):
    name = 'Invalid Category Code'

class InvalidCategoryDesc(TestListErrorWithValue):
    name = 'Invalid Category Description'

class InvalidDate(TestListErrorWithValue):
    name = 'Invalid Date'

def get_legacy_description_code(row):
    return row[1], row[0]

def get_new_description_code(row):
    return row[0], row[1]

def load_categories(path, get_description_code=get_new_description_code):
    code_map = {}
    with open(path, 'rb') as in_file:
        reader = csv.reader(in_file, delimiter=',')
        reader.next() # skip header
        for row in reader:
            desc, code = get_description_code(row)
            code_map[code] = desc
    return code_map

def main(source='OONI', notes='', legacy=False, fix_duplicates=False):
    all_errors = []
    total_urls = 0
    total_countries = 0
    lists_path = sys.argv[1]
    if legacy is True:
        CATEGORY_CODES = load_categories(
            os.path.join(lists_path, LEGACY_CATEGORY_CODES),
            get_legacy_description_code
        )
    else:
        CATEGORY_CODES = load_categories(
            os.path.join(lists_path, NEW_CATEGORY_CODES),
            get_new_description_code
        )
    header = ['url', 'category_code', 'category_description',
              'date_added', 'source', 'notes']
    for csv_path in glob(os.path.join(lists_path, "*")):
        if os.path.basename(csv_path).startswith('00-'):
            continue
        if not csv_path.endswith('.csv'):
            continue
        with open(csv_path, 'rb') as in_file:
            reader = csv.reader(in_file, delimiter=',')
            reader.next() # skip header
            urls_bag = set()
            errors = []
            rows = []
            duplicates = 0
	    idx = -1
            for idx, row in enumerate(reader):
                if len(row) != 6:
                    errors.append(
                        InvalidColumnNumber(csv_path, idx+2)
                    )
                    continue
                url, cat_code, cat_desc, date_added, source, notes = row
                if not VALID_URL.match(url):
                    errors.append(
                        InvalidURL(url, csv_path, idx+2)
                    )
                url = url.strip().lower()
                canonical_url = url
                if url.endswith('/'):
                    # We strip trailing / for canonical URLs
                    canonical_url = url[:-1]
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
                if canonical_url in urls_bag:
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
                urls_bag.add(canonical_url)
                rows.append(row)
            print('* {}'.format(csv_path))
            print('  {} URLs'.format(idx+1))
            print('  {} Errors'.format(len(errors)))
            all_errors += errors
            total_urls += idx+1
            total_countries += 1

        if fix_duplicates and duplicates > 0:
            rows.sort(key=lambda x: x[0].split('//')[1])
            rows.insert(0, header)
            with open(csv_path + '.fixed', 'wb') as out_file:
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
    main()
