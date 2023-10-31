import csv
import ftplib
import os

# FTP server details
FTP_HOST = "your.ftp.host"
FTP_USER = "yourusername"
FTP_PASS = "yourpassword"

# Directory to start listing the files
FTP_MOVIE_FOLDER = "/path/to/movie/folder"

# CSV file to save the list
CSV_FILENAME = "movies_list.csv"

# Maximum depth of subfolders to scan
MAX_DEPTH = 5

# Connect to the FTP server
ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
print(f"Connected to FTP server: {FTP_HOST}")

# Change to the starting directory
ftp.cwd(FTP_MOVIE_FOLDER)
print(f"Changed directory to {FTP_MOVIE_FOLDER}")

# This function will be called for each file in the directory and subdirectories
def add_to_csv(ftp_conn, path, csv_writer, depth):
    if depth > MAX_DEPTH:
        print(f"Reached maximum depth of {MAX_DEPTH} in directory: {path}")
        return

    items = ftp_conn.nlst(path)
    for item in items:
        # Create the full path
        full_path = os.path.join(path, item) if path != "/" else "/" + item
        try:
            # Try to change to directory to check if it's a directory or a file
            ftp_conn.cwd(full_path)
            # It's a directory, so recurse into it if depth is not exceeded
            print(f"Entering directory: {full_path}")
            add_to_csv(ftp_conn, full_path, csv_writer, depth + 1)
            # Go back up to the parent directory
            ftp_conn.cwd("..")
        except ftplib.error_perm as e:
            # It's a file, get its size and write to CSV
            try:
                size = ftp_conn.size(full_path)
                csv_writer.writerow([full_path, size])
                print(f"File added: {full_path} Size: {size} bytes")
            except ftplib.error_perm as e:
                # Unable to get the size for some reason, write without size
                csv_writer.writerow([full_path, 'unknown'])
                print(f"File added (size unknown): {full_path}")

# Open the CSV file to write
with open(CSV_FILENAME, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header
    csvwriter.writerow(["Filename", "Filesize (bytes)"])
    # Start the recursive function to add filenames and file sizes to CSV with initial depth 0
    add_to_csv(ftp, FTP_MOVIE_FOLDER, csvwriter, 0)

# Close the FTP connection
ftp.quit()
print(f"CSV file '{CSV_FILENAME}' has been created with the list of movie filenames and their file sizes.")
print("FTP connection closed.")
