import os
import csv
import shutil
import logging

from datetime import datetime
from lists import https


class AlreadyPresent(Exception):
    pass


class Resource(object):
    columns = [
        ("category_code", "MISC"),
        ("date_added", datetime.now().strftime("%Y-%m-%d")),
        ("date_published", datetime.now().strftime("%Y-%m-%d")),
        ("data_format_version", "0.1"),
        ("source", "unknown"),
        ("notes", None)
    ]

    name = "resource"
    key = "notes"

    download_url = None

    def __init__(self, dst_file_name="services.csv"):
        self.dst_file_name = dst_file_name

    def write_header(self):
        if not os.path.isfile(self.dst_file_name):
            with open(self.dst_file_name, 'w') as f:
                writer = csv.writer(f, delimiter=',', quotechar='"')
                writer.writerow([x[0] for x in ["name"] + self.columns])

    def already_present(self, item):
        if self.key not in item.keys():
            return False
        for idx, c in enumerate(self.columns):
            if c[0] == self.key:
                break

        with open(self.dst_file_name, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            reader.next()
            for row in reader:
                if row[idx] == item[self.key]:
                    return True
        return False

    def write_row(self, item):
        if self.already_present(item):
            raise AlreadyPresent

        row = [self.name]
        for column in self.columns:
            if column[0] in item.keys():
                row.append(item[column[0]])
            else:
                row.append(column[1])

        with open(self.dst_file_name, 'ab') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(row)

    @property
    def dst_filename(self):
        timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%SZ")
        dst_filename = "%s-%s.dat" % (os.path.basename(self.name),
                                      timestamp)
        return os.path.join(self.dst_directory, dst_filename)

    @property
    def dst_directory(self):
        return os.path.join(
            'downloads',
            os.path.dirname(self.name)
        )

    def download(self, url=None, dst_filename=None):
        if self.download_url is None and url is None:
            return

        if dst_filename is None:
            dst_filename = self.dst_filename

        try:
            os.makedirs(self.dst_directory)
        except OSError as exc:
            if exc.errno != 17:
                raise exc

        downloaded_file = open(dst_filename, "w+")
        result = https.open(self.download_url)
        shutil.copyfileobj(result, downloaded_file)
        downloaded_file.seek(0)
        return downloaded_file

    def parse(self, downloaded_file):
        for line in downloaded_file:
            yield {"notes": line.strip()}

    def update(self, skip_download=False):
        self.write_header()
        if skip_download:
            downloaded_file = open(os.path.join(self.dst_directory,
                                                self.dst_filename))
        else:
            downloaded_file = self.download()
        for item in self.parse(downloaded_file):
            try:
                self.write_row(item)
            except AlreadyPresent:
                logging.info("Item %s already present" % item)
        downloaded_file.close()
