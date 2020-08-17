import os
import time

from zipfile import ZipFile
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



__author__ = 'aituarov'



DB_LOADER_DIR = 'C:\\DEV\\output\\'
DATAFILES_DIR = 'C:\\DEV\\output\\'

url = 'https://data.rte-france.com'
EMAIL = 'christian.berclaz@electroroute.com'
PASSWORD = 'Cb10741708.'

chrome_options = Options()
chrome_options.add_experimental_option( "prefs",     
{
  "download.default_directory": DATAFILES_DIR,

  "download.prompt_for_download": False,

  "download.directory_upgrade": True
})
driver = webdriver.Chrome(options = chrome_options)
os.chdir(DATAFILES_DIR)


def download_zip_unav():
    print("Going to " + url)
    driver.get(url)
    time.sleep(2)

    el_login = driver.find_element_by_xpath('//div[@class="header__login"]/a')
    el_login.click()
    time.sleep(2)

    inp_email = driver.find_element_by_xpath('//input[@id="_58_login"]')
    inp_email.send_keys(EMAIL)

    inp_password = driver.find_element_by_xpath('//input[@id="_58_password"]')
    inp_password.send_keys(PASSWORD)

    btn_login = driver.find_element_by_xpath('//div[@class="button-holder "]/button')
    btn_login.click()
    
    sidebar = WebDriverWait(driver,1000).until(EC.presence_of_element_located((By.ID, "sidebar")))
    print("Logined successfully")
    time.sleep(2)
    
    generation_url = 'https://data.rte-france.com/catalog/-/api/generation/Unavailability-Additional-Information/v1.0'
    print("Going to " + generation_url)
    driver.get(generation_url)
    
    file_link = driver.find_element_by_xpath('//ul[@class="links-dev"]//span[text()="Samples.zip"]')
    file_name = file_link.text
    file_link.click()
    while(is_file_downloaded(file_name) == False):
            time.sleep(1)
            
    driver.quit()
            
    get_jsons(file_name)
    
    
def is_file_downloaded(file_name):
    if os.path.isfile(file_name):
        print(file_name + " downloaded")
        return True
    else:
        return False
    

    
def get_jsons(file_name):
    print("Starting to extract json files...")
    with ZipFile(DATAFILES_DIR + file_name, 'r') as out_zip:
        zfiledata = BytesIO(out_zip.read('zip_gu.zip'))
        with ZipFile(zfiledata) as zip_unav:
            zip_unav.extractall(DATAFILES_DIR)
            print("All files extracted from zip_gu.zip to " + DATAFILES_DIR)
            
    
    
    
def main():
    download_zip_unav()

    
if __name__ == '__main__':
    main()
