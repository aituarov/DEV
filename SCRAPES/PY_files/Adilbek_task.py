# import pandas as pd
# import time
# from datetime import date,datetime,timedelta
# from dateutil.relativedelta import relativedelta
# from lxml import html

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import TimeoutException
# from selenium.common.exceptions import NoSuchElementException 
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By

# from selenium.webdriver.common.action_chains import ActionChains



# __author__ = 'berclc'



# requestDate = datetime.today().date() + timedelta(days=-54)

# ALIAS = ["BRENT", "API2", "NEWC", "CO2", "TTF", "NBP"]

# CMDTY = ["ICE Brent Crude Futures - North Sea", "ICE Rotterdam Coal Futures - ARA", 
#          "gC Newcastle Coal Futures - Newcastle", "ICE ECX EUA Futures - ECX", 
#          "ICE Endex Dutch TTF Gas Base Load Futures","ICE UK Natural Gas Futures - NBP"]

# SERIE_NAME = ["brent - oth price fwd", "API2 - oth price fwd", "NEWC - oth price fwd", 
#               "CO2 - oth price fwd", "TTF - gas price fwd", "NBP - gas price fwd"]

# # Vor extra
# F_D_ID = [3498, 3484, 4112, 3494, 3507]
# DB_LOADER_DIR_2 = "R:\\Trading\\Prop\\stdloader\\" 


# url = "https://www.ice.if5.com/ViewData/EndOfDay/FuturesReport.aspx"
# USERNAME = 'cberclaz_electroroute'
# PASSWORD = 'Bai01ley'
# DB_LOADER_DIR = "C:\\DEV\\output\\"

# chrome_options = Options()
# ignored_exceptions = ['TimeoutException','StaleElementReferenceException','NoSuchElementException']


# def retrieve_data():

#     driver = webdriver.Chrome(options = chrome_options)

#     driver.get(url)

#     time.sleep(2)

#     elUsername = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_LoginControl_m_userName"]')
#     elUsername.send_keys(USERNAME)
#     elPassword = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_LoginControl_m_password"]')
#     elPassword.send_keys(PASSWORD)
#     btnLogin = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_LoginControl_LoginButton"]')
#     btnLogin.click()

#     time.sleep(2)

#     lnkFutures = driver.find_element_by_xpath('//a[text()="Futures Report"]')
#     lnkFutures.click()

#     print("Get data for *"+ requestDate.strftime('%d/%m/%Y') +"*")

#     slCalendar = driver.find_element_by_xpath('//img[@id="ctl00_ContentPlaceHolder1_imgDate"]')
#     slCalendar.click()
    
#     #******************************     First I chose a date, after chose commoditites   *************************************#
    
#     #Checking the month and year of the calendar with requestDate's month and year
#     elCalendarTitle = driver.find_element_by_xpath('//div[@id="ctl00_ContentPlaceHolder1_calendarButtonExtender_popupDiv"]/div[1]/div[3]')

#     if(elCalendarTitle.text != requestDate.strftime('%B, %Y')): #There in elCalendarTitle.text will be month, year
#         elCalendarTitle.click()
#         if(elCalendarTitle.text != requestDate.strftime('%Y')): #There in elCalendarTitle.text will be just year
#             while int(elCalendarTitle.text) > requestDate.year: #Go to previous year until we get requestDate's year
#                 prevYear = driver.find_element_by_xpath('//div[@id="ctl00_ContentPlaceHolder1_calendarButtonExtender_prevArrow"]')
#                 prevYear.click()
                
#         monthCalendar = driver.find_element_by_xpath('//tbody[@id="ctl00_ContentPlaceHolder1_calendarButtonExtender_monthsBody"]')  
#         month = monthCalendar.find_element_by_xpath('//div[@title="' + requestDate.strftime("%B, %Y") +'"]')

#         actions = ActionChains(driver)
#         actions.move_to_element(month).perform()
#         month.click() #Chose right month of the year

#     opCalendar = driver.find_element_by_xpath('//tbody[@id="ctl00_ContentPlaceHolder1_calendarButtonExtender_daysBody"]')
#     listDates = [el.get_attribute("title") for el in  opCalendar.find_elements_by_xpath('.//tr/td/div')]

#     if requestDate.strftime('%A, %B %d, %Y') not in listDates :
#         print("The requested date *" + requestDate.strftime('%A, %B %d, %Y') + "* is not available in the calendar")
#         raise Exception('STOP')

#     opCalendar = driver.find_element_by_xpath('//tbody[@id="ctl00_ContentPlaceHolder1_calendarButtonExtender_daysBody"]')
#     opCalendar.find_element_by_xpath('//div[@title="' + requestDate.strftime('%A, %B %d, %Y') + '"]').click()

#     time.sleep(7)

#     dataTbl = pd.DataFrame()
    
#     for i in range(len(CMDTY)) :
#         slCommodity = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlFutures"]')
#         slCommodity.find_element_by_xpath('./option[text()="'+CMDTY[i]+'"] | ./option[text()="'+CMDTY[i].upper()+'"]').click()

#         time.sleep(5)

#         elEmptyData = driver.find_elements_by_xpath('//div[@id="ctl00_ContentPlaceHolder1_UpdatePanel1" and contains(.,"no data available")]')
#         if elEmptyData: 
#            print("Request date *" + requestDate.strftime("%d/%m/%Y") + "* not business day")
#            raise Exception('STOP')

