from selenium import webdriver
from selenium.webdriver.common.by import By
from csv import writer
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import time


driver = webdriver.Firefox()
driver.get("https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Muenchen.90.1.1.0.html?csrf_token=e30a4dc9d48c5137b2a74a3fdcd85f91a2536c55&offer_filter=1&city_id=90&sort_column=&sort_order=&noDeact=&dFr=&dTo=&radLat=&radLng=&clear_vu=&autocompinp=M%C3%BCnchen+(Bayern)&country_code=de&city_name=Muenchen&categories[]=1&rent_types[]=0&sMin=&rMax=&pu=&hidden_dFrDe=&hidden_dToDe=&radAdd=&radDis=&wgSea=&wgMnF=&wgMxT=&wgAge=&wgSmo=&rmMin=&rmMax=&fur=&pet=&sin=&exc=&kit=&flo=&pagination=1")

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

#use soup to get all attributes
all_title =[]
all_price= []
all_space = []
all_time = []
all_district = []
all_address =[]
all_rooms =[]
all_link = []

#get all attributes from a single page(soup)
def getStrings(soup):
    #title
    div_title_container = soup.find_all('h3', class_='truncate_title noprint')  
    for d in div_title_container:
     items_title= d.find_all('a')
     for t in items_title:
        all_title.append(t.contents[0].strip().replace('\n', '').replace(' ', ''))



    #price
    div_container = soup.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['col-xs-3'])  

    for d in div_container:
        items_price= d.find_all('b')
        for p in items_price:
            all_price.append(p.contents[0].replace(' €', ''))


    #space
    div_space_container = soup.find_all('div', class_='col-xs-3 text-right')  

    for d in div_space_container:
        items_space= d.find_all('b')
        for s in items_space:
            all_space.append(s.contents[0].replace(' m²', ''))


    #time
    div_time_container = soup.find_all('div', class_='col-xs-5 text-center')  

    for d in div_time_container:

            all_time.append(d.contents[0].strip().replace('\n', '').replace('ab', '').replace(' ', ''))

  

    #room,district, address
    div_district_container = soup.find_all('div', class_='col-xs-11')  

    for d in div_district_container:
        items_district= d.find_all('span')
        for di in items_district:
            all_rooms.append(di.contents[0].strip().replace('\n', '').replace('ab', '').replace(' ', '').split("|")[0])
            all_district.append(di.contents[0].strip().replace('\n', '').replace('ab', '').replace(' ', '').split("|")[1])
            all_address.append(di.contents[0].strip().replace('\n', '').replace('ab', '').replace(' ', '').split("|")[2])
   
    #link
    div_link_container = soup.find_all('h3', class_='truncate_title noprint')

    for l in div_link_container:
     items_link= l.find_all('a', href = True)
     for a in items_link:
        all_link.append(a['href'])

    


# first page attributes
getStrings(soup)


#go to the next 5 pages by click next button
for i in range(5):
    wait = WebDriverWait(driver, 20)
    button = driver.find_element(by=By.XPATH, value='//a[@class="page-link next"]')
    #driver click next button to the next page
    driver.execute_script("arguments[0].click();", button)

    time.sleep(5) # sleep three seconds so page can load

    html = driver.page_source # now this has new reviews on it
    soup = BeautifulSoup(html, 'html.parser') # now you have soup again, but with new reviews

    getStrings(soup)

# analysis of schwabing
sumPrice = 0
sumSpace = 0
count = 0
averagePrice = 0
averageSpace = 0
averagePS = 0


for i in range(0,len(all_district)):
    if all_district[i].find("Schwing") == -1:
        continue
    else:
        sumSpace = sumSpace + int(all_space[i])
        sumPrice = sumPrice + int(all_price[i])
        count = count +1

averagePrice = sumPrice/count
averageSpace = sumSpace/count
averagePS = sumPrice/sumSpace


# export all attributes into csv file

with open('housing.csv', 'w', encoding='utf8', newline='') as f:
    thewriter = writer(f)
    header = ['Title', 'District', 'Price €', 'Space m²', 'Rooms', 'available since', 'URL']
    thewriter.writerow(header)

    for x in range(len(all_title)):
        t = all_title[x]
        d = all_district[x]
        p = all_price[x]
        s = all_space[x]
        r = all_rooms[x]
        a = all_time[x]
        l = "https://www.wg-gesucht.de"+all_link[x]
        
        #print("Title= {}, District= {}, Price€= {}, Space m²= {}, Rooms= {}, Available since= {}, Url= {}".format(t, d, p, s, r, a,l))
        info = [t,d,p,s,r,a,l]
        thewriter.writerow(info)

    driver.quit()