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

try:
    from lxml import etree
    mode = 'lxml'
except ImportError:
    import xml.etree.ElementTree as etree
    mode = 'Python etree'
print(f"[+] Operating with {mode}")

KRCG_URL = "https://static.krcg.org/data/vtes.json"
SCHEMA_LOCATION = "https://raw.githubusercontent.com/Stolas/SchreckNet-WMRH-CardDB/master/cards.xsd"

def fetch_jobj():
    print(f"[+] Fetching KRCG")
    resp = requests.get(KRCG_URL)
    resp.raise_for_status()
    return resp.json()

def get_short_name(name):
    nameLookupDict = {}
    nameLookupDict["Jyhad"] = "Jyhad"
    nameLookupDict["Vampire: The Eternal Struggle"] = "V:TES"
    nameLookupDict["Dark Sovereigns"] = "DS"
    nameLookupDict["Ancient Hearts"] = "AH"
    nameLookupDict["Sabbat"] = "Sabbat"
    nameLookupDict["Sabbat War"] = "SW"
    nameLookupDict["Final Nights"] = "FN"
    nameLookupDict["Bloodlines"] = "BL"
    nameLookupDict["Camarilla Edition"] = "CE"
    nameLookupDict["Anarchs"] = "Anarchs"
    nameLookupDict["Black Hand"] = "BH"
    nameLookupDict["Gehenna"] = "Gehenna"
    nameLookupDict["Tenth Anniversary"] = "Tenth"
    nameLookupDict["Kindred Most Wanted"] = "KMW"
    nameLookupDict["Legacies of Blood"] = "LoB"
    nameLookupDict["Nights of Reckoning"] = "NoR"
    nameLookupDict["Third Edition"] = "Third"
    nameLookupDict["Sword of Caine"] = "SoC"
    nameLookupDict["Lords of the Night"] = "LotN"
    nameLookupDict["Blood Shadowed Court"] = "BSC"
    nameLookupDict["Twilight Rebellion"] = "TR"
    nameLookupDict["Keepers of Tradition"] = "KoT"
    nameLookupDict["Ebony Kingdom"] = "EK"
    nameLookupDict["Heirs to the Blood"] = "HttB"
    nameLookupDict["Danse Macabre"] = "DM"
    nameLookupDict["The Unaligned"] = "TA"
    nameLookupDict["Anarch Unbound"] = "AU"
    nameLookupDict["Lost Kindred"] = "LK"
    nameLookupDict["Sabbat Preconstructed"] = "SP"
    nameLookupDict["Fifth Edition"] = "V5"
    nameLookupDict["Fifth Edition (Anarch)"] = "V5A"
    nameLookupDict["Shadows of Berlin"] = "SoB"
    nameLookupDict["New Blood"] = "NB"
    nameLookupDict["Fall of London"] = "FoL"
    nameLookupDict["Anthology"] = "Ath"
    nameLookupDict["New Blood II"] = "NB2"
    nameLookupDict["Echoes of Gehenna"] = "EoG"
    nameLookupDict["Keepers of Tradition Reprint"] = "KoTR"
    nameLookupDict["Heirs to the Blood Reprint"] = "HttBR"
    nameLookupDict["First Blood"] = "1e"
    nameLookupDict["Twenty-Fifth Anniversary"] = "25th"
    nameLookupDict["Fifth Edition (Companion)"] = "V5C"
    nameLookupDict["Print on Demand"] = "POD"
    nameLookupDict["Promo"] = "Promo"
    try:
        return nameLookupDict[name]
    except KeyError:
        # print(f"Name unknown: {name}")
        return "XXX"

def find_sets(jobj):
    found_sets=[]
    unique_set_names=[]
    for set_ in [x["sets"] for x in jobj]:
        for set_name in set_.keys():
            if "promo" in set_name.lower() or "2015 Storyline Rewards" == set_name or set_name == "2018 Humble Bundle":
                set_name = 'Promo'

            try:
                release_date = set_[set_name][0]["release_date"]
            except KeyError:
                release_date = None
            if set_name in unique_set_names:
                continue
            unique_set_names.append(set_name)
            short_name = get_short_name(set_name)
            found_sets.append({'release_date': release_date, 'name': short_name, 'name': set_name})

    return found_sets

