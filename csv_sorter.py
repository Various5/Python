import csv
import os

# Function to determine the type of movie based on the resolution in the filename
def determine_resolution_type(filename):
    if '4K' in filename:
        return '4K'
    elif '2K' in filename:
        return '2K'
    elif '1080' in filename:
        return '1080'
    elif '720' in filename:
        return '720'
    elif '420' in filename:
        return '420'
    elif 'SD' in filename:
        return 'SD'
    else:
        return 'rest'

# Open the original CSV file to read entries
with open('movies_list.csv', 'r', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    # Skip the header
    next(csvreader)

    # Prepare dictionaries to hold data for each type of movie
    sorted_data = {
        '4K': [],
        '2K': [],
        '1080': [],
        '720': [],
        '420': [],
        'SD': [],
        'rest': []
    }

    # Sort each row into the appropriate resolution category
    for row in csvreader:
        resolution_type = determine_resolution_type(row[2])  # Assuming the filename is in the 3rd column
        sorted_data[resolution_type].append(row)

# Function to write data to a CSV file
def write_to_csv(filename, data):
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Path", "Folder", "Filename"])  # Writing header
        csvwriter.writerows(data)

# Write sorted data to respective CSV files
for resolution_type, data in sorted_data.items():
    if data:  # If there is data for this resolution type, write to a file
        filename = f'{resolution_type}.csv'
        write_to_csv(filename, data)
        print(f"CSV file '{filename}' has been created.")
