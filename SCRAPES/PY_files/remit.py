from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime

import time
import os
import shutil
import numpy as np
import pandas as pd
from lxml import html
import re

chrome_options = Options()
driver = webdriver.Chrome(options = chrome_options)


__author__ = 'aituarov'


DATAFILES_DIR = 'C:\\DEV\\REMIT_temp\\'
REMIT_data = 'C:\\DEV\\REMIT_data\\'
REMIT_output = 'C:\\DEV\\REMIT_output\\'

url = 'https://www.elia.be/en/grid-data/power-generation/planned-and-unplanned-outages'


def download_snapshots():
    driver.get(url)
    WebDriverWait(driver,1000).until(EC.visibility_of_all_elements_located((By.XPATH, '//div[@class="k-grid k-widget k-display-block"]')))
    time.sleep(2)
    
    table_divs = driver.find_elements_by_xpath('//div[@class="k-grid k-widget k-display-block"]')
    for table_id, table in enumerate(table_divs):
        snapshot_fname = str(table_id) + '__' + datetime.today().strftime('%Y%m%d') + '.html'
        with open(DATAFILES_DIR + snapshot_fname, 'w') as snapshot_file:
            snapshot_file.write(table.get_attribute('outerHTML'))
            print(snapshot_fname + " downloaded.")
            snapshot_file.close()
            
    driver.quit()


def convert_html_files_to_df(folder):
    data = {}

    if not os.listdir(folder):
        print("There's no files")
    else:
        for file_name in os.listdir(folder):
            if file_name.endswith('html'):
                file_type = int(file_name[0])
                data_table = pd.DataFrame()
                with open(folder + file_name, 'r') as snapshot_file:
                    html_content = snapshot_file.read()
                    page = html.fromstring(html_content)
                    header = [th.text for th in page.xpath('./div//tr/th')[1:]]

                    content_row = page.xpath('./div//tbody/tr')
                    for row in content_row:
                        row_data = [td.text for td in row.xpath('./td')]

                        data_table = data_table.append([row_data], ignore_index=True)

                    data_table.columns = header
                    data[file_type] = data_table
                    print("File starting with " + str(file_type) + " from " + folder + " is converted to df")
                    snapshot_file.close()
                    
    return data


def compare_df(old_data, new_data, comp_id):
    comparison = {}
    
    old_uniq_data = {}
    new_uniq_data = {}
 
    for key in new_data.keys():
        print("Comparing files starting with " + str(key))
        data = pd.DataFrame()
        
        if key not in old_data.keys():
            old_data[key] = pd.DataFrame(columns=new_data[key].columns)
        
        old_uniq_data[key]=pd.merge(old_data[key], new_data[key], indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1).reset_index(drop=True)
        new_uniq_data[key]=pd.merge(old_data[key],new_data[key], indicator=True, how='outer').query('_merge=="right_only"').drop('_merge', axis=1).reset_index(drop=True)
        
        old_cnt = old_uniq_data[key].groupby(['Unit']).size().reset_index(name='counts')
        new_cnt = new_uniq_data[key].groupby(['Unit']).size().reset_index(name='counts')

        merged_df=old_cnt.merge(new_cnt, how='outer', on='Unit')
        
        
        for index, row in merged_df.iterrows():
            df_old_match = old_uniq_data[key].loc[old_uniq_data[key]['Unit'] == row['Unit']]
            df_new_match = new_uniq_data[key].loc[new_uniq_data[key]['Unit'] == row['Unit']]

            if row['counts_x'] == row['counts_y'] == 1:
                df_stat = pd.DataFrame([['UPDATED', comp_id]], columns=['status', 'comp_id'])
                data = data.append(pd.concat([pd.concat([df_stat, df_old_match], axis=1), pd.concat([df_stat, df_new_match], axis=1)], axis=0))

            elif row['counts_x'] >= 1 and pd.isna(row['counts_y']):
                df_stat = pd.DataFrame([['REMOVED', comp_id]], columns=['status', 'comp_id'])
                data = data.append(pd.concat([df_stat, df_old_match], axis=1))
            
            elif pd.isna(row['counts_x']) and row['counts_y']>=1:
                df_stat = pd.DataFrame([['ADDED', comp_id]], columns=['status', 'comp_id'])
                data = data.append(pd.concat([df_stat, df_new_match], axis=1))
            
            else:
                df_stat = pd.DataFrame([['NaN', 'NaN']], columns=['status', 'comp_id'])
                data = data.append(pd.concat([df_stat, df_new_match], axis=1))
        
        if not data.empty:
            data[['status', 'comp_id']] = data[['status', 'comp_id']].fillna(method='ffill')
            data = data.drop(data['Unit']==float('NaN'))
            data = data.replace('NaN', float('NaN'))
            
        comparison[key] = data
        
    return comparison

            

def main():
    download_snapshots()
    time.sleep(2)
    if not os.listdir(REMIT_output):
        comp_id = 1
    else:
        exist_comp_ids = [int(re.match("^\d+", file)[0]) for file in os.listdir(REMIT_output)]
        comp_id = max(exist_comp_ids) + 1


    old_data = convert_html_files_to_df(REMIT_data)
    new_data = convert_html_files_to_df(DATAFILES_DIR)

    comparison = compare_df(old_data, new_data, comp_id)
    remit_output = pd.DataFrame()
    for key in comparison.keys():
        remit_output = remit_output.append(comparison[key])
        
        if not comparison[key].empty:
            print("Files starting with " + str(key) + " have differences")
            for file_name in os.listdir(REMIT_data):
                if file_name.startswith(str(key)):
                    os.remove(REMIT_data + file_name)
            
            for new_file_name in os.listdir(DATAFILES_DIR):
                if new_file_name.startswith(str(key)):
                    shutil.copyfile(DATAFILES_DIR + new_file_name, REMIT_data + new_file_name)
                    shutil.copyfile(DATAFILES_DIR + new_file_name, REMIT_data+"ARCHIVE\\" + new_file_name)
                    
            print("File starting with " + str(key) + " moved to " + REMIT_data + ", and copied to ARCHIVE")
        
        else:
            print("Files starting with " + str(key) + " identical")
        
        for file_name in os.listdir(DATAFILES_DIR):
            if file_name.startswith(str(key)):
                os.remove(DATAFILES_DIR + file_name)
                print("File starting with " + str(key) + " removed from " + DATAFILES_DIR)

    remit_output.to_excel(REMIT_output + str(comp_id) + "__remit_output__" + datetime.today().strftime('%Y%m%d') + ".xlsx", index=False)
    print("remit_output file created in " + REMIT_output)


if __name__ == '__main__':

    main()    
