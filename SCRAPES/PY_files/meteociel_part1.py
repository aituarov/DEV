import requests, urllib.request

import re

from lxml import html

import pandas as pd

from lxml import etree
 

SCRIPT_DIR = "C:\\DEV\\output\\"

 
def get_data():
    url="http://www.meteociel.fr/temps-reel/obs_villes.php"

    response = requests.get(url)

    page = html.fromstring(response.text)

    attribute1 = page.xpath('//select[@id="paysdept"]/option')

    out2 = [e.get("value").replace('\n','') for e in attribute1]

    regions = pd.DataFrame({'name'  :  out2})

    regions = regions[~(regions.name.str.startswith('dept')) & ~(regions.name=='none') & ~(regions.name=='') ]



    #Loop through each regions

    url = "http://www.meteociel.fr/cartes_obs/stationselect_helper.php?deptpays="

    dataTbl = pd.DataFrame()

    for i in range(len(regions)) :

        region_name = regions.name.iloc[i]

        print("DEBUG-location: *" + str(i) + "* for '" + region_name + "'" )

        response = requests.get( url + region_name )

        page = html.fromstring(response.text)

        el = page.xpath('//body')

        json_str = el[0].text_content()

        data = [[e.replace(' ','').replace('\n','') for e in row.split('|')] for row in json_str.split('\n')]

        data = pd.DataFrame(data)

        data = {'region'    :  region_name,

              'location'  :  data[1].map(lambda x: format_name(x).replace( ")" , "" ).replace( "(" , "_" ).capitalize() if x else "NaN"),

              'code_2'    :  data[0]}

        data = pd.DataFrame(data)

        data = data.dropna()

        dataTbl = dataTbl.append(data)

        dataTbl = dataTbl[~(dataTbl.location == 'NaN') ]
        
            
    dataTbl.to_csv(SCRIPT_DIR + "locations_list.csv", sep=';',index=False)
    
    
    
    
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
