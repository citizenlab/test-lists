from __future__ import print_function

from datetime import datetime
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
    lists_path = sys.argv[1]
    date_added = datetime.now().strftime("%Y-%m-%d")
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
            rows = []
            duplicates = 0
            for idx, row in enumerate(reader):
                if len(row) != 6:
                    print("INVALID NUMBER OF COLUMNS on line {} of {}".format(
                          idx+2, csv_path), file=sys.stderr)
                    sys.exit(4)
                url, cat_code, cat_desc, date_added, source, notes = row
                url = url.strip().lower()
                if not VALID_URL.match(url):
                    print("INVALID URL {} on line {} of {}".format(
                                url, idx+2, csv_path),
                          file=sys.stderr)
                    sys.exit(1)
                try:
                    cat_description = CATEGORY_CODES[cat_code]
                except KeyError:
                    print("INVALID category {} on line {} of {}".format(
                            cat_code, idx+2, csv_path), file=sys.stderr)
                    sys.exit(2)
                if cat_description != cat_desc:
                    print("INVALID category desc \"{}\" on line {} of {}".format(
                            cat_desc, idx+2, csv_path), file=sys.stderr)
                    sys.exit(5)
                if url in urls_bag:
                    if not fix_duplicates:
                        print("DUPLICATE URL {} on line {} of {}".format(
                              url, idx+2, csv_path), file=sys.stderr)
                        sys.exit(3)
                    duplicates += 1
                    continue
                urls_bag.add(url)
                rows.append(row)
        if fix_duplicates:
            rows.sort(key=lambda x: x[0].split('//')[1])
            rows.insert(0, header)
            with open(csv_path + '.fixed', 'w') as out_file:
                csv_writer = csv.writer(out_file)
                csv_writer.writerows(rows)
            print("Sorting %s - Found %d duplicates" % (csv_path, duplicates))
            os.rename(csv_path + '.fixed', csv_path)

if __name__ == "__main__":
    main()
