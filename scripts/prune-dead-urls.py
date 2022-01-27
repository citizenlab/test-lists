import argparse
import datetime
import random
import os
import re
import sys
import csv
import time
from glob import glob
from urllib.parse import urlparse

import socket
import concurrent.futures

def prune_dead_urls(csv_path, failed_domains):
    with open(csv_path, 'r') as in_file, \
         open(csv_path + '.tmp', 'w') as out_file:
        reader = csv.reader(in_file, delimiter=',')
        writer = csv.writer(out_file, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(next(reader))
        for idx, row in enumerate(reader):
            url = row[0]
            domain = urlparse(url).netloc.split(':')[0]
            if domain in failed_domains:
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

def get_failed_domains(domain_list):
    start_time = time.time()
    failed_domains = set()
    for idx, domain in enumerate(domain_list):
        if resolve_domain(domain, idx, start_time) == False:
            failed_domains.add(domain)
    return failed_domains

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

    failed_domains = get_failed_domains(list(domain_set))
    print("## Going for a second pass ##")
    shuffled_domains = list(failed_domains)
    random.shuffle(shuffled_domains)
    failed_domains_second_pass = get_failed_domains(shuffled_domains)

    failed_domain_set = failed_domains.intersection(failed_domains_second_pass)
    schroedinger_domains = failed_domains - failed_domains_second_pass
    if len(schroedinger_domains) > 0:
        print(f"schroedinger domains {schroedinger_domains}")

    for csv_path in url_lists:
        prune_dead_urls(csv_path, failed_domain_set)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check if URLs in the test list are OK')
    parser.add_argument('lists_path', metavar='LISTS_PATH', help='path to the test list')
    args = parser.parse_args()
    main(args.lists_path)
