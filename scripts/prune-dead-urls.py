import argparse
import datetime
import os
import re
import sys
import csv
import time
from glob import glob
from urllib.parse import urlparse

import socket
import concurrent.futures

def prune_dead_urls(csv_path, domain_map):
    with open(csv_path, 'r') as in_file, \
         open(csv_path + '.tmp', 'w') as out_file:
        reader = csv.reader(in_file, delimiter=',')
        writer = csv.writer(out_file, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(next(reader))
        for idx, row in enumerate(reader):
            url = row[0]
            domain = urlparse(url).netloc.split(':')[0]
            if domain_map[domain] is False:
                continue
            writer.writerow(row)
    os.rename(csv_path + '.tmp', csv_path)

def resolve_domain(domain, idx, start_time):
    delta = time.time() - start_time
    try:
        socket.getaddrinfo(domain, 0)
        print(f"resolving {domain} ({idx} - {delta}) ✓")
        return True
    except socket.gaierror:
        print(f"resolving {domain} ({idx} - {delta}) ✗")
        return False
    except Exception as exc:
        print(f"other failure in {domain} ({idx} - {delta}) ✗")
        print(exc)
        return False

def main(lists_path):
    domain_set = set()
    url_lists = []
    for csv_path in glob(os.path.join(lists_path, "*")):
        if os.path.basename(csv_path).startswith('00-') or \
                os.path.basename(csv_path).startswith('official'):
            continue
        with open(csv_path, 'r') as in_file:
            reader = csv.reader(in_file, delimiter=',')
            next(reader) # Skip header
            for idx, row in enumerate(reader):
                url = row[0]
                domain = urlparse(url).netloc.split(':')[0]
                domain_set.add(domain)
        url_lists.append(csv_path)

    start_time = time.time()
    domain_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        future_to_domain = {
                executor.submit(resolve_domain, domain, idx, start_time):
                domain for idx, domain in enumerate(domain_set)
        }
        for future in concurrent.futures.as_completed(future_to_domain):
            domain = future_to_domain[future]
            status = future.result()
            domain_map[domain] = status
    for csv_path in url_lists:
        prune_dead_urls(csv_path, domain_map)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check if URLs in the test list are OK')
    parser.add_argument('lists_path', metavar='LISTS_PATH', help='path to the test list')
    args = parser.parse_args()
    main(args.lists_path)
