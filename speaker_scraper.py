import re
import sys
import time
import urllib.robotparser
from urllib.parse import urljoin, urlparse, quote
 
import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = "https://loudspeakerdatabase.com"

brands = ["Peerless"]
pause = 5

langs = {"fr", "ru", "cn", "de", "es", "it", "pt", "ja", "pl"}



session = requests.Session()
session.headers.update({
    "User-Agent": "VisualClusterProject-Scraper/0.1 https://github.com/BolaxaTheAlmighty"
})

## Testing Robot txt

robots = urllib.robotparser.RobotFileParser()
r = session.get(BASE + "/robots.txt", timeout = 20)
print("Robots Status: ", r.status_code)

robots.parse(r.text.splitlines())

def permission(url):
    try:
        return robots.can_fetch(session.headers["User-Agent"], url)
    except Exception:
        return True

url_test = BASE + "/search/brand=accuton"
print(permission(url_test))

## Obtain html
def obtain_html(url, num_try = 3):
    
    if not permission(url):
        return None
    
    for i in range(num_try):
        try:
            r = session.get(url, timeout = 20)
            if r.status_code == 200:
                time.sleep(pause)
                return r.text
        
            if r.status_code == 429:
                time.sleep(30 * (i+1))
                continue
        
            print(f"HHTP {r.status_code} in {url}")
            return None
        except requests.RequestException as e:
            print(f"Network error")
            time.sleep(5)
    return None



def print_start_end(html):
    start = ',206,206,206,206,206,206,206,206]}</script>'
    end = '<div class="next_page">'
    #end = 'loading="lazy"'

    start_block = html.split(start)
    
    #print(start_block[0])
    end_block = start_block[1].split(end)

    print(end_block[0])
    return(end_block[0])

#print_start_end(obtain_html(url_test))


def string_to_save(start, end, text):

    first_split = text.split(start)
    #print("\n\n",first_split[0])
    try:
        second_split = first_split[1].split(end)
    except Exception:
        print("\n\n",first_split[0])

    return second_split[0]

def save_parameters(text, page):

    driver_data = []
    
    #clean text solely for easier readability
    text = text.replace("&quot;", "")

    split_block = '<article class="woofer_card ribbon-container"'
    

    individual_driver = text.split(split_block)
    individual_driver = individual_driver[1:]
    #print(individual_driver[0])

    for driver in individual_driver:

        Re = string_to_save('re:', ',bl', driver)
        bl = string_to_save('bl:', ',mmd', driver)
        mmd = string_to_save('mmd:', ',rms', driver)
        rms = string_to_save('rms:', ',cms', driver)
        cms = string_to_save('cms:', ',sd', driver)
        sd = string_to_save('sd:', ',le', driver)
        le = string_to_save('le:', ',fs', driver)
        fs = string_to_save('fs:', ',qts', driver)
        if 'xmax:' in driver:
            qts = string_to_save('qts:', ',xmax', driver)
            xmax = string_to_save('xmax:', ',pmax', driver)
        else:
            qts = string_to_save('qts:', ',pmax', driver)
            xmax = None  

        if 'frmin:' in driver and 'frmax:' in driver:
            pmax = string_to_save('pmax:', ',frmin', driver)
            frmin = string_to_save('frmin:', ',frmax', driver)
            frmax = string_to_save('frmax:', ',spl1w', driver)
        else:
            pmax = string_to_save('pmax:', ',spl1w', driver)
            frmin = None
            frmax = None
        spl1w = string_to_save('spl1w:', ',z:', driver)
        z_raw = driver.split('z:')
        if '}"><a' in z_raw[1]:
            z = string_to_save('z:', '}"><a', driver) #}"><a href=
        elif '}"><div class=' in z_raw[1]:
            z = string_to_save('z:', '}"><div class=', driver)
        else:
            z = None
        
        ty = string_to_save('data-highlight="type">', '</span></td>', driver)

        if 'Discontinued' in driver:
            status = "Discontinued"
        elif 'Vintage' in driver:
            status = "Vintage"
        else:
            status = "Ongoing"

        brand_model = string_to_save('href="/', '" class="photos_and_graphs"', driver).split("/")
        brand = brand_model[0]
        model = brand_model[1]

        data = {
            "Brand": brand,
            "Model": model,
            "Re": Re,
            "Bl": bl,
            "Mmd": mmd,
            "Rms": rms,
            "Cms": cms,
            "Sd": sd,
            "Le": le,
            "Fs": fs,
            "Qts": qts,
            "Xmax": xmax,
            "Pmax": pmax,
            "frmin": frmin,
            "frmax": frmax,
            "spl1w": spl1w,
            "z": z,
            "Type": ty,
            "Status": status,
            "Page": page
        }

        driver_data.append(data)
        print(data)
    
    return driver_data
    

def scrollable_action():
    all_drivers = []
    page = 0

    h=["Brand","Model","Re","Bl","Mmd","Rms","Cms","Sd","Le","Fs","Qts","Xmax","Pmax","frmin","frmax","spl1w","z","Type", "Status", "Page"]

    try:
        df = pd.read_csv("driver_data.csv")
        page = max(df["Page"]) + 1
    
    except Exception:
        pd.DataFrame(columns=h).to_csv("driver_data.csv", index = False, encoding="utf-8")

    while True:
        html = obtain_html(f"{BASE}/next_page_api/offset={page*40}")
        if not html:
            break

        batch = save_parameters(html, page)

        if not batch:
            break
        
        if len(batch) > 40:
            break
        
        df = pd.DataFrame(batch).drop_duplicates(subset=["Brand", "Model"])
        df.to_csv(f"driver_data.csv", mode = "a", index = False, columns=h, header = False, encoding="utf-8")
        #all_drivers.extend(batch)

        print(f"Page {page}: {len(batch)} items")
        page += 1
    
    return df

scrollable_action()

data = pd.read_csv("driver_data.csv")
len(data)
