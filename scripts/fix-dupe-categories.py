import os
import sys
import csv
from collections import Counter
from glob import glob


def fixup(url, url_category_map):
    options = list(url_category_map[url])
    #most_common = Counter(map(lambda x: x[0], options)).most_common()
    #selected_option = most_common[0][0]
    #if most_common[0][1] == most_common[1][1]:

    sorted_by_date = sorted(options, key=lambda x: x[3])
    selected_option = sorted_by_date[-1][0]
    if ".gov/" in url:
        selected_option = "GOVT"

    category_code, category_description, _, date_added, source, _ = list(filter(lambda x: x[0] == selected_option, options))[0]
    print(f"Chosen {category_code}, {category_description}, {date_added}, {source}")

    for opt in options:
        with open(opt[2]) as in_file, open(opt[2]+'.tmp', "w") as out_file:
            reader = csv.DictReader(in_file, delimiter=',')
            writer = csv.DictWriter(out_file, delimiter=',', fieldnames=reader.fieldnames, quotechar='"', lineterminator='\n')
            writer.writeheader()
            for row in reader:
                if row["url"] == url:
                    row["category_code"] = category_code
                    row["category_description"] = category_description
                writer.writerow(row)
        os.rename(opt[2]+'.tmp', opt[2])

def main():
    url_category_map = {}
    for file_name in glob("lists/*.csv"):
        if "00-" in file_name:
            continue
        with open(file_name) as in_file:
            reader = csv.DictReader(in_file, delimiter=',')
            for row in reader:
                url = row["url"]
                url_category_map[url] = url_category_map.get(url, [])
                url_category_map[url].append(
                        (row["category_code"], row["category_description"], file_name, row["date_added"], row["source"], row["notes"])
                )

    to_fixup = []
    for url in sorted(url_category_map.keys()):
        category_tup = url_category_map[url]
        category_codes = set(list(map(lambda x: x[0], category_tup)))
        if len(category_codes) > 1:
            to_fixup.append((url, category_codes))

    print(f"dupes {len(to_fixup)}")
    for url, category_codes in to_fixup:
            print(f"{url}: {category_codes}")
            fixup(url, url_category_map)

if __name__ == "__main__":
    main()
