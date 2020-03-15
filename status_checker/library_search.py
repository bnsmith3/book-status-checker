# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 16:58:30 2018
@author: bnsmith3

Search the Fairfax Country Library catalog for books and their availability.
"""

import requests
from bs4 import BeautifulSoup as bs
from regex import sub
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from time import sleep

def get_session_info():
    """Get the new session information necessary to search the catalog."""
    chrome_options = Options() 
    chrome_options.add_argument("--headless") 
    browser = webdriver.Chrome(executable_path='../../../../Downloads/chromedriver.exe',  options=chrome_options) 
    
    cookies = browser.get_cookies()
    session = requests.Session()
    session.headers.update({'Host': 'fcplcat.fairfaxcounty.gov'})
    
    for cookie in cookies:
        session.cookies[cookie['name']] = cookie['value']
        
    return session, browser

def end_session(browser):
    """End the session"""
    browser.quit()

def clean_result(result):
    """Remove extraneous space and trailing periods from the given string."""
    return sub('\.$', '', sub('\s+', ' ', result).strip())

def get_status(position, session):
    """Grab the availability information of the content at the given results position."""
    r1 = session.get('https://fcplcat.fairfaxcounty.gov/search/components/ajaxhoverbibsummary.aspx?pos={}'.format(position))
    r1.raise_for_status()
    hit = bs(r1.content, 'html.parser').find('span', 'nsm-short-item nsm-e')
    if hit:
        return hit.text.strip()
    else:
        return ''
    pass

def get_results(content, session):
    """Return a list of dictionaries with title, author, book status, and img urls as entries.
    
    Only results that aren't electronic nor large print are returned.
    """
    results = []
    soup = bs(content, 'html.parser')
    
    for index, info in enumerate(soup.find_all('div', 'c-title-detail__container')):
        try:               
            title = '{} (Year: {})'.format(clean_result(info.find('span', 'nsm-e135').text), \
                     clean_result(info.find('span', 'nsm-short-item nsm-e48').text))
    
            resource_types = set([a['title'] for a in info.find_all('img', 'c-title-detail-formats__img')])
            if len(set(['Ebook', 'DVD', 'Eaudiobook', 'RBdigital']).intersection(resource_types)) == 0:
                img = info.find('img', 'c-title-detail__thumbnail')['src']
                author = clean_result(info.find('span', 'nsm-e118').text)
                #status = '{} (Current holds: {})'.format(get_status(index+1, session), info.find('span', 'nsm-short-item nsm-e8').text)
                status = 'N/A'
                call_number = clean_result(info.find('span', 'nsm-short-item nsm-e16385').text)
    
                results.append({'title': title, 'author': author, 'status': status, \
                                'url': img, 'call_number': call_number})
        except AttributeError:
            # if it gets here, most likely no results were found
            break
    return results

def search_for_book(search_string, session=None, browser=None, payload=None):
    """Return a dictionary with the search string and a list of the search results as entries.
    
    If the payload isn't specified, it is assumed that the search string provided is a title.
    """
    session_was_none = True if (session is None) else False

    if not session:
        session, browser = get_session_info()

    if session is not None: # only attempt a search if we were able to get the session info
        browser.get('https://fcplcat.fairfaxcounty.gov/search/searchresults.aspx?ctx=1.1033.0.0.1&type=Keyword&term={}&by=TI&sort=RELEVANCE&limit=TOM=*&query=&page=0&searchid=1'.format(search_string))
        sleep(1)
        page_content = browser.page_source
        results = get_results(page_content, session)
        
        if session_was_none:
            end_session(browser)
            
        return {'search': search_string, 'results': results, 'page_content': page_content}
    else:
        print('Session not retrieved')
        return {'search': search_string, 'results': []}
        
