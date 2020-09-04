import pandas as pd
import os
import warnings
import xml.etree.ElementTree as ET

'''
We have original xml files in 'input_xml' folder. 
We have new values in dictionaries in 'new_val_dict' folder
The idea is to update original .xml files with values from dictionaries and write new xml with updated values (keeping original structure)
I have working algorithm for that. But I can't put everithing in a for loop
'''

warnings.filterwarnings('ignore')

## cg input
cg = pd.read_excel('country_groupings_2020-07.xlsx')
country_iso = cg[['country','iso3','iso2','iso3_num']]
country_iso.country.replace({"Bosnia and Herzegovina": "Bosnia & Herzegovina",
                             "Congo, Republic of": "Congo",
                             "Congo, Democratic Republic of the": "Congo, DR",
                             "Côte d'Ivoire":"Côte d’Ivoire",
                             "Lao People's Democratic Republic": "Lao PDR",
                             "Sao Tome and Principe":"São Tomé and Príncipe",
                             "Tanzania, United Republic of":"Tanzania, UR",
                             "Timor-Leste":"Timor Leste",
                             "Viet Nam":"Vietnam"},inplace=True)

## Master country list & Master iso3 list
my_file = open('county_list.txt', 'r')
content= my_file.read()
my_file.close()
content = content.replace('\n', ';')
master_country_list = content.split(';')
master_country_list.sort() ### Countries that should be observed

country_iso = country_iso.loc[country_iso['country'].isin(master_country_list)].reset_index(drop=True)
iso3_master_list = country_iso.iso3.tolist()
iso3_num_master_list = country_iso.iso3_num.tolist()
iso3_master_list.sort()  ### ISO3 codes of odserved countries


xml_dir = 'input_xml/'
xml_file_list = []
for filename in os.listdir(xml_dir):
    if filename.endswith("_En.xml"):
        f = os.path.join(xml_dir, filename)
        xml_file_list.append(f)
xml_file_list.sort()



'''
This is working algorithm
'''
new_data = {'Total population (2019)': 10000,'World Bank Index, IDA (2015)': 7.45}
# root = ET.fromstring(xml)
tree = ET.parse('input_xml/Country_context-AFG_En.xml')
root = tree.getroot()
for field_name,new_value in new_data.items():
    value_element = root.find(".//Data/[Name='{}']".format(field_name))
    value_element.find('Value').text = str(new_value)
ET.dump(root)
tree = ET.ElementTree(root)
tree.write('testing_output.xml')