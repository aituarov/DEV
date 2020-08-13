import requests, urllib.request
from lxml import etree, html
import csv
import pandas as pd
from datetime import datetime,timedelta,time
import re
import pytz



__author__ = 'aituarov'



DB_LOADER_DIR = "C:\\DEV\\output\\"

#******************************     Giving input data as csv file and start,end dates    *************************************#


csv_path = DB_LOADER_DIR + "locations_list.csv"
open_file = open(csv_path, "r")
csv_reader = csv.reader(open_file, delimiter =";")
header_csv = next(csv_reader)


end_date = datetime.today().date() + timedelta(days=-1)
start_date = end_date + timedelta(days=-1)


needed_values = {'temperature': 'C', 'humidite': 'percent', 'vent': 'km/h', 'precip': 'mm'}
post_fix = ' – meteocielEU weather data act'

CHUNK_SIZE=1



#******************************     Reading csv file line by line    *************************************#
def get_data():
    request_date = start_date
    dte_start = start_date
    
    is_hour_utc = False
    
    data_table = pd.DataFrame()
    f_id = 1
    cnt_days=0
    
    while request_date <= end_date:
        print(request_date)

        for line in csv_reader:
            print(line)

            station_name_csv = line[1]
            station_code_csv = line[2]

    # Creating url every time, when requestDate is change
            url = "http://www.meteociel.fr/temps-reel/obs_villes.php?code2="+str(station_code_csv)+"&jour2="+str(request_date.day)+"&mois2="+str(request_date.month - 1)+"&annee2="+str(request_date.year)
            print("Retrieving data from: " + url)
            response = requests.get(url) 
            page = html.fromstring(response.text)

            element_table = page.xpath('//td/b[contains(.,"Heure")]/../../..')[0]

            header = [(format_name(td.text_content())).replace('.','').split()[0] for td in element_table.xpath('./tr[1]/td')]

            if 'vent' in header:
                header.insert(header.index('vent'), 'vent_direction')

            if header[0] == "heureutc":
                is_hour_utc = True
            else:
                is_hour_utc = False

            header[0] = 'hour'


            data = [[td.text_content().strip().replace(' ','').replace("&nbsp", '').replace('\n','').split('(')[0] for td in tr] for tr in element_table.xpath('./tr[position()>1]')]
            data = pd.DataFrame(data, columns=header)

            for column in header:
                if not (column in needed_values.keys() or column == 'hour'):
                    data = data.drop(column, axis=1)

            data = pd.melt(data, id_vars=['hour'], value_vars=needed_values)


            def get_start_date(contract):
                if is_hour_utc:
                    try:
                        ct = datetime.combine(request_date, time(int(re.findall('\d+', contract)[0])))
                        tz_utc = pytz.timezone('UTC')
                        ct_utc = tz_utc.localize(ct)

                        tz_local = pytz.timezone(line[3])

                        local_start_date = ct_utc.astimezone(tz_local)
                        local_start_date_str = local_start_date.date().strftime('%Y-%m-%d ') + str(local_start_date.time())

                    except Exception as e:
                        print('ERROR-converting-hourUTC-to-hourLocale : ' + str(e))

                else:
                    local_start_date_str = str(request_date) + ' ' + str(re.findall('\d+', contract)[0])+ ':00:00'

                return local_start_date_str


            data = {
                    'name': data['variable'].map(lambda x: station_name_csv + ' ' + x + '_' + needed_values[x] + post_fix),
                    'effective_date': '',
                    'start_date': data['hour'].map(lambda x: get_start_date(x)),
                    'end_date': '',
                    'value' :  data['value'].map(lambda x: re.findall(r'[\d\.\d]+', x)[0] if re.findall(r'[\d\.\d]+', x)!=[] else 0 ),
                    'table': 'spot'
                    }

            data = pd.DataFrame(data)
            data_table = data_table.append(data)

        request_date += timedelta(days=1) #Changing date to the next, until I will get end_date
        open_file.seek(0)
        header_csv = next(csv_reader)
        cnt_days+=1
    
        if cnt_days == CHUNK_SIZE:
            data_table.to_csv(DB_LOADER_DIR + "station_values_( " + str(f_id) + " )" , sep=';',index=False)
            data_table = data_table.iloc[0:0]
            dte_start = request_date
            cnt_days=0
            f_id+=1
        

    
    print("End.")






def format_name(str):

    dic ={
            u'\xe1': 'a', u'\xe2': 'a', u'\xe3': 'a', u'\xe4': 'a', u'\xe5': 'a', u'\xe6': 'a',
        
            u'\xe7': 'c',
        
            u'\xe8': 'e', u'\xe9': 'e', u'\xea': 'e', u'\xeb': 'e',
        
            u'\xf1': 'n',
        
            u'\xf2': 'o', u'\xf3': 'o', u'\xf4': 'o', u'\xf6': 'o',
        
            u'\xed': 'i', u'\xee': 'i',
        
            u'\xfa': 'u', u'\xfb': 'u', u'\xfc': 'u',
        
            u'\xf0': 'd',
        
            u'\xfb': 'th',
        
            u'\xfd': 'y',
        
            '\\': '-', '/': '-','#': '-',
        
            "'": '', '?': '', '\x92': '', '=': '', '*': '', ',': '',
        }
    
    for d in dic:
        str = str.lower().replace(d,dic[d])

    return str




def main():    

    get_data()
    



if __name__ == '__main__':
    main()

