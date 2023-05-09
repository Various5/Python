import requests
import json
import csv
from PIL import Image
from io import BytesIO

# Set up CSV file
with open('image_sizes.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Image Name', 'Image Size'])

# Read in URLs from JSON file
with open('website_links.json') as json_file:
    urls = json.load(json_file)

# Iterate through each URL
for url in urls:
    # Get page content
    response = requests.get(url)
    page_content = response.content

    # Get all images on page
    images = []
    img_formats = ["jpg", "jpeg", "png", "gif"]
    for fmt in img_formats:
        images.extend(re.findall(r'(?i)([^<>\"\']*?\.(?:%s))' % fmt, str(page_content)))

    # Get size of each image
    for image in images:
        try:
            img_data = requests.get(image).content
            img = Image.open(BytesIO(img_data))
            img_size = len(img_data) / 1024.0

            # Write to CSV file
            with open('image_sizes.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if img_size >= 1024:
                    img_size = img_size / 1024.0
                    writer.writerow([image, '{:.2f} MB'.format(img_size)])
                else:
                    writer.writerow([image, '{:.2f} KB'.format(img_size)])

        except:
            print("Could not retrieve size for image: ", image)
