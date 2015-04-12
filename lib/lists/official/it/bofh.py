# -*- encoding: utf-8 -*-
import logging

from datetime import datetime
from HTMLParser import HTMLParser

from lists.resource import Resource


class BOFHParser(HTMLParser):
    in_table = False
    in_td = False
    got_url = False

    def __init__(self):
        HTMLParser.__init__(self)
        self.row = []
        self.items = []

    def handle_starttag(self, tag, attrs):
        if tag == "tbody":
            self.in_table = True
        if self.in_table and tag == "td":
            self.in_td = True

    def handle_endtag(self, tag):
        if tag == "tbody":
            self.in_table = False
        if self.in_table and tag == "td":
            self.in_td = False
        if self.in_table and tag == "tr":
            if self.got_url:
                self.items.append(self.row)
            self.row = []
            self.got_url = False
        if self.in_td and tag == "a":
            self.got_url = True

    def handle_data(self, data):
        if self.in_td is True:
            self.row.append(data)


def map_category(italian_category):
    cats = {
        "Agenzia immobiliare": "", # XXX NEWCATEGORY?
        "Annunci personali": "DATE",
        "Antisemitismo": "HATE",
        "Bestialismo": "PORN", # XXX NEWCAT?
        "Discussioni sull'età del consenso": "HATE", # XXX this is actually CP. NEWCAT?
        "Enigmistica": "GAME", # XXX NEWCATEGORY? this is specifically crosswords
        "Farmaci": "ALDR",
        "File locker": "HACK",
        "Forum": "GRP", # XXX NEWCATEGORY?
        "Giornale online": "FEXP", # XXX Generic news website NEWCATEGORY?
        "Ignoto": "MISC",
        "Live streaming": "MMED", # XXX NEWCATEGORY?
        "Maglie da calcio": "COMM", # XXX NEWCATEGORY?
        "Motore di ricerca per torrent": "P2P",
        "Phishing": "HACK", # XXX NEWCATEGORY?
        "Pornografia amatoriale": "PORN",
        "Portale di link": "MISC", # XXX NEWCAT?
        "Registro medici": "MISC",
        "Reverse proxy verso btjunkie.org": "ANON",
        "Riviste": "FEXP", # XXX NEWCAT? Magazines
        "SMS": "MISC", # XXX NEWCAT?
        "Sementi?": "MISC", # XXX NEWCAT? Seeds
        "Servizi finanziari": "DEV", # XXX NEWCAT?
        "Sito personale": "MISC", #XXX NEWCAT?
        "Studio legale": "MISC", # XXX LEGAL
        "Trading online": "DEV", # XXX NEWCAT this is either DEV of Gambling
        "Valutazione auto usate": "COMM", # XXX NEWCAT?
        "Venditori di abbigliamento": "COMM", # XXX NEWCAT? Stores
        "Venditori di ceramiche": "COMM",
        "Venditori di elettronica": "COMM",
        "Venditori di occhiali": "COMM",
        "Venditori di orologi": "COMM",
        "Venditori di scarpe": "COMM",
        "Whistleblowing": "FEXP"
    }
    for key, value in cats.items():
        if italian_category.startswith(key):
            return value
    return "MISC"


class BOFHBlockList(Resource):
    columns = [
        ("url", None),
        ("name", "official/it/bofh"),
        ("category_code", None),
        ("date_added", None),
        ("date_published", datetime.now().strftime("%Y-%m-%d")),
        ("data_format_version", "0.1"),
        ("source", "censura.bofh.it"),
        ("authority", None),
        ("notes", None)
    ]

    key = "url"
    download_url = "http://censura.bofh.it/elenchi.html"

    def parse(self, downloaded_file):
        logging.info("Parsing BOFH list")
        parser = BOFHParser()
        parser.feed(''.join(downloaded_file.readlines()))
        for row in parser.items:
            notes = None
            if len(row) > 4:
                notes = row[4]
            item = {
                "date_added": row[0],
                "url": row[1],
                "authority": row[3],
                "category_code": map_category(row[2]),
                "category_it_name": row[2],
                "notes": notes
            }
            yield item


def update():
    bofh_block_list = BOFHBlockList('lists/official/it/bofh.csv')
    bofh_block_list.update()
