from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
import requests

INITIAL_ENDPOINT = "/search?min_price=0&max_price=3000&bedrooms=1,2,3,4&bathrooms=0&features=Cats+Allowed,Laundry+In+Unit,Dishwasher&search_title=Manhattan&areas=ino,1rgo,3qyb,3l4k,3qye,3qyf,3qyh,3qyi,3qyo,3qyx,3qyy,3r13,3r1e,3r20,3r38,3r3u,3r52,1rgd,3qyd,3qyj,3qyn,3qyr,5fro,3qyt,5frp,3qzx,5frn,3r0s,2jog,3r2b,1rg2,3qyq,3qyc,3qyg,3qys,3r45,3r4g,3r4r,2koa,2f3b,3r1p&page=1&sort=hopscore"


def build_soup(endpoint):
    url = f"https://www.renthop.com/{endpoint}"
    response = requests.get(url)
    apartment_web_page = response.text
    soup = BeautifulSoup(apartment_web_page, "html.parser")
    return soup


def build_address_list(soup):
    address_classes = soup.find_all(class_="search-info-title")
    address_list = [" ".join(c.getText().replace("\n", " ").strip().split()) for c in address_classes]
    return address_list


def build_price_list(soup):
    price_divs = soup.select(selector=".search-info div .align-middle")
    price_list = [div.getText().strip() for div in price_divs]
    return price_list


def build_bed_list(soup):
    divs = soup.select(selector=".search-info .align-bottom")
    bedroom_list = [div.getText().strip() for div in divs if "Bed" in div.getText().strip()]
    return bedroom_list


def build_bath_list(soup):
    divs = soup.select(selector=".search-info .align-bottom")
    bathroom_list =[div.getText().strip() for div in divs if "Bath" in div.getText().strip()]
    return bathroom_list


def build_link_list(soup):
    link_anchors = soup.select(selector=".search-info-title a")
    link_list = [anchor.get("href") for anchor in link_anchors]
    return link_list


def send_info(address_list, price_list, bedroom_list, bathroom_list, link_list):
    sheet_endpoint = 'https://api.sheety.co/7a6327fc6ea294ff861d1c31744358c7/nyRentHopSearch/rentHop'
    today_date = datetime.now().strftime("%m/%d/%Y")
    for index in range(len(address_list)):
        sheet_inputs = {
            "renthop": {
                "date": today_date,
                "address": address_list[index],
                "price": price_list[index],
                "bed": bedroom_list[index],
                "bath": bathroom_list[index],
                "link": link_list[index],
            }
        }

        sheet_response = requests.post(sheet_endpoint, json=sheet_inputs)
        print(sheet_response.text)

def next_page(soup):
    next_page_tag = soup.select_one(selector=".next-page")
    if next_page_tag is None:
        return False
    else:
        return True

def get_next_soup(current_page):
    next_page_tag = current_page.select_one(selector=".next-page")
    next_page = next_page_tag.get("href")
    return next_page


soup = build_soup(INITIAL_ENDPOINT)
run_program = True
while run_program:
    address_list = build_address_list(soup)
    price_list = build_price_list(soup)
    bed_list = build_bed_list(soup)
    bath_list = build_bath_list(soup)
    link_list = build_link_list(soup)
    send_info(address_list, price_list, bed_list, bath_list, link_list)
    if next_page(soup):
        new_endpoint = get_next_soup(soup)
        soup = build_soup(new_endpoint)
    else:
        print("No more apartments.")
        run_program = False
