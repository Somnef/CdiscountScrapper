from CdiscountScrapper import CdiscountScrapper
import sys
import os
import datetime
import time
import pandas as pd

if len(sys.argv) < 2:
    print("Usage: python cdiscount_scrapper.py <search_terms> <max_pages> (optional) <headless> (optional) <fake_user_agent> (optional) <proxy_list> (optional)")
    exit()


search_terms = sys.argv[1].split(",")
# strip whitespaces
search_terms = [search_term.strip() for search_term in search_terms]

try:
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else -1
except:
    print("Max pages must be an integer.")
    exit()

try:
    headless = sys.argv[3] if len(sys.argv) > 3 else "True"
    if headless != "True" and headless != "False":
        raise Exception()
    headless = True if headless == "True" else False
except:
    print("Headless must be a boolean.")
    exit()

try:
    fake_ua = sys.argv[4] if len(sys.argv) > 4 else "False"
    if fake_ua != "True" and fake_ua != "False":
        raise Exception()
    fake_ua = True if fake_ua == "True" else False
except:
    print("Fake user agent must be a boolean.")
    exit()

try:
    proxy_list = sys.argv[5].split(",") if len(sys.argv) > 5 else []
    # strip whitespaces
    proxy_list = [proxy.strip() for proxy in proxy_list]
except:
    print("Proxy list must be a list of proxies separated by commas.")
    exit()

cdiscount_scrapper = CdiscountScrapper(headless=headless, fake_ua=fake_ua, proxy_list=proxy_list)

for search_term in search_terms:
    tries = 0
    max_tries = 5

    products = pd.DataFrame([])

    while tries < max_tries and products.empty:
        products = cdiscount_scrapper.get_products(search_term, max_pages=max_pages)
        tries += 1

        if products.empty:
            print(f"\n\nError getting products (returned empty). Retrying... ({tries}/{max_tries})\n\n")
            time.sleep(3)

    found_products = not products.empty

    # remove rows that don't contain the search term in their name
    products = products[products["name"].str.contains(search_term, case=False)]

    if not products.empty:
        # save products' dataframe to file
        if os.path.exists(f"./cdiscount/{'_'.join(search_term.lower().strip().split())}") == False:
            os.makedirs(f"./cdiscount/{'_'.join(search_term.lower().strip().split())}")

        products.to_csv(
            f"./cdiscount/{'_'.join(search_term.lower().strip().split())}/{datetime.datetime.now().strftime('%Y-%m-%d__%H-%M-%S')}.csv", 
            index=False
        )

    else:
        if found_products:
            print("\n\nNo products with matching name found. Exiting...\n\n")
            # write to logs
            with open(cdiscount_scrapper.log_file_name, "a") as f:
                f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - No products with matching name found.")
        else:
            print(f"\n\nError getting products (returned empty). Exiting...\n\n")
            # write to logs
            with open(cdiscount_scrapper.log_file_name, "a") as f:
                f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error getting products (returned empty {max_tries} time(s)).")

        exit()


cdiscount_scrapper.close()