# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 16:58:30 2018
@author: bnsmith3

Search the Fairfax Country Library catalog for books and their availability.
"""

import requests
from bs4 import BeautifulSoup as bs
from regex import sub, findall

def get_session_info():
    """Get the new session information necessary to search the catalog."""
    r = requests.get('https://fcplcat.fairfaxcounty.gov/uhtbin/cgisirsi/0/0/0/49')
    r.raise_for_status()
    soup = bs(r.content, 'html.parser')
    return soup.find(attrs={"name": "searchform", 'method': 'post'})['action']

def clean_result(result):
    """Remove extraneous space from the given string."""
    return sub('\s+', ' ', result).strip()

def get_img_url(results):
    """Grab the image information from the given string and return a well-formed url."""
    url = 'https://secure.syndetics.com/index.aspx?isbn={}/SC.GIF&client=703-324-3100&type=xw12&upc=&oclc={}&'
    
    results = findall(r'\'([\d,]*)\'', results)
    results = [a.strip() for a in results if len(a.strip()) > 1]    
    isbn = results[0] if ',' not in results[0] else results[0].split(',')[0]    
    
    return url.format(isbn, results[-1])

def get_results(content):
    """Return a list of dictionaries with title, author, book status, and img urls as entries.
    
    Only results that aren't electronic nor large print are returned.
    """
    results = []
    soup = bs(content, 'html.parser')
    
    # figure out if this is an item page or a search result listing
    if soup.find('h3').text == 'Item Details':
        title = soup.find('dd', 'title').text.strip()
        author = soup.find('dd', 'author').text.strip()
        status = soup.find('dd', 'copy_info').text.strip()
        img = get_img_url(soup.find('ul', 'itemservices').find('script').contents[0])
        
        results.append({'title': title, 'author': author, 'status': status, 'url': img})
    else:        
        for img_info, other_info in zip(soup.find_all('ul', 'hit_list_row'), soup.find_all('li', 'hit_list_item_info')):
            try:
                img = get_img_url(img_info.find('script').contents[0])
                
                title = clean_result(other_info.find('dd', 'title').text)
        
                if ('[electronic resource]' not in title) and ('[Large print edition.]' not in title):
                    author = other_info.find('dd', 'author').text.strip()
                    status = clean_result(other_info.find('dd', 'holdings_statement').text)
        
                    results.append({'title': title, 'author': author, 'status': status, 'url': img})
            except AttributeError:
                # if it gets here, most likely no results were found
                break
    return results

def search_for_book(search, session=None, payload=None):
    """Return a dictionary with the search string and a list of the search results as entries.
    
    If the payload isn't specified, it is assumed that the search string provided is a title.
    """
    if not payload:
        payload = {'query_type': 'search', 'searchdata1': search, \
                  'srchfield1': 'TI^TITLE^SERIES^Title+Processing^Title', \
                  'library': 'ALL', 'sort_by': '-PBYR'}
    if not session:
        session = get_session_info()

    r = requests.post('https://fcplcat.fairfaxcounty.gov{}'.format(session), data=payload)
    r.raise_for_status()
    return {'search': search, 'results': get_results(r.content)}
        
