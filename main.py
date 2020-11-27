import requests
import sys
import json
from bs4 import BeautifulSoup
import config
import time
from config import SERVICE, COUNTRY, DELAY

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'
}
MAIN_URL = 'https://sms-activate.ru/ru'
API_URL = 'https://sms-activate.ru/api/api.php?act=getNumbersStatusAndMediumSmsTime'


def save_page(response_str, file_name='page.html'):
    with open(file_name, 'w', encoding='utf-8') as html_file:
        html_file.write(response_str)


def save_json(response_json, file_name='data.json'):
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(response_json, json_file, ensure_ascii=False, indent=4)


def load_json(file_name):
    with open(file_name, 'r', encoding='utf-8') as json_file:
        return json.loads(json_file.read())


def update_cities_file(response_str):
    soup = BeautifulSoup(response_str, 'lxml')
    countries_blocks = soup.select('a.countryChoose')
    countries = {}
    for country_block in countries_blocks:
        countries[country_block.text] = int(country_block['country'])
    save_json(countries, 'countries.json')


def update_services_file(response_str):
    soup = BeautifulSoup(response_str, 'lxml')
    services_blocks = soup.select('tr.tabbed.cell')
    services = {}
    for service_block in services_blocks:
        service_name = service_block.select_one('.serviceNameRadio').text.replace('&nbsp', '')
        service_key = service_block['service']
        services[service_name] = service_key
    save_json(services, 'services.json')


def get_quant():
    countries = load_json('countries.json')
    request_data = 'action=getNumbersStatusAndMediumSmsTime&api_key=&country={}&operator%5B%5D=any'
    try:
        request_data = request_data.format(countries[COUNTRY])
    except KeyError:
        print('{} страна не найдена'.format(COUNTRY))
        sys.exit()
    response = requests.post(API_URL, data=request_data, headers=HEADERS)
    response_json = response.json()
    services = load_json('services.json')
    try:
        quant = int(response_json[services[SERVICE]]['quant'])
    except KeyError:
        print('{} сервис не найден'.format(SERVICE))
        sys.exit()
    return quant


def scanner():
    quant = None
    while True:
        new_quant = get_quant()
        if quant is None:
            quant = new_quant
            print(quant)
        else:
            delta_quant = new_quant - quant
            print(delta_quant)
            quant = new_quant
        time.sleep(DELAY)


if __name__ == '__main__':
    scanner()
