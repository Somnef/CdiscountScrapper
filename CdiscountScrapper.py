from Scrapper import Scrapper
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import datetime
import pandas as pd
import os

class CdiscountScrapper(Scrapper):
    def __init__(self, fake_ua: bool = False, user_agent: str = "", proxy_list: list = [], proxy_index: int = 0, timeout: int = 20, headless: bool=True) -> None:
        website_url = "https://www.cdiscount.com"
        super().__init__(website_url, fake_ua, user_agent, proxy_list, proxy_index, timeout, headless)

    def get_products(self, search_term: str, max_pages: int = -1) -> pd.DataFrame:
        print(f"Searching for products named \"{search_term}\" on {self.website_url} on a maximum of {max_pages} page(s)...\n")

        self.driver.get(self.website_url)
        try:
            search_box = WebDriverWait(self.driver, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "//input[@aria-label=\"Qu'est-ce qui vous ferez plaisir ?\"]")))
        except:
            print("Error finding search box.\n\n")

            with open(self.log_file_name, "a") as f:
                f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error finding search box.")

            exit()
        
        search_box.clear()
        search_box.send_keys(search_term)
        self.random_wait(2, 0.5)
        search_box.send_keys(Keys.ENTER)

        products = []

        next_page_exists = True

        i = 1
        while next_page_exists and (i <= max_pages or max_pages == -1):
            print(f'Scraping page {i}')

            product_cards = self.driver.find_elements(By.XPATH, "//ul[@id='lpBloc']/li")
            product_cards = [
                product_card
                for product_card in product_cards 
                if product_card.text != '' and product_card.text != 'PUBLICITÉ'
            ]

            extracted_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for product_card in product_cards:
                try:
                    name = product_card.find_element(By.XPATH, ".//a//h2").text
                except:
                    name = None

                try:
                    price = product_card.find_element(By.XPATH, ".//span[contains(@class, 'price') and contains(@class, 'priceColor') and contains(@class, 'hideFromPro')]").text
                    if price.endswith('€'):
                        price = price[:-1].split(",")
                    else:
                        price = price.split('€')
                    price = float(".".join(price))
                except:
                    price = None

                try:
                    rating = product_card.find_element(By.XPATH, ".//span[contains(@class, 'c-stars-result')]").get_attribute('data-score')
                    if rating is not None:
                        rating = float(rating) * 5 / 100
                except:
                    rating = None

                try:
                    description = product_card.find_element(By.XPATH, ".//div[contains(@class, 'prdtBILDesc') and not(contains(@class, 'prdtBILDescription'))]")

                    try:
                        description = description.find_element(By.XPATH, ".//ul")
                        description = description.find_elements(By.XPATH, ".//li")
                        description = {desc.text.split(' : ')[0]: desc.text.split(' : ')[1] for desc in description}
                    except:
                        description = description.text # type: ignore
                except:
                    description = None

                try:
                    link = product_cards[0].find_element(By.XPATH, ".//a").get_attribute('href')
                except:
                    link = None

                products.append(
                    {
                        'name': name,
                        'price': price,
                        'rating': rating,
                        'description': description,
                        'link': link,
                        'extracted_at': extracted_at,
                    }
                )

            try:
                self.random_wait(2, 0.5)
                next_page = self.driver.find_element(By.XPATH, "//input[@value='Page suivante']")
                next_page.click()
                self.random_wait(2, 0.5)
            except:
                next_page_exists = False
                print("No next page.\n\n")
                self.random_wait(2, 0.5)

            i += 1

        print("\nDone!\n")

        df = pd.DataFrame(products)
        return df