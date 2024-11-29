import os
import re
from datetime import datetime
import xxhash



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
                    file_list.append((file_path, file_size, file_checksum, file_checksum_type, file_checksum_date))
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
    
def get_checksum_list_from_report(report_file):

    report_path=os.path.dirname(report_file)
    replication_finish_date = None
    source_path = []
    report_file_list = []
    file_block_start = []
    file_block_end = []
    file_read = None
    date_format = "%d.%m.%Y, %H:%M"
    # Define regex patterns
    finish_date_pattern = re.compile(r"Replication Finish Date:\s+(.+)")
    source_path_pattern = re.compile(r"Source path:\s+(.+)")
    size_pattern = re.compile(r"Size:\s+(.+)")
    checksum_type_pattern = re.compile(r"Checksum Type:\s+(.+)")
    checksum_pattern = re.compile(r"xxHash3-64:\s+([a-f0-9]+)")
    def split_line(line):
        parts = line.split(': ', 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        else:
            return parts[0], ''
    status_pattern = re.compile(r"Status: Offloaded")
    try:
        with open(report_file, 'r') as f:
            lines = f.readlines()
        linenum = 0
        for line in lines:
            
            if not replication_finish_date:
                match = finish_date_pattern.search(line)
                if match:
                    replication_finish_date = match.group(1)
                    replication_finish_time = datetime.strptime(replication_finish_date, date_format)
        
            match = None
            match = source_path_pattern.search(line)
            if match :
                # добавляем в список source_path найденный путь и номер строки в файле репорта
                source_path.append([match.group(1), linenum])
                
            #    print(f"Source path: {source_path}")

            
            # Ищем начало и конец блока описания файла в репорте и добавляем в список file_block_start и file_block_end
            # Блок начинается за строчку до size_pattern и заканчивается строкой после status_pattern
            # строки, начинающиеся с табуляции игнорируются 
            if line.startswith("Size:"):
                file_block_start.append([linenum-1, source_path[-1][0]])
            if line.startswith("Status: Offloaded"):
                file_block_end.append(linenum+1)
            linenum += 1

            match = None


        #В каждом блоке описания файла ищем путь к файлу и его контрольную сумму и тип контрольной суммы
        for i in range(len(file_block_start)):
            if lines[file_block_start[i][0]+1].startswith("Size: Zero KB") or lines[file_block_start[i][0]+1].startswith("Size: N/A"):
                continue
            # если в первой строке блока файл без расширения - пропускаем его
            if not re.match(r'.*\.[a-zA-Z0-9]{3,6}$', lines[file_block_start[i][0]].strip()):
                continue
            # из первой строки блока описания файла выделяем путь к файлу и заменяем в нем source_path, подходящий по номеру строки на report_path без последней папки

            source_path_trimmed = os.path.dirname(file_block_start[i][1])
            file_read = lines[file_block_start[i][0]].split(source_path_trimmed)[1].strip()
            file_read = os.path.dirname(report_path)+file_read
            #file_read = os.path.join(report_path.split("_Reports")[0], file_read)
            # print(f"File: {file_read}")


            # проверяем наличие на диске file_read
            #if os.path.exists(file_read):
            #    print(f"File {file_read} exists.")
            #else:
            #    print(f"File {file_read} not found.")
            
        # ищем контрольную сумму в последней строке блока описания файла
        #   if checksum_pattern.search(lines[file_block_end[i]]):
            file_checksum = lines[file_block_end[i]].split(': ')[1].strip()
            file_heshtype = lines[file_block_end[i]].split(': ')[0].strip()
            #конвертируем размер файла в байтах в число, не забываем про запятую в числе    
            #file_size = file_size.replace(',', '.')
            file_size = lines[file_block_start[i][0]+1].split(': ')[1].strip()
            file_size = file_size.replace(',', '.')  # заменяем запятую на точку
            
            if file_size.endswith('KB'):
                file_size1 = int(float(file_size.split(' ')[0]) * 1024)
            elif file_size.endswith('MB'):
                file_size1 = int(float(file_size.split(' ')[0]) * 1000 * 1000)
            elif file_size.endswith('GB'):
                file_size1 = int(float(file_size.split(' ')[0]) * 1000 * 1000 * 1000)
            else:
                file_size1 = int(float(file_size.split(' ')[0]))
        #   print(f"Checksum: {file_checksum}")

            report_file_list.append((file_read, file_size1, file_checksum, file_heshtype, replication_finish_time))
        
        return report_file_list


            
        
  
    except FileNotFoundError:
        print(f"File {report_file} not found.")
        return None
    except PermissionError:
        print(f"Permission denied for file {report_file}.")
        return None
    
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

            next_line_index = lines.index(line) + 1
            if next_line_index < len(lines) and lines[next_line_index].strip() == 'Size: N/A':
                file_read = None
            
            if file_read:
                match = None
                match = checksum_pattern.search(line)
                if match:
                    file_checksum = match.group(1)
                    file_checksum_type = 'xxHash3-64'
                    file_checksum_date = replication_finish_time
                    found_in_all_files = False
                    #find in all_files list file with the same path and update checksum, checksum type and checksum date
                    for file in all_files:
                        if file[1] == file_read and (file[5] is None or file_checksum_date < file[5]):
                            file[3] = file_checksum
                            file[4] = file_checksum_type
                            file[5] = file_checksum_date
                            found_in_all_files = True
                            break
                    if found_in_all_files == False:
                        print(f"File {file_read} not found in all_files list.")
                    file_read = None



                
                

    except Exception as e:
        print(f"Error processing report: {e}")
            

    all_files = [tuple(file) for file in all_files]

    return all_files


def hash_process(files_to_hash):
    for disk_file in files_to_hash:
        
        hash = hash_file(disk_file[0], disk_file[3])
      

        print(f"File: {disk_file[0]},",hash)
    return True


# создаем функцию для вычисления контрольной суммы файла

def hash_file(file_path, hash_type):
    try:
        with open(file_path, 'rb') as f:
            # if hash_type == 'xxHash3-64':
            hash = xxhash.xxh3_64()
            while True:
                data = f.read(1000000)
                if not data:
                    break
                hash.update(data)
            return hash.hexdigest()
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None
    except PermissionError:
        print(f"Permission denied for file {file_path}.")
        return None
    except Exception as e:
        print(f"Error hashing file {file_path}: {e}")
        return None


#    except FileNotFoundError:
#        print(f"File {report_file} not found.")
#        return None
#    except PermissionError:
#        print(f"Permission denied for file {report_file}.")
#        return None