#         elDataMonth = driver.find_elements_by_xpath('//div[@class="PeriodTypeStyle" and contains(.,"Month")]')
#         if not elDataMonth: 
#            print("WARNING-elDataMonth: Monthly table not visible")
#            raise Exception('STOP')

#         txtTitle = driver.find_element_by_xpath('//div[@id="ctl00_ContentPlaceHolder1_UpdatePanel1"]/div[1]').text.upper()
#         if not  CMDTY[i].upper() in txtTitle:
#            print("WARNING-txtTitle: '" + CMDTY[i] + "' not appearing in title *" + txtTitle + "*")
#            raise Exception('STOP')
#         if not  requestDate.strftime("%d %B %Y").upper() in txtTitle:
#            print("WARNING-txtTitle: '" +  requestDate.strftime("%d %B %Y").upper() + "' not appearing in title *" + txtTitle + "*")
#            raise Exception('STOP')

#         #******************************     PARSE the CMDTY price table   *************************************#
#         elTable = driver.find_element_by_xpath('//div[@class="PeriodTypeStyle" and contains(.,"Month")]/../div[2]/table')

#         tableref = html.fromstring(elTable.get_attribute('outerHTML'))
#         header = [e.text_content().replace(' ','').replace('\n','') for e in tableref.xpath('./tbody/tr[1]/th')]
#         data = [[e.text_content().replace(' ','').replace('\n','') for e in row] for row in tableref.xpath('./tbody/tr[position()>1]')]
#         data = pd.DataFrame(data, columns=header)

#         data = {'start_date':  data['Expiry'].map(lambda x: get_start_date(x)),
#                 'end_date'  :  data['Expiry'].map(lambda x: get_end_date(x)),
#                 'value'     :  data['Sett'].map(lambda x: float(x) if x.replace(".","",1).isdigit() else float("NaN"))}

#         data = pd.DataFrame(data)
#         data = data.dropna()
#         data['effective_date'] = requestDate
#         data['alias'] = ALIAS[i]

#         dataTbl = dataTbl.append(data)


#     return dataTbl



# def get_start_date(contract):
#     try:
#         if len(contract) == 5:
#             if contract[0] == 'Q':  # Quarter
#                 dte = datetime(2000 + int(contract[-2:]), (int(contract[1]) - 1) * 3 + 1, 1)
#             else:  # Month
#                 dte = datetime.strptime(contract, "%b%y")
#         elif len(contract) == 6:  # cal
#             dte = datetime(2000 + int(contract[-2:]), 1, 1)
#         else:
#             return None
#         return dte
#     except:
#         return None


# def get_end_date(contract):
#     try:
#         if len(contract) == 5:
#             if contract[0] == 'Q':  # Quarter
#                 dte = datetime(2000 + int(contract[-2:]), (int(contract[1]) - 1) * 3 + 1, 1) + relativedelta(months=3,
#                                                                                                              days=-1)
#             else:  # Month
#                 dte = datetime.strptime(contract, "%b%y") + relativedelta(months=1, days=-1)
#         elif len(contract) == 6:  # cal
#             dte = datetime(2000 + int(contract[-2:]), 12, 31)
#         else:
#             return None
#         return dte
#     except:
#         return None
    


# def write_stdldr(data,f_id):

#     data = pd.merge(data, pd.DataFrame({'alias': ALIAS,'name': SERIE_NAME}), on='alias')
#     data['effective_date'] = data['effective_date'].map(lambda x: datetime.strftime(x,'%Y-%m-%d %H:%M:%S'))
#     data['start_date'] = data['start_date'].map(lambda x: datetime.strftime(x,'%Y-%m-%d %H:%M:%S'))
#     data['end_date'] = data['end_date'].map(lambda x: datetime.strftime(x,'%Y-%m-%d %H:%M:%S'))
#     data['table'] = 'fcast'
#     data = data[["name","effective_date","start_date","end_date","value","table"]]
#     outfile = DB_LOADER_DIR + "Adilbek_py_iceEU_EOD_("+str(f_id)+")_"+ requestDate.strftime('%Y_%m_%d') +".csv"
#     data.to_csv(outfile, sep=';',index=False)




# def write_vor(data,f_id):

#     data = pd.merge(data, pd.DataFrame({'alias': ALIAS,'name': SERIE_NAME}), on='alias')
#     data['F_DatetimeTick'] = data['effective_date'].map(lambda x: datetime.strftime(x,'%Y-%m-%d %H:%M:%S'))
#     data['F_UTC_Datetime'] = data['start_date'].map(lambda x: datetime.strftime(x,'%Y-%m-%d %H:%M:%S'))
#     data['F_value'] = data['value']
#     data = data[["name","F_UTC_Datetime","F_DatetimeTick","F_value"]]
#     outfile = DB_LOADER_DIR_2 + "py_iceEU_EOD_("+str(f_id)+")_"+ datetime.today().strftime('%Y_%m_%d_%H%M%S') +".csv"
#     data.to_csv(outfile, sep=';',index=False)


# def main():

#     print("Retrieve...")
#     data = retrieve_data()

#     print("Write data...")
#     write_stdldr(data,0)
#     #write_vor(data,0)

#     print("End.")



# if __name__ == '__main__':
#     main()

print("Hello world")