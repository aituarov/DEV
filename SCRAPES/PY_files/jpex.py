from datetime import datetime, timedelta, date, time
from lxml import html
import requests
import time as t
import os
import csv
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)


__author__ = 'aituarov'


DB_LOADER_DIR = 'C:\\DEV\\output\\'
DATAFILES_DIR = 'C:\\DEV\\output\\'


post_fix = "jepx_spot_market_trading_result"



def download_files():
    url = 'http://www.jepx.org/english/market/'
    response = requests.get(url)
    page = html.fromstring(response.text)
    table_body = page.xpath('//table[@class="tableStyle-a styleB"]/tr[position()>1]')
    
    
    today = datetime.today()
    if today.date() > datetime.strptime(today.strftime('%Y-04-01'), '%Y-%m-%d').date():
        cnt_download = 1
    else:
        cnt_download = 2
        
    for file_index in range(cnt_download):
        tr = table_body[file_index]
        file_url = url + tr.xpath('./td/a')[0].get('href')
        file_name = file_url.split('/')[-1]

        resp = requests.get(file_url)
        text = translate_text(resp.text)
        print(file_name)

        with open(DATAFILES_DIR + file_name, 'w') as output:
            output.write(text)
            output.close()

            print(' downloaded')
    print('All files downloaded')
            
            
def gen_output_csv():
    fnames = [f for f in os.listdir(DATAFILES_DIR) if f.startswith('spot_')]
    for f_id, fname in enumerate(fnames):
        data = pd.DataFrame(None)
        print("Reading " + fname + "...")
        with open(DB_LOADER_DIR + fname, newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            header = next(csv_reader)    
            for line in csv_reader:
                data = data.append([line])
        data.rename(columns=lambda x: header[x], inplace=True)
        data = data.replace('', np.nan).dropna(how='all', axis=1)
        data['date'] = data['date'] + '_' + data['time code'].map(lambda x:(datetime.combine(date.today(), time(0,0))+(int(x)-1)*timedelta(minutes=30)).time().strftime('%H:%M'))
        data = data.drop(columns='time code')
        data = pd.melt(data, id_vars=['date'], value_vars = list(data.columns)[1:], var_name='name', value_name='value')

        write_stdldr(data,f_id)

    print('End.')
        
        
        
        
        
        
def write_stdldr(data,f_id):
    print("Writing to new csv file...")

    data['name'] = data['name'].map(lambda x: x.replace(' ','_').replace('(','').replace(')','').replace('/','_per_') + '_' + post_fix)

    data['effective_date'] = ""

    data['start_date'] = data['date'].map(lambda x: datetime.strptime(x, '%Y/%m/%d_%H:%M').strftime('%Y-%m-%d_%H:%M'))

    data['end_date'] = ""

    data['table'] = 'spot'

    data = data[["name","effective_date","start_date","end_date","value","table"]]

    outfile = DATAFILES_DIR + "jepx_("+str(f_id)+")_"+ datetime.today().strftime('%Y_%m_%d_%H%M%S') +".csv"

    data.to_csv(outfile, sep=';',index=False)
    
    print(outfile + " is ready")

            
            
  

        
        
        
def translate_text(str):

    dic = {'年月日': 'date', 
           '時刻コード': 'time code', 
           '売り入札量(kWh)': 'sell bid amount (kWh)', 
           '買い入札量(kWh)': 'buy bid amount (kWh)', 
           '約定総量(kWh)': 'contracted total amount (kWh)', 
           'システムプライス(円/kWh)': 'system price (yen/kWh)', 
           'エリアプライス北海道(円/kWh)': 'area price Hokkaido (yen/kWh)', 
           'エリアプライス東北(円/kWh)': 'area price Tohoku (yen/ kWh)', 
           'エリアプライス東京(円/kWh)': 'area price Tokyo (yen/kWh)', 
           'エリアプライス中部(円/kWh)': 'area price Chubu (yen/kWh)', 
           'エリアプライス北陸(円/kWh)': 'area price Hokuriku (yen/kWh)', 
           'エリアプライス関西(円/kWh)': 'area price Kansai (yen/kWh)', 
           'エリアプライス中国(円/kWh)': 'area price China (yen/kWh)', 
           'エリアプライス四国(円/kWh)': 'area price Shikoku (yen/kWh)', 
           'エリアプライス九州(円/kWh)': 'area price Kyushu (yen/kWh)', 
           'α上限値×スポット・時間前平均価格(円/kWh)': 'upper limit x spot-average price before hour (yen/kWh)', 
           'α下限値×スポット・時間前平均価格(円/kWh)': 'lower limit x spot-average price before hour (yen/kWh)', 
           'α速報値×スポット・時間前平均価格(円/kWh)': 'preliminary value x spot-hourly average price (yen/kWh)', 
           'α確報値×スポット・時間前平均価格(円/kWh)': 'confirmed value x spot-hourly average price (yen/kWh)', 
           '回避可能原価全国値(円/kWh)': 'national avoidable cost (JPY/kWh)', 
           '回避可能原価北海道(円/kWh)': 'avoidable cost Hokkaido (JPY/kWh)', 
           '回避可能原価東北(円/kWh)': 'avoidable cost Tohoku (JPY/kWh)', 
           '回避可能原価東京(円/kWh)': 'avoidable cost Tokyo (JPY/kWh)', 
           '回避可能原価中部(円/kWh)': 'avoidable cost Chubu (JPY/kWh)', 
           '回避可能原価北陸(円/kWh)': 'avoidable cost Hokuriku (JPY/kWh)', 
           '回避可能原価関西(円/kWh)': 'avoidable costs Kansai (JPY/kWh)', 
           '回避可能原価中国(円/kWh)': 'avoidable costs China (JPY/kWh)', 
           '回避可能原価四国(円/kWh)': 'avoidable costs Shikoku (JPY/kWh)', 
           '回避可能原価九州(円/kWh)': 'avoidable costs Kyushu (JPY/kWh)',
           'スポット・時間前平均価格(円/kWh)': 'Spot-average price before hour (yen/kWh)',
           '\r': ''
          }
    
    for d in dic:
        str = str.replace(d,dic[d])

    return str





def main():
    print('Starting to download files')
    download_files()
    t.sleep(3)
    print('Starting to generate output csv')
    gen_output_csv()



    
    
if __name__ == '__main__':
    main()
