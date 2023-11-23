import requests as reqs
from bs4 import BeautifulSoup
import uuid
import json
import os
import random
from tqdm import tqdm
import multiprocessing
import time

def get_tor_session():
    session = reqs.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


root = 'https://www.mopo.de/page/{}/?s'

session = get_tor_session()
requests = get_tor_session()

def extract_meta_tags_from_url(url):
    parts = url.split('/')
    return parts[-2].replace('-', ' '), parts[-3], parts[-3]

def extract_news_urls_from_root(root_page_soup):
    links = root_page_soup.find_all(class_ = 'main-preview__img-link')
    return [x['href'] for x in links if hasattr(x, 'href')]

def page_url_scrap(page_url):
    
    title, topic, edition = extract_meta_tags_from_url(page_url)
    page_soup = get_soup(page_url)
    
    # Get all titles (h1, h2, etc.)
    titles = [x.text for x in 
                        page_soup.find_all(
        
                                ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']

                                 )
                ]

    # Get all paragraphs (p)
    paragraphs = [x.text for x in 
                    page_soup.find_all('p')
            ]
    
    if 'Bot Protection Firewall Blocked because of Malicious Activities' in ' '.join(paragraphs):
        time.sleep(5 * 60) # 5 minutes chilling
        return {'exit_code': False, 'data': None}
    return {'exit_code': True, 'data': (title, topic, edition, titles, paragraphs),}

    

def extract_text_and_save(page_url, output_folder):
    

    exit_code = False
    while not exit_code:
        output = page_url_scrap(page_url)
        exit_code, (title, topic, edition, titles, paragraphs) = output['exit_code'], output['data']
    
    json_dictionary = {
        'url': page_url,
        'topic': topic,
        'edition': edition,
        'url_title': title,
        'titles': titles,
        'paragraphs': paragraphs,
        'uuid4': str(uuid.uuid4())
    }
    
    base_folder = os.path.join(
            output_folder, edition, topic
        )
    os.makedirs(base_folder, exist_ok=True)
    json.dump(json_dictionary, open(
        os.path.join(base_folder, json_dictionary['uuid4'] + '.json'), 'w'
    ))
    
    

def get_soup(url):
    text = requests.get(url=url).text
    return BeautifulSoup(text, features='lxml')

def process_url(url):
    try:
        extract_text_and_save(url, './infinite_patience_tor_scrapped_data/')
    except:
        pass

def process_random_index(idx):
    valid_urls = [
        url for url in extract_news_urls_from_root(
            get_soup(root.format(idx))
        ) if url not in visited_urls
    ]

    # Using multiprocessing Pool with 8 processes
    pool = multiprocessing.Pool(processes=16)
    for _ in tqdm(pool.imap_unordered(process_url, valid_urls), total=len(valid_urls)):
        pass
    pool.close()
    pool.join()

    visited_urls.extend(valid_urls)

random_indexes = list(range(1, 3101)) # Empirical max depth
random.shuffle(random_indexes)
visited_urls = []

# Assuming you have the random_indexes list defined somewhere
for idx in random_indexes:
    process_random_index(idx)