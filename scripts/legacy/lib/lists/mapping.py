import csv


def get(file_name):
    mapping = {}
    with open(file_name, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        reader.next()
        for row in reader:
            mapping[row[0].lower()] = row[1]
    return mapping
