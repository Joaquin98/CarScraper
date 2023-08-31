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

"https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=93117&distance=50000"


########################## PARAMETROS PARA CAMBIAR ##################################
NUMERO_DE_HILOS = 6
#####################################################################################


class Bot:

    selectors_dict = {
        'brand_section2': '//select[@name="selectedMakeId"]/optgroup[contains(@label,"All")]/option',
        'brand_section': '//select[@name="makeCodeList"]/option',
        'car_link': '//div/a[@rel="nofollow"]'
    }

    brands = set()
    car_links = set()
    new_car_links = set()

    base_url = 'https://www.cargurus.com/'
    __WAIT_FOR_ELEMENT_TIMEOUT = 10
    new_posts = set()
    all_posts = set()
    browser = None
    loaded_users = set()
    current_user = None
    results_filename = "./bot_data/links.csv"

    car_titles = ['Name', 'Brand', 'Model', 'Type', 'City', 'Engine',
                  'Color', 'Fuel_Type', 'Warranty', 'Dealer_Name', 'Chassis', 'Year', 'Door', 'Seats', 'Power']

    person_titles = ['user_url', 'person_name',
                     'person_title', 'person_others', 'person_about', 'extraction_date']

    experience_titles = ['user_url', 'experience_link',
                         'experience_title', 'experience_subtitle', 'experience_location', 'experience_date', 'experience_text', 'extraction_date']

    education_titles = ['user_url', 'education_link', 'education_title',
                        'education_subtitle', 'education_date', 'education_text', 'extraction_date']

    def __init__(self) -> None:
        # self.users = users
        # self.iteration()
        self.browser = driver_module.get_driver()

    def get_brands(self):
        '''
        Autotrader:
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
        self.browser.get(search_url)
        input()
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

    def iteration(self):
        self.users_errors = []

        while len(self.users):
            times = 0
            self.browser = driver_module.get_driver2()
            for country in self.countries:
                if len(self.users):
                    if times == 5:
                        self.browser.close()
                        self.browser = driver_module.get_driver2()
                    times += 1
                    user = self.users.pop()
                    self.current_user = user
                    url = self.create_url(user, country)
                    try:
                        self.browser.get(url)
                        time.sleep(3)
                        try:
                            self.get_education()
                            self.get_experience()
                            self.get_person()
                        except Exception as e:
                            # print(e)
                            self.users_errors.append(user)
                    except Exception as e:
                        # print(e)
                        self.users_errors.append(user)

        for i in range(len(self.users_errors)*5):
            times = 0
            self.browser = driver_module.get_driver2()
            for country in self.countries:
                if len(self.users_errors):
                    if times == 5:
                        self.browser.close()
                        self.browser = driver_module.get_driver2()
                    times += 1
                    user = self.users_errors.pop()
                    self.current_user = user
                    url = self.create_url(user, country)
                    try:
                        self.browser.get(url)
                        time.sleep(3)
                        try:
                            self.get_education()
                            self.get_experience()
                            self.get_person()
                        except Exception as e:
                            # print(e)
                            self.users_errors.append(user)
                    except Exception as e:
                        # print(e)
                        self.users_errors.append(user)

    def save_person(self, person_json, user_url):
        person_json['user_url'] = user_url
        with codecs.open('./data/profile.csv', 'a+', 'utf8') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(
                [person_json[title] if title in person_json.keys() else None for title in self.person_titles])
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

    def get_person(self):

        person_section = self.browser.find_element(
            By.XPATH, self.selectors_dict['person_section'])

        person_dict = {}

        try:
            person_dict['person_about'] = self.browser.find_element(
                By.XPATH, self.selectors_dict['person_about']).text
        except Exception:
            pass

        try:
            person_dict['person_name'] = person_section.find_element(
                By.XPATH, self.selectors_dict['person_name']).text
        except Exception:
            pass
        try:
            person_dict['person_title'] = person_section.find_element(
                By.XPATH, self.selectors_dict['person_title']).text
        except Exception:
            pass
        try:
            person_dict['person_others'] = person_section.find_element(
                By.XPATH, self.selectors_dict['person_others']).text
        except Exception:
            pass

        person_dict['extraction_date'] = datetime.datetime.now().strftime(
            "%d/%m/%Y, %H:%M:%S")

        self.save_person(person_dict, self.current_user)

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

        if not os.path.exists('./data/experience.csv'):
            file = codecs.open('./data/experience.csv', 'a+', 'utf8')
            file.write(",".join(Bot.experience_titles) + "\n")
            file.close()

        if not os.path.exists('./data/education.csv'):
            file = codecs.open('./data/education.csv', 'a+', 'utf8')
            file.write(",".join(Bot.education_titles) + "\n")
            file.close()

        if not os.path.exists('./data/profile.csv'):
            file = codecs.open('./data/profile.csv', 'a+', 'utf8')
            file.write(",".join(Bot.person_titles) + "\n")
            file.close()
        else:
            with codecs.open('./data/profile.csv', "r", encoding="utf8") as file:
                reader = csv.reader(file, delimiter=",")
                first = True
                for row in reader:
                    if first:
                        loaded_users.add(row[0])
                    else:
                        first = False


def thread_function(index, users):
    bot = Bot(index, users)

    '''
    file_obj = codecs.open('results.txt', 'r')
    users = []
    for user in [user.replace("\n", "") for user in file_obj.readlines()]:
        if user not in loaded_users:
            users.append(user)
    '''


'''
users = start_files()
threads_n = NUMERO_DE_HILOS

users_threads_list = [[] for _ in range(threads_n)]
users_len = len(users)
i = 0
for user in users:
    users_threads_list[i].append(user)
    i += 1
    i %= threads_n

threads = list()


for index in range(threads_n):
    print("CREANDO HILO ", index)

    x = threading.Thread(target=thread_function, args=(
        index, users_threads_list[index]))
    threads.append(x)
    time.sleep(1)
    x.start()

for index, thread in enumerate(threads):
    print("ESPERANDO HILO ", index)
    thread.join()
    print("HILO ", index, " TERMINADO", index)
'''

bot = Bot()

bot.start_files()
bot.get_brands()
