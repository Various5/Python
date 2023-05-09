import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse

def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href is not None and (href.startswith('http') or href.startswith('https')):
            links.append(href)
    return links

def crawl_website(url):
    links = set()
    visited = set()
    links.add(url)
    domain = urlparse(url).netloc
    while len(links) > 0:
        current_url = links.pop()
        if current_url in visited:
            continue
        if not current_url.startswith('http'):
            current_url = 'http://' + current_url
        if not current_url.startswith('https'):
            current_url = 'https://' + current_url
        if urlparse(current_url).netloc != domain:
            continue
        print('Crawling:', current_url)
        try:
            current_links = get_links(current_url)
        except requests.exceptions.ConnectionError:
            print('Skipping:', current_url)
            continue
        visited.add(current_url)
        for link in current_links:
            if link not in visited:
                links.add(link)
    return visited

if __name__ == '__main__':
    url = input('Enter a website URL: ')
    visited = crawl_website(url)
    json_data = json.dumps(list(visited))
    with open('website_links.json', 'w') as f:
        f.write(json_data)
