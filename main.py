import sys
import xxhash 
from utils import get_file_list
from utils import get_checksum_from_reports
from utils import get_checksum_list_from_report
from utils import hash_process
from datetime import datetime
import pandas as pd

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
    #all_files = list(set(all_files))
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
    
    # Конвертировать all_filese в Panda Tables
    #  
    # Convert all_files to DataFrame
    df_all_files = pd.DataFrame(all_files, columns=['file_path', 'file_size', 'file_hash', 'file_hash_type','file_hash_date'])
    df_all_files.set_index('file_path', inplace=True)

    # напечатать количество строк в df_all_files
    print(f"Number of files in df_all_files: {df_all_files.shape[0]}")
    # удалить строки с дублирующимся file_path
    df_all_files = df_all_files[~df_all_files.index.duplicated(keep='first')]
    # напечатать количество строк в df_all_files
    print(f"Number of files in df_all_files: {df_all_files.shape[0]}")

    print(df_all_files.head())
    NotOnDisk = []
    # по всем строкам в report_all_files найти соответствующие строки в df_all_files
    for report_file in report_all_files:
        file_path = report_file[0]
        file_hash = report_file[2]
        file_hash_type = report_file[3]
        file_hash_date = report_file[4]
        if file_path in df_all_files.index:
            df_all_files.at[file_path, 'file_hash'] = file_hash
            df_all_files.at[file_path, 'file_hash_type'] = file_hash_type
            df_all_files.at[file_path, 'file_hash_date'] = file_hash_date
            #print(f'File {file_path} found in all_files.Hash updated {df_all_files.at[file_path,'file_hash']}.')
        else:
            print(f"File {file_path} not found in all_files.")
            NotOnDisk.append(file_path)

    # сохранить NotOnDisk в файл в текстовом виде
    try:
        os.remove('/Volumes/bastet2/guantanamera/check/NotOnDisk.txt')
    except FileNotFoundError:
        pass
    with open('/Volumes/bastet2/guantanamera/check/NotOnDisk.txt', 'w') as f:
        for item in NotOnDisk:
            f.write("%s\n" % item) 

    
    print(df_all_files.head())
    # напечатать число строк в df_all_files без file_hash
    print(f"Number of files in df_all_files without hash: {df_all_files[df_all_files['file_hash'].isnull()].shape[0]}")
    # напечатать  строки в df_all_files без file_hash
    print(df_all_files[df_all_files['file_hash'].isnull()])
    # создать список NoHash из file_path без file_hash
    NoHash = df_all_files[df_all_files['file_hash'].isnull()].index.tolist()
    # сохранить NooHash в файл в текстовом виде
    try:
        os.remove('/Volumes/bastet2/guantanamera/check/NoHash.txt')
    except FileNotFoundError:
        pass
    with open('/Volumes/bastet2/guantanamera/check/NoHash.txt', 'w') as f:
        for item in NoHash:
            f.write("%s\n" % item)
    # создать список files_to_hash из df_all_files строк. содержащих  file_hash
    # со структурой (file_path, file_size, file_hash, file_hash_type, file_hash_date)
    files_to_hash = df_all_files[~df_all_files['file_hash'].isnull()].reset_index().values.tolist()


                
    hash_process(files_to_hash)

    
    return True

    
    
    print(f"Report files: {report_files[:20]}")


if __name__ == "__main__":
    main()