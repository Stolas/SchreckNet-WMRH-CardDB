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
# SCHEMA_LOCATION = "./cards.xsd"

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
    nameLookupDict["Tokens"] = "TK"
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
            found_sets.append({'release_date': release_date, 'name': short_name, 'longname': set_name})

    return found_sets

class Card():
    def __init__(self, jobj):
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
        self.sets = [get_short_name(set_) for set_ in jobj.get('sets', [])]
        self.scans = {}
        for scan in jobj.get('scans', []):
            self.scans[get_short_name(scan)] = jobj['scans'][scan]
        self.rulings = jobj.get('rulings', None)
        self.token = jobj.get('token', None)

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

def xml_add_info(info, author="SchreckNet Authors", sourceUrl=KRCG_URL):
    etree.SubElement(info, "author").text = author
    etree.SubElement(info, "createdAt").text = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    etree.SubElement(info, "sourceUrl").text = sourceUrl

def xml_add_sets(sets, jobj):
    for set_ in find_sets(jobj):
        xml_set = etree.SubElement(sets, "set")
        for k in set_:
            etree.SubElement(xml_set, k).text = set_[k]

def xml_add_cards(sets, jobj):
    for card in find_cards(jobj):
        card_set = etree.SubElement(sets, "card")

        # First Generic Types
        for key in ['name', 'printed_name', 'url', 'group', 'capacity', 'banned', 'pool_cost', 'blood_cost']:
            value = card.get(key)
            if value:
                etree.SubElement(card_set, key).text = str(value)

        etree.SubElement(card_set, 'text').text = card['card_text']
        if card['is_crypt']:
            etree.SubElement(card_set, 'is_crypt').text = 'true'
        else:
            etree.SubElement(card_set, 'is_crypt').text = 'false'

        # Next Sets
        if card.get('sets'):
            sets_ = etree.SubElement(card_set, 'sets')
            for set_ in card['sets']:
                scan = card['scans'][set_]
                etree.SubElement(sets_, 'set', name=set_, picURL=scan)

        # Next Types
        for m_type in ['types', 'clans', 'disciplines']:
            values = card[m_type]
            if values:
                types = etree.SubElement(card_set, m_type)
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

        if card['token']:
            etree.SubElement(card_set, 'token').text = '1'

        # Todo; add related and reverse-related
        # if card['related']:

def generate_xml_header():
    attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
    return etree.Element("wmrh_carddatabase", {attr_qname: f"urn:{SCHEMA_LOCATION}"},
            nsmap={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}, version="1")

def generate_carddb():
    jobj = fetch_jobj()

    carddatabase = generate_xml_header()
    xml_add_info(etree.SubElement(carddatabase, "info"))
    xml_add_sets(etree.SubElement(carddatabase, "sets"), jobj)
    xml_add_cards(etree.SubElement(carddatabase, "cards"), jobj)

    return carddatabase

def generate_tokendb():
    all_tokens = [
            {'name': 'Edge',
             'card_text': 'Gain control of the Edge after a successful bleed. Burn the Edge during a referendum to gain 1 vote. If you control the Edge during your unlock phase, you may gain 1 pool from the Blood Bank.',
             'types': ['Token'],
             'url': 'https://static.krcg.org/card/edge2.png',
             'token': 'true',
             'reverse-related': [
                '419 Operation', 'Alicia Barrows', 'Alonzo Guillen', 'Amenophobis',
                'Bulscu', 'Code of Milan Suspended', 'Curse of Nitocris', 'Cyscek',
                'Deploy the Hand', 'Dreams of the Sphinx', 'Eat the Rich',
                'Edge Vitiation', 'Emily Carson', 'Enticement', 'Eric Kressida',
                'Esteem', 'Extortion', 'Fiorenza Savona', 'Form of Corruption',
                'Free States Rant', 'Gracetius', 'Hand Intervention', 'Hartmut Stover',
                'Heather Florent, The Opportunist', 'High Priest Angra Mainyu',
                'Hrothulf', 'Inside Dirt', 'Instability', 'Intisar', 'Isouda de Blaise',
                'Jazz Wentworth', 'Kalinda', 'Keith Moody', "King's Rising",
                'Lady Constancia', 'Leverage', 'Lucina', 'Lucinde, Alastor',
                'Mapatano Utando', 'Marcel de Breau', 'Medic, The', 'Melissa Barton',
                'Nagaraja', 'Nkule Galadima', 'Off Kilter', 'Ondine "Boudicca" Sinclair',
                'Patsy', 'Powerbase: Zürich', 'Regaining the Upper Hand', 'Rising, The',
                'Sabbat Threat', 'Sargon', 'Sarrasine', 'Sennadurek', 'Shard, London, The',
                'Shatter the Gate', 'Soldat', 'Tereza Rostas', 'Torvus Bloodbeard',
                'Tragic Love Affair', 'Tyler McGill', 'Urraca', 'Using the Advantage',
                'Victoria', 'Victorine Lafourcade', 'Vincent Day, Paladin and Paragon',
                ]},
            {'name': 'Anarch Counter',
             'card_text': 'This vampire is considered Anarch. If this vampire change sects burn this counter.',
             'types': ['Token'],
             'url': 'https://static.krcg.org/card/anarchcounter.png',
             'token': 'true',
            },
            {'name': 'Black Hand Counter',
             'card_text': 'This vampire is considered Black hand.',
             'types': ['Token'],
             'url': 'https://static.krcg.org/card/corruptioncounter.png',
             'token': 'true',
            },
            {'name': 'Liaison Marker',
             'card_text': ' This vampire is considered Liaison, unique Independent title that worth 4 votes. If this title would be contested with a younger vampire, the younger vampire immediately yields instead of contesting.',
             'types': ['Token'],
             'url': 'https://static.krcg.org/card/liaisonmarker.png',
             'token': 'true',
             'reverse-related': ['Rise of the Nephtali']
            },
    ]

    tokens = generate_xml_header()
    xml_add_info(etree.SubElement(tokens, "info"))
    xml_add_cards(etree.SubElement(tokens, "cards"), all_tokens)
    return tokens

def validate_xml(xml):
    print("[+] Validating against the schema")
    try:
        if SCHEMA_LOCATION.startswith("http"):
            resp = requests.get(SCHEMA_LOCATION)
            resp.raise_for_status()
            xmlschema_doc = etree.parse(StringIO(resp.text))
        else:
            with open(SCHEMA_LOCATION, 'r') as fd:
                xmlschema_doc = etree.parse(fd)

        xmlschema = etree.XMLSchema(xmlschema_doc)
        xmlschema.assertValid(xml)
        print("[+] XML is valid")
    except etree.XMLSchemaParseError as ex:
        print(f"[!!] {ex}")
    except etree.DocumentInvalid as ex:
        print(f"[!!] XML is invalid: {ex}")
    except requests.exceptions.HTTPError as ex:
        print(f"[!!] Failed to Download Schema, won't validate: {ex}")

def write_xml_file(xml, filename, pretty_print):
    with open(filename, "wb") as fd:
        fd.write(etree.tostring(xml, xml_declaration=True, pretty_print=pretty_print, encoding='utf-8'))

def generate_xml_files(generate_fcn, filename, do_validate=True, pretty_print=True):
    xml = generate_fcn()
    if do_validate:
        validate_xml(xml)
    write_xml_file(xml, filename, pretty_print)

if __name__ == '__main__':
    generate_xml_files(generate_carddb, "schrecknet_wmrh.xml")
    generate_xml_files(generate_tokendb, "tokens.xml")
