import requests
import sys
import json
from bs4 import BeautifulSoup
import time
from config import SERVICE, COUNTRY, DELAY
import bot
import bs4

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Content-Length': '78',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'sms-activate.ru',
    'Origin': 'https://sms-activate.ru',
    'Referer': 'https://sms-activate.ru/ru',
    'TE': 'Trailers',
}
MAIN_URL = 'https://sms-activate.ru/ru'
API_URL = 'https://sms-activate.ru/api/api.php?act=getNumbersStatusAndMediumSmsTime'


def save_page(response, file_name='page.xml'):
    with open(file_name, 'wb',) as html_file:
        html_file.write(response)


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
    try:
        request_data = 'action=getNumbersStatusAndMediumSmsTime&api_key=&country={}&operator%5B%5D=any'.format(countries[COUNTRY])
    except KeyError:
        print('{} страна не найдена'.format(COUNTRY))
        sys.exit()
    response = requests.post(API_URL, data=request_data, headers=HEADERS)
    save_page(response.content)
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
            message = 'Добавлено {} шт. ({}) в {}'.format(quant, COUNTRY, time.strftime("%H:%M"))
            bot.send_info(message)
        else:
            delta_quant = new_quant - quant
            if delta_quant:
                quant = new_quant
                message = 'Добавлено {} шт. ({}) в {}'.format(delta_quant, COUNTRY, time.strftime("%H:%M"))
                bot.send_info(message)
        time.sleep(DELAY)


if __name__ == '__main__':
    scanner()
