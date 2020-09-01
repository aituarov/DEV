from datetime import datetime
from google.cloud import translate_v2
from lxml import html
import os
import requests
import json
import pandas as pd
import numpy as np
import re
import time
import warnings

warnings.filterwarnings("ignore")


__author__ = 'aituarov'


DB_LOADER_DIR = 'C:\\DEV\\output\\'
DATAFILES_DIR = 'C:\\DEV\\output\\'
JSON_FILE_DIR = 'C:\\DEV\\'


use_translation_api = False

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\DEV\GoogleTranslationAPI\GoogleCloudKey_AdilbekServiceAccount.json"
translate_client = translate_v2.Client()
target_language = 'en'


header = {
    'Business name_': 'company',
    'Hydroelectric power plant_general': 'Hydro',
    'Hydroelectric power plant_Pumped': 'Pumped Hydro',
    'Thermal power plant_coal': 'coal',
    'Thermal power plant_ＬＮＧ': 'LNG',
    'Thermal power plant_oil': 'oil',
    'Thermal power plant_LPG': 'LPG',
    'Thermal power plant_Other gas': 'Gas other',
    'Thermal power plant_Cyanogen mixture': 'Bituminous mixture',
    'Thermal power plant_Other': 'Thermal other',
    'Nuclear power plant_': 'Nuclear',
    'New energy power plant_Wind force': 'Wind',
    'New energy power plant_sunshine': 'Solar',
    'New energy power plant_Geothermal': 'Geothermal',
    'New energy power plant_biomass':'Biomass',
    'New energy power plant_waste':'Waste',
    'Other_':'Other'   
}


def download_file():
    url = 'https://www.enecho.meti.go.jp/statistics/electric_power/ep002/'
    response = requests.get(url + 'results.html')
    print("Trying to find file from " + url + 'resulst.html')
    page = html.fromstring(response.text)
    
    files = page.xpath('//div[@class="tileListCol1st h15em"]/ul/li/a')
    for file in files:
        if file.text.startswith('2-(1)'):
            url = url + file.get('href')
    response = requests.get(url)
    print("Starting download file " + url)
    file_name = DATAFILES_DIR + 'owner_raw.xlsx'
    with open(file_name, 'wb') as output:
        output.write(response.content)
        output.close()
    print("File downloaded")
    
    
def parse_needed_data_from_xl(file_name):
    print("Parsing data from " + file_name)
    xl = pd.ExcelFile(file_name)
    needed_sheets_names = []
    for sh_name in xl.sheet_names:
        if re.search(r'\d{4}.\d+', sh_name):
            needed_sheets_names.append(sh_name)

    raw_data = xl.parse(needed_sheets_names)
    print("Parsing finished successfully")
    return raw_data
    
    
def update_json(raw_data):
    print("Starting to update json file")
    if os.path.exists(JSON_FILE_DIR + 'google_translate_v2.json'):
        print("Find google_translate_v2.json in " + JSON_FILE_DIR)
        with open(JSON_FILE_DIR + 'google_translate_v2.json') as j:
            myDict = json.load(j)
    else:
        print("Can't find google_translate_v2.json file in " + JSON_FILE_DIR + '\nCreating new json file...')
        myDict = {}
    
    for key in raw_data.keys():
        for row in range(raw_data[key].shape[0]):
            for col in range(raw_data[key].shape[1]):
                if(isinstance(raw_data[key].iloc[row, col], str) and raw_data[key].iloc[row, col] not in myDict):
                    new_string = raw_data[key].iloc[row, col]
                    myDict[new_string] = translate_client.translate(
                        new_string,
                        target_language=target_language
                        )["translatedText"]           
    
    with open(JSON_FILE_DIR + 'google_translate_v2.json', "w") as outfile:
        json.dump(myDict, outfile)
    print("JSON file successfully updated.")
        
    
def translate_text(str):
    if os.path.exists(JSON_FILE_DIR + 'google_translate_v2.json'):
        with open(JSON_FILE_DIR + 'google_translate_v2.json') as j:
            dic = json.load(j)

        for d in dic:
            str = str.replace(d,dic[d])
    else:
        str = 'Json file not find, please check the json path'
    
    return str
    
    
def translate_file(raw_data):
    print("Translating sheets of downloaded file...")
    data_table = pd.DataFrame()

    data = {}

    for key in raw_data.keys():
        data[key] = translate_text(raw_data[key])
        headers = data[key].iloc[0]
        for ind in range(len(headers)):
            if isinstance(headers[ind], float):
                headers[ind] = headers[ind-1]
    
        sub_headers = data[key].iloc[1].replace(np.nan, '')
        headers = headers + '_' + sub_headers
        data[key].columns = headers
        data[key] = data[key].rename(columns=lambda x: header[x] if x in header.keys() else np.nan)
        data[key] = data[key].loc[data[key]['company'].notnull(), data[key].columns.notnull()].reset_index(drop=True).head(-1).tail(-1)
        
        data[key] = pd.melt(data[key], id_vars=['company'], value_vars = list(data[key].columns)[1:], var_name='name', value_name='value')
        data[key] = change_format_df(data[key], key)
        data_table = data_table.append(data[key])
        print(key + " sheet translated")
        
        
    data_table.to_csv(DB_LOADER_DIR + "owner_data.csv", sep=';',index=False)
    print("End.")


def change_format_df(data, key):
    data['name'] = data['company'].replace('/', '').replace('㈱Global New Energy Togo', 'Global New Energy Togo') + '_' + data['name']
    data['effective_date'] = ""
    data['start_date'] = datetime.strptime(key, '%Y.%m').strftime('%Y-%m-%d')
    data['end_date'] = ""
    data['value'] = data['value'].map(lambda x:round(x) if not (pd.isna(x) or isinstance(x, str)) else float('nan'))
    data['table'] = 'spot'
    data = data[["name","effective_date","start_date","end_date","value","table"]]
    
    return data

   
def main():
    download_file()
    time.sleep(3)
    
    raw_data = parse_needed_data_from_xl(DATAFILES_DIR + 'owner_raw.xlsx')
    time.sleep(3)
    
    if use_translation_api:
        update_json(raw_data)
        time.sleep(3)
        
    translate_file(raw_data)


if __name__ == '__main__':
    main()