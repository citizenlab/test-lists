import logging

from hashlib import sha1
from datetime import datetime

from lists.services import base


class Bridges(base.Service):
    columns = [
        ("address", None),
        ("transport_name", "vanilla"),
        ("fingerprint", None),
        ("hashed_fingerprint", None),
        ("name", "tor/bridges"),
        ("category_code", "ANON"),
        ("date_added", datetime.now().strftime("%Y-%m-%d")),
        ("date_published", datetime.now().strftime("%Y-%m-%d")),
        ("data_format_version", "0.1"),
        ("source", "The Tor Project"),
        ("notes", None)
    ]


class TorBrowserBridges(Bridges):
    key = "address"
    download_url = "https://gitweb.torproject.org/builders/tor-browser-bundle.git/plain/Bundle-Data/PTConfigs/bridge_prefs.js"

    def parse(self, downloaded_file):
        for line in downloaded_file:
            line = line.strip()
            if not line.startswith('pref("extensions.torlauncher.default_bridge.'):
                continue
            logging.debug("Looking at %s" % line)
            item = {}
            address = line.split(", ")[1].replace('"', '').replace(");", "")
            parts = address.split(" ")
            transport_name = parts[0]

            if transport_name not in ["meek", "flashproxy"]:
                item["fingerprint"] = parts[2]
                fingerprint = item["fingerprint"].decode('hex')
                item["hashed_fingerprint"] = sha1(fingerprint).hexdigest()

            item["address"] = address
            item["transport_name"] = transport_name
            yield item


def update():
    tor_browser_bridges = TorBrowserBridges('lists/services/tor/bridges.csv')
    tor_browser_bridges.update()
