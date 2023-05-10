import requests
import json
import csv
from concurrent.futures import ThreadPoolExecutor
from PIL import ImageFile
from io import BytesIO
import re

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
    try:
        img_data = requests.get(image, timeout=timeout, stream=True).content
        parser = ImageFile.Parser()
        parser.feed(img_data)
        img_size = len(img_data) / 1024.0
        with open('image_sizes.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if img_size >= 1024:
                img_size = img_size / 1024.0
                writer.writerow([image, '{:.2f} MB'.format(img_size)])
            else:
                writer.writerow([image, '{:.2f} KB'.format(img_size)])
        print("Processed image:", image, "| Size:", '{:.2f}'.format(img_size), "KB")
    except:
        print("Could not retrieve size for image: ", image)

# Iterate through each URL
for url in urls:
    try:
        print("Processing URL:", url)

        # Get page content
        response = requests.get(url, timeout=timeout)
        page_content = response.content

        # Get all images on page
        images = []
        img_formats = ["jpg", "jpeg", "png", "gif"]
        for fmt in img_formats:
            images.extend(re.findall(r'(?i)([^<>\"\']*?\.(?:%s))' % fmt, str(page_content)))

        # Process each image
        with ThreadPoolExecutor() as executor:
            executor.map(get_image_size, images)

    except requests.exceptions.Timeout:
        print("Request timed out for URL: ", url)
        continue

# Close CSV file
csvfile.close()
