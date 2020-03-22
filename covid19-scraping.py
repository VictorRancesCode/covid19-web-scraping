from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import json

from bs4 import BeautifulSoup
import pandas as pd

# the controller is being used in macos and is using another, you can change it for another
driver = webdriver.Chrome("/usr/local/bin/chromedriver")
driver.get("https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6")

try:
    element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "ember228"))
    )
    content = driver.page_source
    data= BeautifulSoup(content)
    # Confirmed by Country
    confirmed_cases= driver.find_element_by_id("ember34")
    list_confirmed = confirmed_cases.find_element_by_class_name("feature-list")
    data= BeautifulSoup(list_confirmed.get_attribute('innerHTML'), 'html.parser')
    countries = []
    confirmed_case= []
    list_country = {}
    for a in data.findAll('span', attrs={'class':'flex-horizontal feature-list-item ember-view'}):
        count=a.find('span', attrs={'style':'color:#e60000'}).text
        country=a.find('span', attrs={'style':'color:#d6d6d6'}).text
        list_country[country]={
            'name':country,
            'confirmed_case': count,
            'provinces': {}
        }
        #countries.append(country)
        #confirmed_case.append(count)

    #Confirmed By Province
    confirmed_cases= driver.find_element_by_id("ember41")
    list_confirmed = confirmed_cases.find_element_by_class_name("feature-list")
    data2= BeautifulSoup(list_confirmed.get_attribute('innerHTML'), 'html.parser')
    for item in data2.findAll('span', attrs={'class':'flex-horizontal feature-list-item ember-view'}):
        count=item.findAll('p')[0].find('span', attrs={'style':'color:#e60000'}).text.split('\xa0')
        country_and_state = item.findAll('p')[1].text.split('\xa0')
        if(len(country_and_state)>0):
            province = country_and_state[1]
            if(country_and_state[0]!=""):
                province = country_and_state[0]
            list_country[country_and_state[1]]['provinces'][province]={'name':province,'confirmed':count }
        else:
            country_aux=country_and_state[0]
            list_country[country_aux]['provinces'][country_aux]={'name':country_aux,'confirmed':count }

        # if(len(country_and_state)>0):
        #     countries.append(country_and_state[0]+" "+country_and_state[1])
        # else:
        #     countries.append(country_and_state[0])
        # confirmed_case.append(count[0])

    #Deaths by Province
    deaths= driver.find_element_by_id("ember84")
    list_deaths = deaths.find_element_by_class_name("feature-list")
    data3= BeautifulSoup(list_deaths.get_attribute('innerHTML'), 'html.parser')
    for item in data3.findAll('span', attrs={'class':'flex-horizontal feature-list-item ember-view'}):
        count=item.findAll('p')[0].find('span', attrs={'style':'color:#ffffff'}).text.split('\xa0')
        country_and_state = item.findAll('p')[1].text.split('\xa0')
        if(len(country_and_state)>0):
            province = country_and_state[1]
            if(country_and_state[0]!=""):
                province = country_and_state[0]

            if(province in list_country[country_and_state[1]]['provinces']):
                list_country[country_and_state[1]]['provinces'][province]['deaths']=count
            else:
                list_country[country_and_state[1]]['deaths']=count
        else:
            if(country_and_state[0] in  list_country[country_and_state[0]]['provinces']):
                list_country[country_and_state[0]]['provinces'][country_and_state[0]]['deaths']=count
            else:
                country_aux= country_and_state[0]
                list_country[country_aux]['provinces'][country_aux]={'name':country_aux,'deaths':count }

     #Recovered by Province
    recovered= driver.find_element_by_id("ember98")
    list_recovered = recovered.find_element_by_class_name("feature-list")
    data4= BeautifulSoup(list_recovered.get_attribute('innerHTML'), 'html.parser')
    for item in data4.findAll('span', attrs={'class':'flex-horizontal feature-list-item ember-view'}):
        count=item.findAll('p')[0].find('span', attrs={'style':'color:#70a800'}).text.split(' ')
        country_and_state = item.findAll('p')[1].text.split('\xa0')
        if(len(country_and_state)>0):
            province = country_and_state[1]
            if(country_and_state[0]!=""):
                province = country_and_state[0]
            if(province in list_country[country_and_state[1]]['provinces']):
                list_country[country_and_state[1]]['provinces'][province]['recovered']=count
            else:
                list_country[country_and_state[1]]['provinces'][province]={'name':province,'recovered':count }
        else:
            if(country_and_state[0] in list_country[country_and_state[0]]['provinces']):
                list_country[country_and_state[0]]['provinces'][country_and_state[0]]['recovered']=count
            else:
                list_country[country_and_state[0]]['provinces'][country_and_state[0]]={'name':country_and_state[0],'recovered':count }

    with open('result.json', 'w') as fp:
        json.dump(list_country, fp)

    list_countries = []
    list_province = []
    list_confirmed =[]
    list_deaths = []
    list_recovered = []
    for key in list_country:
        item = list_country[key]
        if('provinces' in item):
            for key_province in item['provinces']:
                list_countries.append(key)
                province =item['provinces'][key_province]
                list_province.append(province['name'])
                if('confirmed' in province):
                    list_confirmed.append(province['confirmed'][0])
                else:
                    if float(list_country[key]['confirmed_case'])<3:
                        list_confirmed.append(list_country[key]['confirmed_case'])
                    else:
                        list_confirmed.append('0')

                if('deaths' in province):
                    list_deaths.append(province['deaths'][0])
                else:
                    list_deaths.append('0')
                
                if('recovered' in province):
                    list_recovered.append(province['recovered'][0])
                else:
                    list_recovered.append('0')
                

    

    df = pd.DataFrame({'Country':list_countries, 'Province':list_province,'Confirmed Case':list_confirmed,'Deaths':list_deaths,'Recovered':list_recovered}) 
    df.to_csv('DataCoronavirusWorld.csv', index=False, encoding='utf-8')
finally:
    driver.quit()
