import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import json

all = []

def getNumbersFromStr(str):
    numbers = []
    nums = str.split('.')
    for num in nums:
        numbers.append(''.join([n for n in num if n.isdigit()]))
    res = ''
    if len(numbers) > 1:
        res = numbers[0] + '.' + numbers[1]
    else:
        res = numbers[0]
    if res == '':
        return 0
    else:
        return float(res)

def getAllMobiles():
    firefox_driver_path = 'geckodriver.exe'
    delay = 15

    driver = webdriver.Firefox(executable_path=firefox_driver_path)

    def extract_text(soup_obj, tag, attribute_name, attribute_value):
        txt = soup_obj.find(tag, {attribute_name: attribute_value}).text.strip() if soup_obj.find(tag, {attribute_name: attribute_value}) else ''
        return txt

    rows = []
    index = 0

    def getDiscountedPrice(sellingPrice, marketPrice):
        sPrice = getNumbersFromStr(sellingPrice)
        mPrice = getNumbersFromStr(marketPrice)
        if mPrice == 0:
            return '0'
        else:
            return str(((mPrice-sPrice)/mPrice)*100)
    
    # scrape the Sharaf Dg site for mobiles
    for page_number in range(1, 10):
        page_url = f'https://uae.sharafdg.com/c/mobiles_tablets/mobiles/?page_number={page_number}'
        driver.get(page_url)
        time.sleep(5)

        try:
            # lets wait for the html to load all mobiles, the class element 'product-items' will contain all the mobiles in Sharaf Dg
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'product-items')))
        except TimeoutException:
            print('Loading exceeds delay time')
            break
        else:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            mobile_list = soup.find('div', {'class': 'product-items'})
            mobiles = mobile_list.find_all('div', {'class': 'slide'})
            site = 'sharafdg'
            for mobile in mobiles:   
                mobile_url = 'https:' + mobile.find_all('a', href=True)[0]['href']
                mobile_name = mobile.findAll(attrs={'class' : 'name'})[0].text
                mobile_price = mobile.findAll(attrs={'class' : 'price'})[0].text
                mobile_market_price = mobile.findAll(attrs={'class' : 'cross-price'})[0].text
                discount = getDiscountedPrice(mobile_price, mobile_market_price) + '%'
                mobile_image_url = 'https:' + mobile.find_all('img')[0]['src']
                mobile_brand = mobile_name.split(' ', 1)[0]
                index += 1

                data = {
                    "mobile_url": mobile_url,
                    "mobile_name": mobile_name,
                    "mobile_price": mobile_price,
                    "mobile_market_price": mobile_market_price,
                    "discount": discount,
                    "mobile_image_url": mobile_image_url,
                    "mobile_brand": mobile_brand,
                    "id": index, # need to give unique ids for each mobile
                    "site": site
                }

                all.append(data)

    # scrape the noon site for mobiles
    for page_number in range(1, 10):
        page_url = f'https://www.noon.com/uae-en/electronics-and-mobiles/mobiles-and-accessories/mobiles-20905/?page={page_number}'
        driver.get(page_url)
        time.sleep(5)

        try:
            # lets wait for the html to load all mobiles, the class element 'sc-1be8ju5-7' will contain all the mobiles in noon
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'sc-1be8ju5-7')))
        except TimeoutException:
            print('Loading exceeds delay time')
        else:
            # noon loads the images and some other data only if they are in view, so need to scroll the webpage entirely
            for i in range(0, 3500):
                driver.execute_script("window.scrollBy(0,15)")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            mobile_list = soup.find('div', {'class': 'sc-1be8ju5-7'})
            mobiles = mobile_list.find_all('div', {'class': 'productContainer'})
            site = 'noon'
            for mobile in mobiles: 
                m = mobile.find('img', {'class': 'eytPMO'})
                mobile_url = 'https://noon.com' + mobile.find('a', href=True)['href']
                mobile_price = extract_text(mobile, 'div', 'class', 'sc-sxpmji-1 hWCRR')[1:-3]
                mobile_market_price = mobile.find_all(attrs={'class' : 'oldPrice'})[0].text if mobile.find_all(attrs={'class' : 'oldPrice'}) else '--'
                discount = mobile.find_all(attrs={'class' : 'discount'})[0].text if mobile.find_all(attrs={'class' : 'discount'}) else '--'
                # mobile_image_url = mobile.find(attrs={'class' : 'eytPMO'})['src'] if mobile.find(attrs={'class' : 'eytPMO'}) else '--'
                mobile_image_url = m['src']
                mobile_name = mobile.find(attrs={'class' : 'eytPMO'})['alt'] if mobile.find(attrs={'class' : 'eytPMO'}) else '--'
                mobile_brand = mobile_name.split(' ', 1)[0]
                index += 1

                data = {
                    "mobile_url": mobile_url,
                    "mobile_name": mobile_name,
                    "mobile_price": mobile_price,
                    "mobile_market_price": mobile_market_price,
                    "discount": discount,
                    "mobile_image_url": mobile_image_url,
                    "mobile_brand": mobile_brand,
                    "id": index,
                    "site": site
                }
                all.append(data)

    # lets save all the scraped data in the json file
    json_string = json.dumps(all)
    with open('mobiles-data.json', 'w') as outfile:
        outfile.write(json_string)
    print('Task completed successflly, please check the mobiles-data.json file. Run api.py to automate search integration')
    driver.quit()

getAllMobiles()
