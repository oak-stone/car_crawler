#!/usr/bin/python3
""" Python 3.x webscraper for cars """

import time, sys, threading
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from mapping import make_to_number
import crawl_config

class loader:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_loader():
        while 1:
            for char in '|/-\\': yield char

    def __init__(self, delay=None):
        self.loader_generator = self.spinning_loader()
        if delay and float(delay): self.delay = delay

    def loader_task(self):
        while self.busy:
            sys.stdout.write(next(self.loader_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.loader_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False

def get_url_content(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as source:
            if response_200_ok(source):
                return source.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def response_200_ok(source):
    """
    Returns True if the response seems to be HTML, False otherwise
    """
    content_type = source.headers['Content-Type'].lower()
    return (source.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(e):
    print(e)

def get_listings(html, listings={}):
    #listings = {}
    makeAndModels = html.select('td.make_and_model')
    prices = html.select('td.price')
    getLink = html.select('td.make_and_model > a', href=True)
    for model, price, link in zip(makeAndModels, prices, getLink):
        """
        A bit of string formatting and using try if one or more fields are empty
        """
        try:
            model = model.contents[0].contents[0]
            price = ((str(price.contents[0])).replace(u'\xa0', '').strip() + '€')
            link = ('https://www.auto24.ee' + link.get('href'))
        except:
            continue
        """
        Append findings to listing dictionary
        """
        listings[model] = [price, link]        
    return listings

def print_listings(listings):
    #print(i,'\b:', model.contents[0].contents[0], '\n\t', price.contents[0], '\b€', '\n\thttps://www.auto24.ee' + link.get('href'))
    print("\b" + "\n".join("{}\t{}".format(k, v) for k, v in listings.items()))
        
def get_usable_make_code_for_search(make, year, gearBox, lookBackPeriod):
    """
    Input: 
        make = string argument from user using sys. arg. e.g python3 app.py Ducati
        year = year of the make/model e.g python3 app.py Ducati 2016
        period = period of lookback when the listing was added e.g python3 app.py Ducati 2016 7

    Returns: 
        make = the makes' code in str. format, e.g 359 for ducati for search use
        year = year in string
        period = lookback period in string
    """
    #make = []
    #make.append(str(make_to_number(make)))
    #print(make)
    make = str(make_to_number(make))
    year = str(year)
    gearBox = str(gearBox)
    lookBackPeriod = str(lookBackPeriod)
    return make, year, gearBox, lookBackPeriod

def print_listings_to_terminal():
    try:
        make, year, gearBox, lookBackPeriod = get_usable_make_code_for_search(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        url = 'https://www.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&aj=&b=' + make + '&f1=' + year + '&i=' + gearBox + '&ae=2&af=200&ad=' + lookBackPeriod + '&by=2&ag=0&ag=1&otsi=otsi'
        html = BeautifulSoup(get_url_content(url), 'html.parser')
        print_listings(get_listings(html))
    except Exception as e:
                print("Error ", e)

def return_listings_as_email_content():
    listings = {}
    try:
        for make in crawl_config.make:
            make = str(make)
            url = 'https://www.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&aj=&b=' + make + '&f1=' + crawl_config.year + '&g2=' + crawl_config.maxPrice + '&i=' + crawl_config.gearBox + '&ae=2&af=200&ad=' + crawl_config.lookBackPeriod + '&by=2&ag=0&ag=1&otsi=otsi'
            html = BeautifulSoup(get_url_content(url), 'html.parser')
            emailContent = get_listings(html, listings)

        if (bool(emailContent)):
            #print(str("\n".join("{}\t{}".format(k, v) for k, v in emailContent.items())))
            return emailContent
        else:
            print("No cars were found")
            return 

    except Exception as e:
                print("Error ", e)

def main():
    with loader():
        if len(sys.argv) > 1:
            print_listings_to_terminal()
        elif (crawl_config.crawl == True):
            return(return_listings_as_email_content()) 
        else:
            print('\bError occured. Crawl is set to False and thus, make sure the enter ALL attributes: python3 app.py <make> <year> <gearBox>  <lookBackPeriod>')
            print('Exiting program')

if __name__ == '__main__':
    main()
