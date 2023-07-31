from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import time
import numpy as np
import re
import os
import datetime

class Scrapper:
    def __init__(self, website_url: str, fake_ua: bool=False, user_agent: str="", proxy_list: list=[], proxy_index: int=0, timeout: int=20, headless: bool=True) -> None:
        
        print("Setting up scrapper...\n")

        # create log file if not exists
        pattern = re.compile(r"^((.*\/\/)|)((www\.)|)(.*?)(\..*)$")
        website_name = pattern.match(website_url)
        if website_name is not None:
            website_name = website_name.group(5)

        self.log_file_name = f"./{website_name}_scrapper.log"
        if not os.path.exists(f"{self.log_file_name}"):
            with open(f"./{website_name}_scrapper.log", "w") as f:
                f.write("")
    
        # setup proxy
        self.proxy_list = proxy_list

        if proxy_list != []:
            print(f"Setting up proxies...")

            pattern = re.compile(r"^(\d{1,3}(\.|:)){4}\d{1,5}")
            for proxy in self.proxy_list:
                if not pattern.match(proxy):
                    print(f"Invalid proxy: {proxy}\n\n")
                    exit()

            try:
                self.current_proxy_index = proxy_index
                self.current_proxy = proxy_list[self.current_proxy_index]
                print(f"Proxies set up. Current proxy: {self.current_proxy}\n")
            except Exception as e:
                print(f"Error setting up proxies: {e}\n\n")
                
                with open(self.log_file_name, "a") as f:
                    f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error setting up proxies: {e}\n\n")

                exit()

        # setup user agent
        self.fake_ua = fake_ua
        if fake_ua:
            print("Setting up user agent...")
            try:
                self.user_agent_generator = UserAgent()
                self.user_agent = self.user_agent_generator.chrome
                print(f"User agent set up. Current user agent: {self.user_agent}\n")
            except Exception as e:
                print(f"Error setting up user agent: {e}\n\n")

                with open(self.log_file_name, "a") as f:
                    f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error setting up user agent: {e}\n\n")

                exit()

        else:
            if user_agent == "":
                print("No user agent provided. Using default.")
                
                options = Options()
                options.add_argument("--headless")
                options.add_argument('--log-level=3')
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                driver = webdriver.Chrome(options=options)

                ua = driver.execute_script('return navigator.userAgent').replace('Headless', '')
                r = r"(Chrome\/\d+\.\d+\.)(.+)( )"
                result = re.search(r, ua)

                if result is not None:
                    self.user_agent = ua.replace(result.group(2), "0.0")
                else:
                    print("Error while getting default user agent from browser.\n")

                    with open(self.log_file_name, "a") as f:
                        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error while getting default user agent from browser.\n")

                    exit()

                driver.close()

                print(f"User agent set up. Current user agent: {self.user_agent}\n")
            else:
                print(f"Setting up user agent...")
                try:
                    self.user_agent = user_agent
                    print(f"User agent set up. Current user agent: {self.user_agent}\n")
                except Exception as e:
                    print(f"Error setting up user agent: {e}\n\n")

                    with open(self.log_file_name, "a") as f:
                        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error setting up user agent: {e}\n\n")

                    exit()

        
        # setup selenium options
        print("Setting up selenium options...")
        try:
            self.chrome_options = Options()
            
            if headless:
                self.chrome_options.add_argument("--headless")
            
            self.chrome_options.add_argument(f"user-agent={self.user_agent}")

            self.chrome_options.add_argument("--disable-extensions")
            self.chrome_options.add_argument("--disable-gpu")
            self.chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            self.chrome_options.add_argument("--start-maximized")
            self.chrome_options.add_argument('--log-level=3')
            self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

            if proxy_list != []:
                self.chrome_options.add_argument(f"--proxy-server={self.current_proxy}")

            print("Selenium options set up.\n")
        except Exception as e:
            print(f"Error setting up selenium options: {e}\n\n")

            with open(self.log_file_name, "a") as f:
                f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error setting up selenium options: {e}\n\n")

            exit()

        # launch selenium driver
        print("Launching selenium driver...")
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            print("Selenium driver launched.\n")
        except Exception as e:
            print(f"Error launching selenium driver: {e}\n\n")

            with open(self.log_file_name, "a") as f:
                f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error launching selenium driver: {e}\n\n")

            exit()

        self.website_url = website_url
        self.timeout = timeout

        print("Scrapper set up.\n")


    def renew_identity(self, renew_proxy=True, renew_ua=True, new_ua=None) -> None:
        if renew_proxy and self.proxy_list != []:
            print(f"Renewing proxy {self.current_proxy}...")
            try:
                self.current_proxy_index += 1 % len(self.proxy_list)
                self.current_proxy = self.proxy_list[self.current_proxy_index]
                self.chrome_options.add_argument(f"--proxy-server={self.current_proxy}")
                print(f"Proxy renewed. Current proxy: {self.current_proxy}\n")
            except Exception as e:
                print(f"Error renewing proxy: {e}\n\n")

                with open(self.log_file_name, "a") as f:
                    f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error renewing proxy: {e}\n\n")

                exit()

        if renew_ua and (new_ua is not None or self.fake_ua):
            print(f"Renewing user agent {self.user_agent}...")
            try:
                self.user_agent = self.user_agent_generator.chrome if new_ua is None else new_ua
                self.chrome_options.add_argument(f"user-agent={self.user_agent}")
                print(f"User agent renewed. Current user agent: {self.user_agent}\n")
            except Exception as e:
                print(f"Error renewing user agent: {e}\n\n")

                with open(self.log_file_name, "a") as f:
                    f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error renewing user agent: {e}\n\n")

                exit()

        print("Restarting selenium driver...")
        try:
            self.driver.close()
            self.driver = webdriver.Chrome(options=self.chrome_options)
            print("Selenium driver restarted.\n")
        except Exception as e:
            print(f"Error restarting selenium driver: {e}\n\n")

            with open(self.log_file_name, "a") as f:
                f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error restarting selenium driver: {e}\n\n")

            exit()


    def random_wait(self, avg: float = 2, std: float = 0.5) -> None:
        # make sure the random number is positive and doesn't go above or below the average by more than 2 standard deviations
        random_time = -1
        while random_time < 0 or random_time > avg + 2 * std or random_time < avg - 2 * std:
            random_time = np.random.normal(avg, std)
        time.sleep(random_time)


    def close(self) -> None:
        print("Closing scrapper...")
        try:
            self.driver.close()
            print("Scrapper closed.\n")
        except Exception as e:
            print(f"Error closing scrapper: {e}\n\n")

            with open(self.log_file_name, "a") as f:
                f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error closing scrapper: {e}\n\n")

            exit()