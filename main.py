import sys
from utils import get_file_list
from utils import get_checksum_from_reports
from utils import get_checksum_list_from_report
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
    import os
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
    
   
    files_to_hash = []
    date_format = "%d.%m.%Y, %H:%M"

    for disk_file in all_files:
        file_found = 0
        file_path = disk_file[0]
        file_size = disk_file[1]
        file_hash_type = disk_file[3]
        file_hash = disk_file[2]
        file_hash_date = datetime.strptime("29.08.1974, 14:00", date_format)
        for report_file in report_all_files:
            if disk_file[0] == report_file[0]:
                file_found =+ 1
                if file_hash_date < report_file[4]:
                    file_hash_date = report_file[4]
                    file_hash = report_file[2]
                    file_hash_type = report_file[3]
        if file_found == 0:
            print(f"File {disk_file[0]} not found in reports.")
        else:
            files_to_hash.append((file_path, file_size, file_hash, file_hash_type, file_hash_date))


                
        
    
    return True

    
    
    print(f"Report files: {report_files[:20]}")


if __name__ == "__main__":
    main()