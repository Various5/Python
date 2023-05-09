import requests
from bs4 import BeautifulSoup
import json

def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href.startswith('http'):# including both http and https links
            links.append(href)
    return links

def crawl_website(url):
    links = set()
    visited = set()
    links.add(url)
    while len(links) > 0:
        current_url = links.pop()
        if current_url in visited:
            continue
        print('Crawling:', current_url)
        current_links = get_links(current_url)
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
