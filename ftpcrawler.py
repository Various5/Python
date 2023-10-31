import csv
import ftplib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

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

# Maximum number of worker threads
MAX_WORKERS = 2

# Function to split path into its constituent parts
def split_path(path):
    parts = path.rstrip("/").split("/")
    filename = parts[-1] if parts[-1] else None
    foldername = parts[-2] if len(parts) > 1 else None
    path = "/".join(parts[:-1])
    return path, foldername, filename

# This function will be called for each file in the directory and subdirectories
def add_to_csv(ftp_conn, path, csv_writer, depth):
    if depth > MAX_DEPTH:
        print(f"Reached maximum depth of {MAX_DEPTH} in directory: {path}")
        return []

    results = []
    try:
        items = ftp_conn.nlst(path)
    except ftplib.error_perm as e:
        print(f"Access denied to directory: {path}, skipping...")
        return results

    for item in items:
        full_path = os.path.join(path, item) if path != "/" else "/" + item
        try:
            ftp_conn.cwd(full_path)
            print(f"Entering directory: {full_path}")
            results.append((full_path, depth + 1))
            ftp_conn.cwd("..")
        except ftplib.error_perm as e:
            file_path, folder_name, filename = split_path(full_path)
            csv_writer.writerow([file_path, folder_name, filename])
            print(f"File added: {full_path}")

    return results

# Main function to handle FTP connection and threading
def main():
    with ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS) as ftp, \
            open(CSV_FILENAME, 'w', newline='') as csvfile, \
            ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        print(f"Connected to FTP server: {FTP_HOST}")
        ftp.cwd(FTP_MOVIE_FOLDER)
        print(f"Changed directory to {FTP_MOVIE_FOLDER}")

        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Path", "Folder", "Filename"])

        futures = {executor.submit(add_to_csv, ftp, FTP_MOVIE_FOLDER, csvwriter, 0): FTP_MOVIE_FOLDER}
        while futures:
            for future in as_completed(futures):
                path = futures.pop(future)
                try:
                    results = future.result()
                    for new_path, new_depth in results:
                        if new_depth <= MAX_DEPTH:
                            new_future = executor.submit(add_to_csv, ftp, new_path, csvwriter, new_depth)
                            futures[new_future] = new_path
                except Exception as e:
                    print(f"Exception occurred while processing directory {path}: {e}")

        print(f"CSV file '{CSV_FILENAME}' has been created with the list of files.")
        print("FTP connection closed.")

if __name__ == "__main__":
    main()
