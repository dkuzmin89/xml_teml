#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import warnings
from xml.etree import ElementTree as ET
from pathlib import Path

import pandas as pd
import pycountry

'''
We have original xml files in 'input_xml' folder. 
We have new values in dictionaries in 'new_val_dict' folder
The idea is to update original .xml files with values from dictionaries and 
write new xml with updated values (keeping original structure)
I have working algorithm for that. But I can't put everything in a for loop
'''

warnings.filterwarnings('ignore')

# cg input
cg = pd.read_excel('country_groupings_2020-07.xlsx')
country_iso = cg[['country', 'iso3', 'iso2', 'iso3_num']]
country_iso.country.replace({"Bosnia and Herzegovina": "Bosnia & Herzegovina",
                             "Congo, Republic of": "Republic of the Congo",
                             "Congo, Democratic Republic of the": "Congo, The Democratic Republic of the",
                             #"Côte d'Ivoire": "Côte d’Ivoire",
                             "Lao People's Democratic Republic": "Lao PDR",
                             "Sao Tome and Principe": "São Tomé and Príncipe",
                             "Tanzania, United Republic of": "Tanzania, UR",
                             "Timor-Leste": "Timor Leste",
                             "Viet Nam": "Vietnam"}, inplace=True)

# Master country list & Master iso3 list
with open("country_list.json") as f:
    master_country_list = sorted(json.load(f))  # Countries that should be observed

country_iso = country_iso.loc[country_iso['country'].isin(master_country_list)].reset_index(
    drop=True)
iso3_master_list = country_iso.iso3.tolist()
iso3_num_master_list = country_iso.iso3_num.tolist()
iso3_master_list.sort()  # ISO3 codes of observed countries

#%%
# This is a better way to make the list you wanted to make
# Although I have no idea why you want to make it
xml_files = sorted([f for f in Path("input_xml").glob("*_En.xml")])


def fuzzy(name):
    return pycountry.countries.search_fuzzy(name)


"""
This is the working algorithm
"""
for country_ in master_country_list:
    if country_ == "Congo, DR":
        country_ = "Congo, The Democratic Republic of the"
    print(f"Working on: {country_}")
    # Pick the closest match
    country = pycountry.countries.search_fuzzy(pycountry.remove_accents(country_))[0]
    iso3 = country.alpha_3
    # print(iso3)
    new_data_path = Path(f"new_values/general_info_{iso3}.json")
    xml_path = Path(f"input_xml/Country_context-{iso3}_En.xml")

    if not new_data_path.is_file():
        print(f"No new data file available for: {iso3}")
        continue
    if not xml_path.is_file():
        print(f"No xml file available for: {iso3}")
        continue

    with open(new_data_path, "r") as f:
        new_data = json.load(f)
    tree = ET.parse(xml_path)

    root = tree.getroot()
    for field_name, new_value in new_data.items():
        value_element = root.find(f".//Data/[Name='{field_name}']")
        if value_element is not None:
            elem_value_element = value_element.find("Value")
            elem_value_element.text = str(new_value)
        else:
            value_element = root.find(f".//Data/")
            new_element = ET.Element("Data")
            new_name_elem = ET.Element("Name")
            new_name_elem.text = field_name
            new_value_elem = ET.Element("Value")
            new_value_elem.text = new_value
            new_element.append(new_name_elem)
            new_element.append(new_value_elem)
            value_element.append(new_element)
    # ET.dump(root)
    tree = ET.ElementTree(root)
    tree.write(f"output_xml/Country_context-{iso3}_En.xml")
