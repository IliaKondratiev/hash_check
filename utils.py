import os
import re
from datetime import datetime



def get_file_list(path):
    try:
    # return os.listdir(path)
    # return table of all files in subfolders with filename, path to file, filesize in bytes
        file_list = []
        for root, dirs, files in os.walk(path):
            # Ignore hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    file_checksum = None
                    file_checksum_type = None
                    file_checksum_date = None
                    file_list.append((file, file_path, file_size, file_checksum, file_checksum_type, file_checksum_date))
        return file_list
    except FileNotFoundError:
        print(f"Directory {path} not found.")
        return []
    except NotADirectoryError:
        print(f"{path} is not a directory.")
        return []
    except PermissionError:
        print(f"Permission denied for directory {path}.")
        return []
    
def get_checksum_from_reports(report_file,all_files):
    report_path=os.path.dirname(report_file)
    replication_finish_date = None
    source_path = None
    file_read = None
    date_format = "%d.%m.%Y, %H:%M"
    # Define regex patterns
    finish_date_pattern = re.compile(r"Replication Finish Date:\s+(.+)")
    source_path_pattern = re.compile(r"Source path:\s+(.+)")
    size_pattern = re.compile(r"Size:\s+(.+)")
    checksum_type_pattern = re.compile(r"Checksum Type:\s+(.+)")
    checksum_pattern = re.compile(r"xxHash3-64:\s+([a-f0-9]+)")

    # Convert all tuples in all_files to lists
    all_files = [list(file) for file in all_files]



    try:
        with open(report_file, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if not replication_finish_date:
                match = finish_date_pattern.search(line)
                if match:
                    replication_finish_date = match.group(1)
                    replication_finish_time = datetime.strptime(replication_finish_date, date_format)
        
            match = None
            match = source_path_pattern.search(line)
            if match :
                source_path = match.group(1)
                print(f"Source path: {source_path}")

            match = None
            #search if line starts with source_path string 
            if source_path and line.startswith(source_path):
                # Cut off the last folder from source_path
                parent_path = os.path.dirname(source_path)
                
                # Extract part of the line after the parent path
                extracted_part = line.split(parent_path)[1].strip()
                
                # Combine the parent path of report_path with the extracted part
                file_read = os.path.join(os.path.dirname(report_path)) + extracted_part

            if line == 'Size: N/A':
                file_read = None
            
            if file_read:
                match = None
                match = checksum_pattern.search(line)
                if match:
                    file_checksum = match.group(1)
                    file_checksum_type = 'xxHash3-64'
                    file_checksum_date = replication_finish_time
                    #find in all_files list file with the same path and update checksum, checksum type and checksum date
                    for file in all_files:
                        if file[1] == file_read and (file[5] is None or file_checksum_date < file[5]):
                            file[3] = file_checksum
                            file[4] = file_checksum_type
                            file[5] = file_checksum_date
                            break
                    file_read = None



                
                

    except Exception as e:
        print(f"Error processing report: {e}")
            

    all_files = [tuple(file) for file in all_files]

    return all_files
    
            
#    except FileNotFoundError:
#        print(f"File {report_file} not found.")
#        return None
#    except PermissionError:
#        print(f"Permission denied for file {report_file}.")
#        return None