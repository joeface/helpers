'''
Script for scrapping kremlin.ru website search
You may set search parameters inside params attribute (#17)

Requires: requests and bs4

Mikhail Ageev, 2019
michaelageev.com

'''

import requests
from bs4 import BeautifulSoup


def retrieve_list():
    # Retrieving Kremlin official announcements 
    response = requests.get('http://en.kremlin.ru/search', params={'query': 'interview'}, timeout=40)

    # Checking response status code
    if response.status_code == requests.codes.ok:
        # Output response content as a string
        parse_response(response.text)
    else:
        # Status code is not 200
        print 'Error occured'


def parse_response(html):

    # Initialize a bs4 instance with a HTML-source
    page_dom = BeautifulSoup(html, "html.parser")

    # Iterate over all DIVs with class hentry_event
    for line in page_dom.find_all('div', class_="hentry_event"):
        
        # Find first A inside the DIV and get innerText
        title = line.find('a').contents[0]
        
        # Get article URL
        href = 'http://kremlin.ru'+line.find('a')['href']
        
        # If the line has a TIME node — retrieve 'datetime' attribute
        date = line.find('time')['datetime'] if line.find('time') else 'no-date' 
        
        print date, title, href


retrieve_list()
