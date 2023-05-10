import requests 
import json
import csv
from concurrent.futures import ThreadPoolExecutor
from PIL import ImageFile
from io import BytesIO
import re
import time

# Set up CSV file
with open('image_sizes.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Image Name', 'Image Size'])

# Read in URLs from JSON file
with open('urls.json') as json_file:
    urls = json.load(json_file)

# Set request timeout limit to 10 seconds
timeout = 10

# Define a function to get the size of an image
def get_image_size(image):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        img_data = requests.get(image, headers=headers, timeout=timeout, stream=True).content
        parser = ImageFile.Parser()
        parser.feed(img_data)
        img_size = len(img_data) / 1024.0
        img_name = re.search(r'/([^/]+\.(jpg|jpeg|png|gif))$', image, re.I).group(1)
        if img_name in processed_images:
            print("Skipping image with duplicate name:", img_name)
            return
        with open('image_sizes.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if img_size >= 1024:
                img_size = img_size / 1024.0
                writer.writerow([img_name, '{:.2f} MB'.format(img_size)])
            else:
                writer.writerow([img_name, '{:.2f} KB'.format(img_size)])
        processed_images.add(img_name)
        print("Processed image:", img_name, "| Size:", '{:.2f}'.format(img_size), "KB")
    except:
        print("Could not retrieve size for image: ", image)

# Iterate through each URL
for url in urls:
    try:
        print("Processing URL:", url)

        # Get page content
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=timeout)
        page_content = response.content

        # Get all images on page
        images = []
        img_formats = ["jpg", "jpeg", "png", "gif"]
        for fmt in img_formats:
            images.extend(re.findall(r'(?i)([^<>\"\']*?\.(?:%s))' % fmt, str(page_content)))

        # Process each image
        processed_images = set()
        for image in images:
            get_image_size(image)
            time.sleep(1) # Add a delay between requests

    except requests.exceptions.RequestException:
        print("Request failed for URL: ", url)
        continue

# Close CSV file
csvfile.close()
