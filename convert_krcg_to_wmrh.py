#!/usr/bin/env python
#
# Copyright (c) 2024, SchreckNet Authors
#
# SPDX-License-Identifier: BSD-3-Clause
##

import requests
import json
from datetime import datetime
from io import StringIO
# import cbor2
import zlib

KRCG_URL = "https://static.krcg.org/data/vtes.json"

def fetch_jobj():
    print(f"[+] Fetching KRCG")
    resp = requests.get(KRCG_URL)
    resp.raise_for_status()
    return resp.json()

def find_sets(jobj):
    found_sets=[]
    for set_ in [x["sets"] for x in jobj]:
        for set_name in set_.keys():
            if "promo" in set_name.lower() or "2015 Storyline Rewards" == set_name or set_name == "2018 Humble Bundle":
                set_name = 'Promo'

            if set_name in found_sets:
                continue
            found_sets.append(set_name)
    return found_sets

class Card():
    def __init__(self, jobj):
        self.id = jobj['id']
        self.name = jobj['name']
        self.card_text = jobj['card_text']
        self.printed_name = jobj.get('printed_name', None)
        self.types = jobj['types']
        self.is_crypt = "Vampire" in self.types or "Imbued" in self.types
        self.clans = jobj.get('clans', None)
        self.url = jobj['url']
        self.group = jobj.get('group', None)
        if self.group == 'ANY':
            self.group = 0
        self.capacity = jobj.get('capacity', None)
        self.disciplines = jobj.get('disciplines', None)
        self.banned = jobj.get('banned', None)
        self.pool_cost = jobj.get('pool_cost', None)
        self.blood_cost = jobj.get('blood_cost', None)
        self.sets = [set_ for set_ in jobj['sets']]
        self.scans = {}
        for scan in jobj.get('scans', []):
            self.scans[scan] = jobj['scans'][scan]
        self.rulings = jobj.get('rulings', None)
        self.token = jobj.get('token', None)

    def __str__(self):
        str_  = ""
        str_ += f"ID: {self.id}, Name: {self.name}, Printed: {self.printed_name}, Types: {self.types}, Clans: {self.clans},"
        str_ += f"Group: {self.group}, Capacity: {self.capacity}, Disciplines: {self.disciplines},"
        str_ += f"Sets: {self.sets}, Scans: {self.scans}, Banned: {self.banned}, Blood Cost: {self.blood_cost},"
        str_ += f"Pool Cost: {self.pool_cost}, Rulings: {self.rulings}"
        return str_

def find_cards(jobj):
    found_cards = []
    for jcard in jobj:
        c = Card(jcard)
        # print(f"Card: {c}")
        found_cards.append(c.__dict__)
    return found_cards

def add_info(author="SchreckNet Authors", sourceUrl=KRCG_URL):
    return {"author": author, "createdAt": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), "sourceUrl": sourceUrl, "formatVersion": 1}

def add_cards(jobj):
    _cards = {}
    _crypt = []
    _library = []
    # _unique_list = {"types":[], "clans": [], "disciplines": []}
    for card in find_cards(jobj):
        _card = {}
        # First Generic Types
        for key in ['id', 'name', 'printed_name', 'url', 'group', 'capacity', 'banned', 'pool_cost', 'blood_cost' ]:
            v = card.get(key, None)
            if v == None:
                continue
            _card[key] = v

        text = card.get('card_text', None)
        if text != None:
            _card["text"] = text
        is_crypt = card['is_crypt']

        for key in [ 'types', 'clans', 'disciplines' ]:
            if card[key] == None:
                continue
            _card[key] = card[key]

        # Next Sets
        if card.get('sets'):
            sets_ = []
            for set_ in card['sets']:
                scan = card['scans'][set_]
                sets_.append({'name': set_, 'picUrl': scan})
        _card['sets'] = sets_

        # Finaly Rulings
        rulings = []
        card_rulings = card['rulings']
        if card_rulings:
            for ruling in card_rulings:
                entry_ = {}
                refs = []
                entry_['text'] = ruling['text']
                for ref in ruling["references"]:
                    refs.append({"ref": ref['label'], "url": ref['url']})
                entry_['refs'] = refs
                rulings.append(entry_)

        _card['rulings'] = rulings
        if is_crypt:
            _crypt.append(_card)
        else:
            _library.append(_card)
        _cards["crypt"] = _crypt
        _cards["library"] = _library
    #@ import ipdb; ipdb.set_trace()
    return _cards

def generate_carddb():
    jobj = fetch_jobj()

    carddatabase = {}
    carddatabase['info'] = add_info();
    carddatabase['sets'] = find_sets(jobj);
    carddatabase['cards'] = add_cards(jobj);
    carddatabase['tokens'] = generate_tokens();

    return carddatabase

def generate_tokens():
    tokens = []

    # VTES Card Numbers work like so.
    # 100000+ library
    # 110000+ playtest library
    # 200000+ crypt
    # 210000+ playtest crypt
    # Smeea recommends using 300000+ for other stuff.

    tokens.append({"id": 300000, "name": "Anarch Counter", "text": "This vampire is considered Anarch. If this vampire changs sects, burn this counter.", "sets": [{"name": "token", "picUrl": "XXX"}]})
    tokens.append({"id": 300001, "name": "Liaison Counter", "text": "Title. This vampire is considered Liaison, unique Independent title that worth 4 votes. If this title would be contested with a younger vampire, the younger vampire immediately yields instead of contesting.", "sets": [{"name": "token", "picUrl": "XXX"}]})
    tokens.append({"id": 300002, "name": "Corruption Counter", "text": "", "sets": [{"name": "token", "picUrl": "XXX"}]})
    tokens.append({"id": 300003, "name": "Black Hand Counter", "text": "This vampire is considered Black Hand.", "sets": [{"name": "token", "picUrl": "XXX"}]})
    tokens.append({"id": 300004, "name": "Disease Counter", "text": "When this vampire is in combat at close range with another vampire, the second vampire gets a counter as well. When this vampire unlocks, he or she burns a blood or, if unable, burns the disease counter. A vampire can have only one disease counter.", "sets": [{"name": "token", "picUrl": "XXX"}]})

    return tokens


def write_file(carddb, filename):
    binary_blob = json.dumps(carddb, indent=5)

    with open(f"{filename}.json", "w") as fd:
        fd.write(binary_blob)

    compressed_blob = zlib.compress(binary_blob.encode(), level=9)
    with open(f"{filename}_compressed.dat", "wb") as fd:
        fd.write(compressed_blob)
    print(f"Created: {filename}, {len(carddb['cards']['crypt'])} Crypt Cards, {len(carddb['cards']['library'])} Library Cards, {len(carddb['tokens'])} Tokens, and {len(carddb['sets'])} Sets")

def generate_wmrh_files(generate_fcn, filename):
    carddb = generate_fcn()
    write_file(carddb, filename)

if __name__ == '__main__':
    generate_wmrh_files(generate_carddb, "schrecknet_wmrh")
    # generate_wmrh_files(generate_tokendb, "tokens.bin")
