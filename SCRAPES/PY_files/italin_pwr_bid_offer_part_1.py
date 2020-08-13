import os
import time
import requests
from datetime import datetime,timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


ZIP_DOWNLOAD_DIR = "C:\\DEV\\output\\"


start_date = '2019-05-26'
DAY_CNT = 7


url = "https://www.mercatoelettrico.org/En/download/DownloadDati.aspx?val=OfferteFree_Pubbliche"
chrome_options = Options()
chrome_options.add_experimental_option( "prefs",     
{
  "download.default_directory": ZIP_DOWNLOAD_DIR,

  "download.prompt_for_download": False,

  "download.directory_upgrade": True,

  "safebrowsing.enabled": True
})
driver = webdriver.Chrome(options = chrome_options)

os.chdir(ZIP_DOWNLOAD_DIR)



def retrieve_files(s_date, file_path):
    driver.get(url)
    try:
        download_zip_files(s_date, file_path)

    except NoSuchElementException:
        print('Going through disclaimer...')
        time.sleep(1)  
        go_disclaimer()
        download_zip_files(s_date, file_path)


                
def go_disclaimer():
    try:
        accept_checkbox_1 = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_CBAccetto1"]')
        accept_checkbox_1.click()
        accept_checkbox_2 = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_CBAccetto2"]')
        accept_checkbox_2.click()
        accept_btn = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_Button1"]')
        accept_btn.click()

    except Exception as e:
        print('ERROR-going through disclaimer : ' + str(e))
        raise Exception('EXIT')
        
        
        
def download_zip_files(start_date, file_path):
    
    el_date = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_tbDataStart"]')
    for single_date in (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(n) for n in range(DAY_CNT)):
        single_date_str = single_date.strftime('%d/%m/%Y')
        el_date.clear()
        el_date.send_keys(single_date_str)
        el_download_btn = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_btnScarica"]')
        el_download_btn.click()
        file_name = single_date.strftime('%Y%m%d') + "OfferteFree_Pubbliche.zip"
        print('Downloading ' + file_name)
        while(is_file_downloaded(file_path, file_name) == False):
            time.sleep(3)
    print("All files downloaded.")
    driver.quit()
    
    
    
def is_file_downloaded(file_path, file_name):
    if os.path.isfile(file_name):
        return True
    else:
        return False
        
        
    
if __name__ == '__main__':
    retrieve_files(start_date, ZIP_DOWNLOAD_DIR)
