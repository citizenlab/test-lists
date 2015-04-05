# -*- encoding: utf-8 -*-
import re
import logging

from datetime import datetime

from lists.resource import Resource


class AAMSBlockList(Resource):
    columns = [
        ("url", None),
        ("name", "official/it/aams"),
        ("category_code", "GMB"),
        ("date_added", None),
        ("date_published", datetime.now().strftime("%Y-%m-%d")),
        ("data_format_version", "0.1"),
        ("source", "AAMS"),
        ("authority", "AAMS"),
        ("notes", None)
    ]

    key = "url"
    download_url = "ftp://ftp.finanze.it/pub/monopoli/elenco_siti_inibiti.rtf"

    def parse(self, downloaded_file):
        logging.info("Parsing AAMS Block list")
        from pyth.plugins.rtf15.reader import Rtf15Reader, Group

        def _handle_ansi_escape(self, code):
            try:
                Group._handle_ansi_escape(self, code)
            except:
                self.content.append(" ")
        Group.handle_ansi_escape = _handle_ansi_escape

        doc = Rtf15Reader.read(downloaded_file)
        doc.content[0].content
        siti = doc.content[0].content[3].content[0]
        for sito in siti.split("\n"):
            m = re.search("(\d+)(.*)", sito)
            if m:
                url = m.group(2)
                yield {
                    "url": url,
                }


def update():
    logging.info("Updating AAMS Block list")
    aams_block_list = AAMSBlockList('lists/official/it/bofh.csv')
    aams_block_list.update()
