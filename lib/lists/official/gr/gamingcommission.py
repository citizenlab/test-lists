# -*- encoding: utf-8 -*-
import re
import logging

from datetime import datetime

from lists.resource import Resource


class GamblingCommissionBlockList(Resource):
    columns = [
        ("url", None),
        ("category_code", "GMB"),
        ("date_added", None),
        ("date_published", datetime.now().strftime("%Y-%m-%d")),
        ("data_format_version", "0.1"),
        ("source", "AAMS"),
        ("authority", "AAMS"),
        ("notes", None)
    ]

    name = "official/gr/gamingcommission"
    key = "url"
    download_url = "https://www.gamingcommission.gov.gr/images/epopteia-kai-elegxos/blacklist/blacklist.pdf"

    def parse(self, downloaded_file):
        from pyPdf import PdfFileReader
        reader = PdfFileReader(downloaded_file)
        contents = reader.getPage(0).extractText().split('\n')
        import pdb; pdb.set_trace()
        url = "Foo"
        yield {
            "url": url,
        }


def update(skip_download=False):
    logging.info("Updating Gambling Commission Block list")
    gambling_commission_block_list = GamblingCommissionBlockList('lists/official/gr/gamblingcommission.csv')
    gambling_commission_block_list.update(skip_download)
