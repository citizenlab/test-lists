import logging

from datetime import datetime

from lists.resource import Resource

class DirectoryAuthority(Resource):
    columns = [
            ("address", None),
            ("nickname", None),
            ("v3_ident", None),
            ("fingerprint", None),
            ("or_port", None),
            ("dir_port", None),
            ("bridge", False),
            ("date_added", datetime.now().strftime("%Y-%m-%d")),
            ("date_published", datetime.now().strftime("%Y-%m-%d")),
            ("data_format_version", "0.1"),
            ("source", "The Tor Project"),
            ("notes", None)
    ]

    name = "tor/dir_auths"
    key = "address"
    download_url = "https://gitweb.torproject.org/tor.git/plain/src/or/config.c"

    def parse(self, downloaded_file):
        raw_lines = []
        dir_auths = []
        new_dir = ""
        found_line = False
        signature = "static const char *default_authorities[] = {"

        for line in downloaded_file:
            line = line.strip()
            if line != signature and not found_line:
                continue
            elif line == signature:
                found_line = True
                continue
            elif line == "};" or line == "NULL":
                break
            else:
                raw_lines.append(line)

        for item in raw_lines:
            item = item.strip('"')
            if "," in item:
                item = item.strip(",")
                new_dir = new_dir + item
                dir_auths.append(new_dir)
                new_dir = ""
            else:
                new_dir = new_dir + item

        for directory in dir_auths:
            item = {}
            item["nickname"] = directory.split(" ")[0]
            # is hardcoding fingerprint length safe?
            item["fingerprint"] = directory[-50:-1].replace(" ","")

            for part in directory.split(" "):
                if "orport" in part:
                    part = part.strip("orport=")
                    item["or_port"] = part
                elif "v3ident" in part:
                    part = part.strip("v3ident=")
                    item["v3_ident"] = part
                elif "bridge" in part:
                    item["bridge"] = True
                elif isgoodipv4(part):
                    item["address"] = part.split(":")[0]
                    item["dir_port"] = part.split(":")[1]

            yield item

def isgoodipv4(s):
    s = s.split(':')[0]
    pieces = s.split('.')
    if len(pieces) != 4: return False
    try: return all(0<=int(p)<256 for p in pieces)
    except ValueError: return False

def update():
    tor_directory_authorities = DirectoryAuthority("lists/services/tor/dir_auths.csv")
    tor_directory_authorities.update()
