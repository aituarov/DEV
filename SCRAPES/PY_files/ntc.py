from datetime import datetime, timedelta
from lxml import html
import requests
import time
import pandas as pd
import os
import urllib3


__author__ = 'aituarov'


DB_LOADER_DIR = 'C:\\DEV\\output\\'
DATAFILES_DIR = 'C:\\DEV\\output\\'

post_fix = '_ntc_trans'

end_date = datetime.today().date() + timedelta(days=-1)
start_date = end_date + timedelta(days=-1)

# end_date = datetime.strptime("2020-07-11", '%Y-%m-%d').date()
# start_date = datetime.strptime("2020-07-10", '%Y-%m-%d').date()


def download_file():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = 'https://damas.terna.it/api/Ntc/DownloadNtcReport?businessDayFrom='+(start_date + timedelta(days=-1)).strftime('%Y-%m-%d')+'T22:00:00.000Z&businessDayTill='+(end_date + timedelta(days=-1)).strftime('%Y-%m-%d')+'T22:00:00.000Z'
    response = requests.get(url, stream=True, verify=False)
    
    file_name = 'NtcReport_' + datetime.today().strftime('%Y%m%d_%H%M') + '.xlsx'
    with open(DATAFILES_DIR + file_name, 'wb') as output:
            output.write(response.content)
            print('File ' + file_name + ' downloaded')
            output.close()
    
    
def gen_output_csv():
    file_names = [f for f in os.listdir(DATAFILES_DIR) if f.startswith('NtcReport_')]
    for f_id, file_name in enumerate(file_names):
        print("Reading " + file_name)
        data = pd.read_excel(DATAFILES_DIR + file_name)
        data['date'] = data['Business Day'] + '_' +(data['Hour'] - 1).astype(str)
        data = data.drop(columns=['Business Day', 'Hour'])
        
        write_stdldr(data,f_id)
              
        
def write_stdldr(data,f_id):
    print("Writing to new csv file...")
    
    data['name'] = data['Border Direction'] + post_fix
    data['effective_date'] = ""
    data['start_date'] = data['date'].map(lambda x: datetime.strptime(x, '%d.%m.%Y_%H').strftime('%Y-%m-%d %H:%M'))
    data['end_date'] = ""
    data['value'] = data['NTC [MW]'] 
    data['table'] = 'spot'

    data = data[["name","effective_date","start_date","end_date","value","table"]]
    outfile = DB_LOADER_DIR + "ntc_("+str(f_id)+")_"+ datetime.today().strftime('%Y_%m_%d_%H%M%S') +".csv"
    data.to_csv(outfile, sep=';',index=False)
    print(outfile + " is ready")
            
    
def main():
    download_file()
    time.sleep(3)
    gen_output_csv()



if __name__ == '__main__':

    main()
