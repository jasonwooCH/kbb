import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib.parse as urlparse
import re
from urllib.parse import parse_qs
from bs4 import BeautifulSoup


# https://www.kbb.com/<make>/<model>/<year>/styles/?intent=buy-new
# ex. https://www.kbb.com/acura/rdx/2019/styles/?intent=buy-new
kbb_base_url = "https://www.kbb.com"
default_model_url = "https://www.kbb.com/{}/{}/{:d}/styles/?intent=buy-new"

def requests_retry_session(
    retries=3, 
    backoff_factor=0.3, 
    status_forcelist=(500, 502, 504),
    session=None
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def construct_default_url(make, model, year):
    return default_model_url.format(make, model, year)

def url_response(url):
    try:
        response = requests_retry_session().get(url, timeout=5)
        return response
    except Exception:
        print("URL Fetch for {} failed".format(url))
        sys.exit(1)

def scrape_style_url_from_model_url(response):
    soup = BeautifulSoup(response, "lxml")

    a_style_elems = soup.findAll('a', class_='big-button-one style-link')

    style_urls_for_model = []

    for a in a_style_elems:
        # https://www.kbb.com/acura/rdx/2019/base-style/options/?vehicleid=436300&intent=buy-new&modalview=false
        # https://www.kbb.com/acura/rdx/2019/base-style/?vehicleid=436300&intent=buy-new
        model_style_options_url = "{}{}".format(kbb_base_url, a['href'])
        model_style_url = model_style_options_url.replace("options/", "")

        style_urls_for_model.append(model_style_url)

    return style_urls_for_model

def extract_style_name_from_style_url(style_url):
    return style_url.split('/')[-2]


def fetch_style_urls_for_model(make, model, year):
    '''Fetch URLs for different Styles per model (ex. Base style, Technology pkg, etc.)
    Some models only have one Style available, which gets Redirected straight to the Style URL. 
    '''
    model_styles_url = construct_default_url(make, model, year)

    model_styles_res = url_response(model_styles_url)

    if model_styles_res.history:
        redirected_url = model_styles_res.url
        url_to_return = redirected_url.replace("options/", "")
        return [url_to_return]

    return scrape_style_url_from_model_url(model_styles_res.text)


def fetch_cto_values_for_vehicleid(vehicleid):
    ''' Returns a list of 3 values making up Cost to Own
            Out of Pocket Expenses
            Loss of Value
            5 Year Cost to Own (sum of above two)
    '''
    #https://www.kbb.com/vehicles/hub/_costtoown/?vehicleid=447236
    cto_url = "https://www.kbb.com/vehicles/hub/_costtoown/?vehicleid={}"
    #print(cto_url.format(vehicleid))
    cto_page = url_response(cto_url.format(vehicleid))

    soup = BeautifulSoup(cto_page.text, "lxml")

    cto_dict = {}

    cto_elems = soup.findAll('div', class_="cto-box")
    for elem in cto_elems:
        cto_name = elem.find('div', class_='title-four').text.strip()
        cto_value = elem.find('div', class_='title-two').text
        cto_dict[cto_name] = cto_value

    return cto_dict

def extract_vehicleid_from_style_url(style_url):
    parsed = urlparse.urlparse(style_url)
    return parse_qs(parsed.query)['vehicleid'][0]

def scrape_specs_for_vehicleid(vehicleid):
    #  https://www.kbb.com/vehicles/hub/_specifications/?vehicleid=436300
    specs_url = " https://www.kbb.com/vehicles/hub/_specifications/?vehicleid={}"

    specs_page = url_response(specs_url.format(vehicleid))
    soup = BeautifulSoup(specs_page.text, "lxml")
    basic_spec_elems = soup.findAll('div', class_="hub-specs-item")

    specs_dict = {}

    for spec_elem in basic_spec_elems:
        spec_name = spec_elem.find('div', class_="hub-specs-title").text
        spec_value = spec_elem.find('div', class_="paragraph-three").text
        specs_dict[spec_name] = spec_value

    detailed_spec_soup = BeautifulSoup(soup.script.string, "lxml")
    detailed_spec_elems = detailed_spec_soup.findAll('div', class_='table-row')

    for spec_elem in detailed_spec_elems:
        spec_name = spec_elem.div.find(text=True, recursive=False)
        spec_value = spec_elem.find('div', class_='table-column-resize').text
        specs_dict[spec_name] = spec_value
    
    return specs_dict

# print(scrape_specs_for_vehicleid("436300"))


'''
style_urls = fetch_style_urls_for_model("acura", "rdx", 2019)

for style_url in style_urls:
    print(extract_style_name_from_style_url(style_url))
'''

    


    