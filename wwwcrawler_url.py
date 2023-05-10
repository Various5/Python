import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
from collections import deque
import time

def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = set()
    for link in soup.find_all('a'):
        href = link.get('href')
        if href is not None:
            scheme = urlparse(href).scheme or urlparse(url).scheme
            href = urlparse(href)._replace(scheme=scheme).geturl()
            if scheme in ('http', 'https') and urlparse(href).netloc == urlparse(url).netloc:
                links.add(href)
    return links

def crawl_website(url, timeout, save_count):
    links = deque([url])
    visited = set()
    domain = urlparse(url).netloc
    while links:
        link = links.popleft()
        if len(visited) % save_count == 0 and len(visited) > 0:
            json_data = json.dumps(list(visited))
            with open('website_links.json', 'w') as f:
                f.write(json_data)
        if len(visited) % timeout == 0 and len(visited) > 0:
            time.sleep(2)
        if link in visited:
            continue
        try:
            current_links = get_links(link)
        except requests.exceptions.ConnectionError:
            print('Skipping:', link)
            continue
        visited.add(link)
        print(f'Visited: {len(visited)}', end='\r')
        for sub_link in current_links:
            if sub_link not in visited and sub_link not in links:
                links.append(sub_link)
    json_data = json.dumps(list(visited))
    with open('website_links.json', 'w') as f:
        f.write(json_data)
    return visited

if __name__ == '__main__':
    url = input('Enter a website URL: ')
    timeout = int(input('Enter the timeout (in seconds) between URLs: '))
    save_count = int(input('Enter the number of URLs after which the JSON data is saved: '))
    visited = crawl_website(url, timeout, save_count)
