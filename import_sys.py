import sys
import os

# Отладочные сообщения
print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("Python path:", sys.path)

try:
    import xxhash
    print("xxhash imported successfully")
except ImportError as e:
    print("Error importing xxhash:", e)

from utils import get_file_list
from utils import get_checksum_from_reports
from utils import get_checksum_list_from_report
from utils import hash_process
from datetime import datetime

def get_arguments():
    try:
        return sys.argv[1:]
    except IndexError:
        print("No arguments provided.")
        sys.exit(1)

def main():
    # get arguments from command line
    paths = get_arguments()
    
    all_files = []
    for path in paths:
        file_list = get_file_list(path)
        all_files.extend(file_list)
    #print(f"All files: {all_files[:20]}")
    #    print(f"Files in {path}: {file_list[:20]}")
    
    #get number of files in all_files
    print(f"Number of files: {len(all_files)}")
    #get list of all txt files
    txt_files = [file for file in all_files if file[0].endswith('.txt')]
    print(f"Number of txt files: {len(txt_files)}")

    #get from all_files list of all .txt files, lying in folders with name ending with 'Reports'
    report_txt_files = [file for file in all_files if os.path.dirname(file[0]).endswith('Reports') & file[0].endswith('.txt')]
    print(f"Number of Report txt files: {len(report_txt_files)}")

    #for report in report_txt_files:
    #    all_checksum = get_checksum_from_reports(report[1],all_files)
    #    all_files = all_checksum

    report_all_files = []
    report_files=[]

    for report in report_txt_files:
        report_files = get_checksum_list_from_report(report[0])
        report_all_files.extend(report_files)

if __name__ == "__main__":
    main()