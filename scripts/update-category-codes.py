#!/usr/bin/env python
# This script is used to migrate the testing lists from the old category
# codes to the new category codes.
# It must be run from the root of the repository like so:
#
# $ python scripts/update-category-codes.py

import os
import sys
import csv
import json
import shutil
import logging

from datetime import datetime
from tempfile import NamedTemporaryFile

from glob import glob


def convert_categories(file_name, category_mapping):
    tempfile = NamedTemporaryFile(delete=False)
    logging.debug("Opening CSV file %s" % file_name)
    with open(file_name, 'rb') as csvfile, tempfile:
        reader = csv.reader(csvfile, delimiter=',')
        writer = csv.writer(tempfile, delimiter=',', quotechar='"')
        header = reader.next()
        writer.writerow(header)
        for row in reader:
            new_category = category_mapping[row[1].upper()]
            logging.debug("%s -> %s" % (row[1], new_category))
            row[1] = new_category['code']
            row[2] = new_category['desc']
            writer.writerow(row)

    shutil.move(tempfile.name, file_name)

def fix_directory(path='lists/'):
    category_mapping = {}
    with open(os.path.join(path, '00-LEGEND-new_category_codes.csv')) as in_file:
        reader = csv.reader(in_file, delimiter=',')
        reader.next()
        for desc, new_code, old_codes, _ in reader:
            for old_code in old_codes.strip().split(" "):
                category_mapping[old_code] = {
                    "code": new_code,
                    "desc": desc
                }
            category_mapping[new_code] = {
                "code": new_code,
                "desc": desc
            }
    for file_name in glob(path+'*.csv'):
        if '00-' in file_name:
            continue
        logging.info("Converting %s" % (file_name))
        try:
            convert_categories(file_name, category_mapping)
        except Exception as exc:
            logging.error(exc)
            logging.error("Error in generating %s" % file_name)
            sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    fix_directory()
