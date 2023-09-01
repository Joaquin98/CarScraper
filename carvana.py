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


class Bot:

    threads_n = 5

    selectors_dict = {
        'brand_section': '//select[@name="makeCodeList"]/option',
        'car_link': '//div/a[@rel="nofollow"]',
        'car_engine': '//div/div[@aria-label="ENGINE_DESCRIPTION"]/parent::div/following-sibling::div',
        'car_name': '//h1[@data-cmp="heading"]',
        'car_owner_name': '//div[@data-cmp="ownerDetailsSnapshot"]//h2',
        'car_owner_contact': '//div[@data-cmp="ownerDetailsSnapshot"]//span[@data-cmp="phoneNumber"]',
        'car_owner_address': '//div[@data-cmp="ownerDetailsSnapshot"]//div[@data-cmp="address"]',
        'car_MPG': '//div/div[@aria-label="MPG"]/parent::div/following-sibling::div',
        'car_MILEAGE': '//div/div[@aria-label="MILEAGE"]/parent::div/following-sibling::div',
        'car_colorSwatch': '//div/div[@data-cmp="colorSwatch"]/parent::div/following-sibling::div',
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

    person_titles = ['user_url', 'person_name',
                     'person_title', 'person_others', 'person_about', 'extraction_date']

    experience_titles = ['user_url', 'experience_link',
                         'experience_title', 'experience_subtitle', 'experience_location', 'experience_date', 'experience_text', 'extraction_date']

    education_titles = ['user_url', 'education_link', 'education_title',
                        'education_subtitle', 'education_date', 'education_text', 'extraction_date']

    def __init__(self) -> None:
        # self.users = users
        # self.iteration()
        self.browser = None

    def get_brands(self):
        while True:
            self.browser = driver_module.get_driver(True)
            search_url = "https://carvana.com/"
            self.browser.get(search_url)
            x = input()
            if x == 's':
                return
        brands_elements = self.browser.find_elements(
            By.XPATH, self.selectors_dict['brand_section'])
        for brand in brands_elements:
            brand_value = brand.get_attribute('value')
            if brand_value != "Any Make":
                self.brands.add(brand_value)

        print(self.brands)

        for brand in self.brands:
            self.browser.get(
                f"https://www.autotrader.com/cars-for-sale/{brand}?endYear=2022&isNewSearch=true&marketExtension=include&numRecords=24&searchRadius=0&sortBy=relevance&startYear=2010")

            link_elements = self.browser.find_elements(
                By.XPATH, self.selectors_dict['car_link'])
            for link in link_elements:
                link_value = link.get_attribute('href')
                if 'car' in link_value:
                    self.add_new_link(link_value)
                    # self.car_links.add(link_value)
            print(len(self.new_car_links))
            self.save_links()
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
        browser = driver_module.get_driver(True)
        for link in link_list:
            ok = self.get_car_info_parrallel(browser, link)
            while not ok:
                browser.close()
                browser = driver_module.get_driver(True)
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
            car_dict['Color'] = self.browser.find_element(
                By.XPATH, self.selectors_dict['car_colorSwatch']).text
        except Exception:
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

        browser.get(car_link)

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
        loaded_users = set()

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


bot = Bot()

bot.get_brands()
