import stat
import os
import paramiko
import csv
import logging

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# SSH server details
SSH_HOST = "username"
SSH_PORT = 22  # Default SSH Port
SSH_USER = "pass"
SSH_PASS = "pass"

# Directory to start listing the files
SSH_MOVIE_FOLDER = "/home/Videos"

# CSV file to save the list
CSV_FILENAME = "movies_list.csv"

# Maximum depth of subfolders to scan
MAX_DEPTH = 5

# Function to establish an SSH connection and return an SFTP client
def create_sftp_client(host, port, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)
    return ssh.open_sftp()

# Maximum depth of subfolders to scan
MAX_DEPTH = 5

def list_files_recursively(sftp, path, csv_writer, depth=0):
    if depth > MAX_DEPTH:
        print(f"Reached maximum depth of {MAX_DEPTH} in directory: {path}")
        return

    for entry in sftp.listdir_attr(path):
        mode = entry.st_mode
        if stat.S_ISDIR(mode):  # Correctly check if it's a directory
            print(f"Entering directory: {entry.filename}")
            # Ensure we use forward slashes for Unix-like path on the remote system
            new_path = f"{path}/{entry.filename}"
            list_files_recursively(sftp, new_path, csv_writer, depth + 1)
        else:
            # Convert size to gigabytes and keep more precision if it's less than 1 GB
            file_size_gb = entry.st_size / (1024**3)
            if file_size_gb < 1:
                # If the file is less than 1GB, show size in MB with 2 decimal places
                file_size = f"{round(entry.st_size / (1024**2), 2)} MB"
            else:
                # If the file is equal or larger than 1GB, show size in GB with 2 decimal places
                file_size = f"{round(file_size_gb, 2)} GB"

            # Construct full file path
            full_file_path = f"{path}/{entry.filename}"
            
            # Write the file information to the CSV
            csv_writer.writerow([full_file_path, entry.filename, file_size])
            print(f"File added: {full_file_path} Size: {file_size}")

# Create SFTP client
sftp = create_sftp_client(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
print(f"Connected to SSH server: {SSH_HOST}")

# Open the CSV file to write
with open(CSV_FILENAME, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header
    csvwriter.writerow(["Path", "Folder", "Filename"])
    # Start the recursive listing of files
    list_files_recursively(sftp, SSH_MOVIE_FOLDER, csvwriter)

# Close the SFTP connection
sftp.close()
print(f"CSV file '{CSV_FILENAME}' has been created with the list of files.")
print("SFTP connection closed.")