class Card():
    def __init__(self, jobj):
        self.name = jobj['name']
        self.printed_name = jobj['printed_name']
        self.types = jobj['types']
        self.is_crypt = "Vampire" in self.types or "Imbued" in self.types
        self.clans = jobj.get('clans', None)
        self.url = jobj['url']
        self.group = jobj.get('group', None)
        self.capacity = jobj.get('capacity', None)
        self.disciplines = jobj.get('disciplines', None)
        self.banned = jobj.get('banned', None)
        self.pool_cost = jobj.get('pool_cost', None)
        self.blood_cost = jobj.get('blood_cost', None)
        self.sets = [get_short_name(set_) for set_ in jobj['sets']]
        self.scans = {}
        for scan in jobj['scans']:
            self.scans[get_short_name(scan)] = jobj['scans'][scan]
        self.rulings = jobj.get('rulings', None)

    def __str__(self):
        str_  = ""
        str_ += f"Name: {self.name}, Printed: {self.printed_name}, Types: {self.types}, Clans: {self.clans},"
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

def xml_add_info(info):
    etree.SubElement(info, "author").text = "SchreckNet Authors"
    etree.SubElement(info, "createdAt").text = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    etree.SubElement(info, "sourceUrl").text = KRCG_URL

def xml_add_sets(sets, jobj):
    for set_ in find_sets(jobj):
        xml_set = etree.SubElement(sets, "set")
        for k in set_:
            etree.SubElement(xml_set, k).text = set_[k]

def xml_add_cards(sets, jobj):
    for card in find_cards(jobj):
        card_set = etree.SubElement(sets, "card")

        # First Generic Types
        for key in ['name', 'printed_name', 'url', 'group', 'capacity', 'banned', 'pool_cost', 'blood_cost', 'is_crypt']:
            value = card.get(key)
            if value:
                etree.SubElement(card_set, key).text = str(value)

        # Next Sets
        sets_ = etree.SubElement(card_set, 'sets')
        for set_ in card['sets']:
            scan = card['scans'][set_]
            etree.SubElement(sets_, 'set', name=set_, picURL=scan)

        # Next Types
        for m_type in ['types', 'clans', 'disciplines']:
            types = etree.SubElement(card_set, m_type)
            values = card[m_type]
            if values:
                for type_ in values:
                    etree.SubElement(types, m_type[:-1]).text = type_

        # Magic things, such as related and reverse-related

        # Finaly Rulings
        rulings = etree.SubElement(card_set, 'rulings')
        card_rulings = card['rulings']
        if card_rulings:
            for ruling_text in card_rulings['text']:
                ruling = etree.SubElement(rulings, 'ruling')
                ruling.text = ruling_text
                for tag in card_rulings["links"]:
                    if tag in ruling_text:
                        etree.SubElement(ruling, 'link', tag=tag).text = card_rulings["links"][tag]

if __name__ == '__main__':
    jobj = fetch_jobj()

    attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
    carddatabase = etree.Element("wmrh_carddatabase", {attr_qname: f"urn:{SCHEMA_LOCATION}"},
            nsmap={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}, version="1")

    xml_add_info(etree.SubElement(carddatabase, "info"))
    xml_add_sets(etree.SubElement(carddatabase, "sets"), jobj)
    xml_add_cards(etree.SubElement(carddatabase, "cards"), jobj)

    final_xml = etree.tostring(carddatabase, xml_declaration=True, pretty_print=True)

    # Validate it
    # parser = etree.XMLParser(dtd_validation=True)
    # etree.fromstring(final_xml, parser)
    print("[+] Validating against the schema")
    try:
        resp = requests.get(SCHEMA_LOCATION)
        resp.raise_for_status()
        xmlschema_doc = etree.parse(StringIO(resp.text))

        xmlschema = etree.XMLSchema(xmlschema_doc)
        xmlschema.assertValid(carddatabase)
        print("[+] XML is valid")
    except etree.XMLSchemaParseError as ex:
        print(f"[!!] {ex}")
    except etree.DocumentInvalid as ex:
        print(f"[!!] XML is invalid: {ex}")
    except requests.exceptions.HTTPError as ex:
        print(f"[!!] Failed to Download Schema, won't validate: {ex}")

    with open("schrecknet_wmrh.xml", "wb") as fd:
        fd.write(final_xml)

    # with open("wmrh.json", "w") as fd:
    #     fd.write(json.dumps(wmrh))
