from csv import writer, reader
import datetime
import csv
import codecs
import os
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import driver_module
import undetected_chromedriver as uc
import threading
import re
import sys


class Bot:

    threads_n = 10

    selectors_dict = {
        'brand_section': '//select[@name="makeCodeList"]/option',
        'next_page_filter': '//li/a[@aria-label="Next Page" and @role = "button"]',
        'close_popup': '//button[@aria-label="Close dialog"]',
        'car_link': '//div/a[@rel="nofollow"]',
        'car_engine': '//div/div[@aria-label="ENGINE_DESCRIPTION"]/parent::div/following-sibling::div',
        'car_name': '//h1[@data-cmp="heading"]',
        'car_owner_name': '//div[@data-cmp="ownerDetailsSnapshot"]//h2',
        'car_owner_contact': '//div[@data-cmp="ownerDetailsSnapshot"]//span[@data-cmp="phoneNumber"]',
        'car_owner_address': '//div[@data-cmp="ownerDetailsSnapshot"]//div[@data-cmp="address"]',
        'car_MPG': '//div/div[@aria-label="MPG"]/parent::div/following-sibling::div',
        'car_MILEAGE': '//div/div[@aria-label="MILEAGE"]/parent::div/following-sibling::div',
        'car_colorSwatch2': '//div/div[contains(@class,"color-swatch")]',
        'car_colorSwatch': '//div/div[@data-cmp="colorSwatch"]/parent::div/following-sibling::div',
        'car_data_columns': '//div/ul[@data-cmp="listColumns"]',
        'car_data_accordian': '//div/div[@data-cmp="accordian"]/div[@data-cmp="accordionPanel"]'
    }

    brands = set()
    car_links = set()
    new_car_links = set()

    base_url = 'https://www.cargurus.com/'
    __WAIT_FOR_ELEMENT_TIMEOUT = 10
    new_posts = set()
    all_posts = set()
    DEBUG = True
    browser = None
    loaded_cars = set()
    current_user = None
    results_filename = "./bot_data/links.csv"

    car_titles = ['Url', 'Name', 'Brand', 'Model', 'Type', 'City', 'Engine',
                  'Color', 'Fuel_Type', 'Warranty', 'Dealer_Name', 'Chassis', 'Year', 'Door', 'Seats', 'Power', 'Date']

    def __init__(self) -> None:
        # self.users = users
        # self.iteration()
        # self.browser = driver_module.get_driver()
        pass

    def get_brands(self):
        '''
        Autotrader:
            - Poner paginación en 100
            - Dividir por cada año
            - No se puede cambiar la página por url
            - Se llega máximo hasta la página 40
            - Se tendría que dividir la búsqueda
            https://www.autotrader.com/cars-for-sale/used-cars?
            endYear=2022&firstRecord=311&isNewSearch=false&marketExtension=include&numRecords=24&searchRadius=0&sortBy=relevance&startYear=2010

            https://www.autotrader.com/cars-for-sale/suzuki?endYear=2022&isNewSearch=true&marketExtension=include&numRecords=24&searchRadius=0&sortBy=relevance&startYear=2010
        '''
        search_url = "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=93117&distance=50000"
        search_url = "https://www.autotrader.com/cars-for-sale/all-cars/buick/goleta-ca?zip=93117"
        search_url = "https://carvana.com/"
        search_url = "https://www.autotrader.com/cars-for-sale/used-cars?endYear=2022&isNewSearch=true&marketExtension=include&numRecords=24&searchRadius=0&sortBy=relevance&startYear=2010"
        self.browser = driver_module.get_driver()
        self.browser.get(search_url)

        try:
            WebDriverWait(self.browser, 15).until(EC.presence_of_element_located(
                (By.XPATH, self.selectors_dict['brand_section'])))
        except Exception:
            self.info("No brands")

        # input()
        brands_elements = self.browser.find_elements(
            By.XPATH, self.selectors_dict['brand_section'])
        for brand in brands_elements:
            brand_value = brand.get_attribute('label')
            brand_value = brand_value.strip()
            if brand_value != "Any Make":
                brand_value = brand_value.replace(' ', '-')
                self.brands.add(brand_value)

        self.info("All Brands: " + str(self.brands))

        for brand in self.brands:
            for year in range(2010, 2023):
                self.info(f"Brand: {brand} - Year: {year}")
                url = f"https://www.autotrader.com/cars-for-sale/{brand}?endYear={year}&isNewSearch=true&marketExtension=include&numRecords=100&searchRadius=0&sortBy=relevance&startYear={year}"
                self.info(url)
                results = 0
                self.browser.get(url)

                try:
                    link_elements = self.browser.find_element(
                        By.XPATH, self.selectors_dict['close_popup']).click()
                except Exception as e:
                    pass

                next = True
                while next:

                    link_elements = self.browser.find_elements(
                        By.XPATH, self.selectors_dict['car_link'])
                    for link in link_elements:
                        link_value = link.get_attribute('href')
                        if 'car' in link_value:
                            pattern = 'listingId=(\d{9})'
                            match = re.search(pattern, link_value)
                            if match:
                                self.add_new_link(match.group(1))
                                # self.add_new_link(link_value)

                    results += len(self.new_car_links)
                    self.save_links()
                    time.sleep(1)

                    for i in range(20):
                        place = 400
                        try:
                            self.browser.find_element(
                                By.XPATH, self.selectors_dict['next_page_filter']).click()
                            time.sleep(4)
                            break
                        except Exception as e:
                            # print(e)
                            self.browser.execute_script(
                                f"window.scrollTo(0, {place});")
                            time.sleep(0.3)
                            place += 400
                        if i == 19:
                            next = False

                    self.info(f"Results {results}")
                time.sleep(3)

            time.sleep(3)
            # input()

        # self.browser.get("https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=93117&inventorySearchWidgetType=AUTO&sortDir=ASC&sourceContext=untrackedWithinSite_false_0&distance=10000&sortType=BEST_MATCH&entitySelectingHelper.selectedEntity=m3#resultsPage=2")

    def create_url(self, user, country):
        user = user.replace("www.", country + ".") + self.google_reference
        return user

    def save_car(self, car_json, car_url):
        car_json['Url'] = car_url
        with codecs.open('./data/cars.csv', 'a+', 'utf8') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(
                [car_json[title] if title in car_json.keys() else None for title in self.car_titles])
            f_object.close()

    def add_new_link(self, link):
        if link not in self.car_links:
            self.car_links.add(link)
            self.new_car_links.add(link)

    def save_links(self):
        links_txt = ""
        for link in self.new_car_links:
            links_txt += link + "\n"
        file_obj = codecs.open(self.results_filename, 'a+', "utf-8")
        file_obj.write(links_txt)
        file_obj.close()
        self.new_car_links = set()

    def info(self, message):
        if self.DEBUG:
            print("-> ", message)

    def start(self):
        self.info(f"Loaded Cars: {len(self.loaded_cars)}")
        self.info(f"Total Links: {len(self.car_links)}")

        for link in self.car_links:
            if link not in self.loaded_cars:
                self.get_car_info(link)

    def thread_function(self, index, link_list):
        self.info(f"Thread Init {index}")
        proxy = False  # True
        browser = driver_module.get_driver(proxy)
        for link in link_list:
            ok = self.get_car_info_parrallel(browser, link)
            while not ok:
                # browser.close()
                # browser = driver_module.get_driver(proxy)
                ok = self.get_car_info_parrallel(browser, link)
        browser.close()

    def start_parallel(self):
        self.info(f"Loaded Cars: {len(self.loaded_cars)}")
        self.info(f"Total Links: {len(self.car_links)}")

        links_to_fetch = []

        for link in self.car_links:
            if link not in self.loaded_cars:
                links_to_fetch.append(link)

        links_threads_list = [[] for _ in range(self.threads_n)]
        links_len = len(links_to_fetch)
        i = 0
        for link in links_to_fetch:
            links_threads_list[i].append(link)
            i += 1
            i %= self.threads_n

        self.threads = list()

        for index in range(self.threads_n):
            print("CREANDO HILO ", index)

            x = threading.Thread(target=self.thread_function, args=(
                index, links_threads_list[index]))
            self.threads.append(x)
            time.sleep(1)
            x.start()

        for index, thread in enumerate(self.threads):
            print("ESPERANDO HILO ", index)
            thread.join()
            print("HILO ", index, " TERMINADO", index)

    def get_car_info(self, car_link):

        self.browser.get(car_link)

        car_dict = {}
        try:
            car_dict['Name'] = self.browser.find_element(
                By.XPATH, self.selectors_dict['car_name']).text
        except Exception:
            pass

        try:
            car_dict['Engine'] = self.browser.find_element(
                By.XPATH, self.selectors_dict['car_engine']).text
        except Exception:
            pass

        try:
            car_dict['Dealer_Name'] = self.browser.find_element(
                By.XPATH, self.selectors_dict['car_owner_name']).text
        except Exception:
            pass

        try:
            car_dict['City'] = self.browser.find_element(
                By.XPATH, self.selectors_dict['car_owner_address']).text
        except Exception:
            pass

        try:
            colors = self.browser.find_elements(
                By.XPATH, self.selectors_dict['car_data_columns'])

            print(self.selectors_dict['car_colorSwatch'])
            print(colors)
            for color in colors:
                car_dict['Color'] += color.text + "\n"
            print(car_dict['Color'])
        except Exception as e:
            print(e)
            pass

        car_dict['Date'] = datetime.datetime.now().strftime(
            "%d/%m/%Y, %H:%M:%S")

        self.save_car(car_dict, car_link)

    def get_year_brand_model_from_name(self, name):
        return name.split(" ", 3)

    def get_fuel_type_from_engine(self, engine):
        fuel_type = None
        if "Gas/Electric" in engine:
            fuel_type = "Gas/Electric"
        elif "Gas" in engine:
            fuel_type = "Gas"
        elif "Fuel" in engine:
            fuel_type = "Fuel"
        else:
            fuel_type = "Electric"

        return fuel_type

    def get_car_info_parrallel(self, browser, car_link):
        car_link = "https://www.autotrader.com/cars-for-sale/vehicledetails.xhtml?listingId=" + car_link
        browser.get(car_link)
        # self.browser.execute_script(
        #    f"window.scrollTo(0, {700});")
        car_dict = {}
        try:
            car_dict['Name'] = browser.find_element(
                By.XPATH, self.selectors_dict['car_name']).text
        except Exception:
            pass

        if 'Name' not in car_dict.keys():
            return False

        try:
            car_dict['Engine'] = browser.find_element(
                By.XPATH, self.selectors_dict['car_engine']).text
        except Exception:
            pass

        try:
            car_dict['Dealer_Name'] = browser.find_element(
                By.XPATH, self.selectors_dict['car_owner_name']).text
        except Exception:
            pass

        try:
            car_dict['City'] = browser.find_element(
                By.XPATH, self.selectors_dict['car_owner_address']).text
        except Exception:
            pass

        try:
            colors = browser.find_elements(
                By.XPATH, self.selectors_dict['car_colorSwatch'])
            car_dict['Color'] = ""
            for color in colors:
                car_dict['Color'] += color.text + "\n"
        except Exception as e:
            print(e)
            pass

        if 'Name' in car_dict.keys():
            _, car_dict['Year'], car_dict['Brand'], car_dict['Model'] = self.get_year_brand_model_from_name(
                car_dict['Name'])

        if 'Engine' in car_dict.keys():
            car_dict['Fuel_Type'] = self.get_fuel_type_from_engine(
                car_dict['Engine'])

        car_dict['Date'] = datetime.datetime.now().strftime(
            "%d/%m/%Y, %H:%M:%S")

        self.save_car(car_dict, car_link)

        return True

    def start_files(self):

        if not os.path.exists('./bot_data'):
            os.makedirs('./bot_data')

        if not os.path.exists('./bot_data/links.csv'):
            file = codecs.open('./bot_data/links.csv', 'a+', 'utf8')
            file.close()
        else:
            with codecs.open('./bot_data/links.csv', "r", encoding="utf8") as file:
                reader = csv.reader(file, delimiter=",")
                for row in reader:
                    self.car_links.add(row[0])

        if not os.path.exists('./data'):
            os.makedirs('./data')

        if not os.path.exists('./data/cars.csv'):
            file = codecs.open('./data/cars.csv', 'a+', 'utf8')
            file.write(",".join(Bot.car_titles) + "\n")
            file.close()
        else:
            with codecs.open('./data/cars.csv', "r", encoding="utf8") as file:
                reader = csv.reader(file, delimiter=",")
                first = True
                for row in reader:
                    if first:
                        self.loaded_cars.add(row[0])
                    else:
                        first = False

    def get_id_from_links(self):
        init_set = self.car_links
        print(len(init_set))
        for link in init_set:
            pattern = 'listingId=(\d{9})'
            match = re.search(pattern, link)
            if match:
                self.new_car_links.add(match.group(1))
        self.save_links()


if __name__ == "__main__":
    bot = Bot()
    bot.start_files()
    option = int(
        input("1 - Get post ids.\n2 - Get data from stored post ids.\n"))

    if option == 1:
        bot.get_brands()
    elif option == 2:
        bot.start_parallel()
    else:
        print("Wrong input")
