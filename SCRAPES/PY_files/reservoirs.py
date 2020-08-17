import io
import os
import re
import pandas as pd
from datetime import datetime
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

import requests
from lxml import etree, html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import time

DB_LOADER_DIR = "C:\\DEV\\output\\"# Folder, where pdf files need to load
DB_OUTPUT_DIR = "C:\\DEV\\output\\"# Folder, in which csv files save


header = ["value_date",
         
          "Valais_reservoir_level", "Valais_reservoir_fillrate",
         
          "Grisons_reservoir_level", "Grisons_reservoir_fillrate",

          "Tessin_reservoir_level", "Tessin_reservoir_fillrate",

          "Other_reservoir_level", "Other_reservoir_fillrate",
         
          "Total_reservoir_level", "Total_reservoir_fillrate",

          "average_flow", "effective_flow", "effective_flow_pct"]


post_fix = '- reservoir level bfeCH pwr data act'


def download_pdf(download_folder):  
    chrome_options = Options()
    prefs = {"download.default_directory" : download_folder}# Setting directory to download files
    chrome_options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(options = chrome_options)

    url = "https://www.bfe.admin.ch/bfe/de/home/versorgung/statistik-und-geodaten/energiestatistiken/elektrizitaetsstatistik.html"
    driver.get(url)
   
    pdf_files = driver.find_elements_by_xpath('//a[contains(.,"' + u'F\xfcllungsgrad der Speicherseen' + '")]')
   
    today = datetime.today()
    if today.date() > datetime.strptime(today.strftime('%Y-04-01'), '%Y-%m-%d').date():
        cnt_download = 1
    else:
        cnt_download = 2
    for pdf_index in range(cnt_download):
        pdf = pdf_files[pdf_index]
        print("Downloading " + pdf.text + " to " + download_folder )
        pdf.click()
       

       
       
       

def convert_pdf_to_csv(pdf_path, csv_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
   
    for fname in os.listdir(pdf_path):# Go throw all files in my folder
        if fname.endswith('.PDF'):
            with open(pdf_path + fname, 'rb') as fh:# Open files ends with .PDF
                print("Converting " + pdf_path + fname + " to csv file....")
                for page in PDFPage.get_pages(fh,
                                              caching=True,
                                              check_extractable=True):
                    page_interpreter.process_page(page)

                text = fake_file_handle.getvalue()

            lines = text.split('      ')

            data_table = pd.DataFrame()
            for line in lines:
                match = re.search(r'(\d{2}\.\d{2}\.\d{4})(\d\'\d{3}|\d{3})(\d{1,2}\.\d).(\d\'\d{3}|\d{3})(\d{1,2}\.\d).(\d\'\d{3}|\d{3})(\d{1,2}\.\d).(\d\'\d{3}|\d{3}|\d{4})(\d{1,2}\.\d).(\d\'\d{3}|\d{3})(\d{1,2}\.\d).(\d\'\d{3}|\d{3})(\d\'\d{3}|\d{3})(\d{2,3}).', line)
                if match is not None:
                    line = match.group(1) + " " + match.group(2) + " " + match.group(3) + " " + match.group(4) + " " + match.group(5) + " " + match.group(6) + " " + match.group(7) + " " + match.group(8) + " " + match.group(9) + " " + match.group(10) + " " + match.group(11) + " " + match.group(12) + " " + match.group(13) + " " + match.group(14)
                    line = line.replace("'","")
                    line = line.split()
                   
                    data_table = data_table.append([line], ignore_index=True)
            data_table = data_table.rename(columns=lambda s: header[s])
            data_table = pd.melt(data_table, id_vars=['value_date'], value_vars = header[1:], var_name='name', value_name='value')
           
            data_table = {
                    'name': data_table['name'].map(lambda x: x + '_' + post_fix),
                    'effective_date': '',
                    'start_date': data_table['value_date'].map(lambda x: datetime.strptime(x, '%d.%m.%Y')),
                    'end_date': '',
                    'value' :  data_table['value'],
                    'table': 'spot'
                        }
            data_table = pd.DataFrame(data_table)
            fname = fname.replace('.PDF', '.csv')
            data_table.to_csv(csv_path + fname, sep=';',index=False)
#             close open handles
    converter.close()
    fake_file_handle.close()
    print("END.")
           



if __name__ == '__main__':

    download_pdf(DB_LOADER_DIR)
    print("All files downloaded")
   
    time.sleep(3)
   
    print("Starting to convert pdf files: ")
    convert_pdf_to_csv(DB_LOADER_DIR, DB_OUTPUT_DIR)


