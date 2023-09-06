import undetected_chromedriver as uc
from fp.fp import FreeProxy
from selenium import webdriver

HEADLESS = False
HEADLESS = True


def set_proxy(options):
    proxy_server_url = FreeProxy(timeout=1).get()
    options.add_argument(f"--proxy-server={proxy_server_url}")


def get_driver(proxy=False):
    options = uc.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless")
    if proxy:
        set_proxy(options)
    driver = uc.Chrome(options=options)
    return driver
