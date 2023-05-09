import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
import time

def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href is not None and (href.startswith('http') or href.startswith('https')):
            links.append(href)
    return links

def crawl_website(url, timeout, save_count):
    links = set()
    visited = set()
    links.add(url)
    domain = urlparse(url).netloc
    while len(links) > 0:
        links_copy = links.copy()
        for link in links_copy:
            if len(visited) % save_count == 0 and len(visited) > 0:
                json_data = json.dumps(list(visited))
                with open('website_links.json', 'w') as f:
                    f.write(json_data)
            if len(visited) % timeout == 0 and len(visited) > 0:
                time.sleep(2)
            if link in visited:
                continue
            if not link.startswith('http'):
                link = 'http://' + link
            if not link.startswith('https'):
                link = 'https://' + link
            if urlparse(link).netloc != domain:
                continue
            try:
                current_links = get_links(link)
            except requests.exceptions.ConnectionError:
                print('Skipping:', link)
                continue
            visited.add(link)
            print(f'Visited: {len(visited)}', end='\r')
            for sub_link in current_links:
                if sub_link not in visited:
                    links.add(sub_link)
            links.remove(link)
    json_data = json.dumps(list(visited))
    with open('website_links.json', 'w') as f:
        f.write(json_data)
    return visited

if __name__ == '__main__':
    url = input('Enter a website URL: ')
    timeout = int(input('Enter the timeout (in seconds) between URLs: '))
    save_count = int(input('Enter the number of URLs after which the JSON data is saved: '))
    visited = crawl_website(url, timeout, save_count)
