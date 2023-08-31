from copy import deepcopy
import logging
import re
from threading import Thread, RLock


CATEGORY_EXTS = {
    "archives": ('zip', 'gz', 'tar', '7z', 'rar', 'arj', 'pkg', 'deb', 'rpm', 'z'),
    "audio": ('mp3', 'ogg', 'wav', 'wma', 'amr', 'aif', 'flac', 'cue'),
    "documents": ('doc', 'docx', 'odt', 'wpd', 'rtf', 'txt', 'tex', 'pdf', 'ods', 'xls', 'xlsx', 'xlsm', 'pptx', 'djv', 'djvu'),
    "images": ('jpeg', 'png', 'jpg', 'svg', 'bmp', 'tif', 'tiff', 'ai', 'gif', 'ico', 'ps', 'psd', 'webp'),
    "video": ('avi', 'mp4', 'mov', 'mkv', 'm4v', 'h264', 'h265', 'mp4', 'mpg', 'mpeg', 'rm', 'flv', 'swf', 'vob', 'webm', 'wmv'),
}



def check_path(path, defined_files, rlock):
    for key in defined_files:
        if path.suffix.removeprefix(".").casefold() in CATEGORY_EXTS[key]:
            rlock.acquire()
            defined_files[key].append(path)
            rlock.release()
            logging.debug(f'Done {path.name}')
            break


def define_data(path):
    defined_files = {}
    category_dirs = []
    for key in CATEGORY_EXTS:
        defined_files[key] = []
        category_dirs.append(path.joinpath(key))

    rlock = RLock()
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

    threads = []
    for i in path.glob("**/*"):
        if i.is_file() and i.parent not in category_dirs:
            thread = Thread(target=check_path, args=(i, defined_files, rlock))
            thread.start()
            threads.append(thread)
    [el.join() for el in threads]

    for key in CATEGORY_EXTS:
        if not defined_files[key]:
            defined_files.pop(key)

    return defined_files


def print_data(defined_files):
    for key in defined_files:
        if len(defined_files[key]) > 0:
            print(f"Files from '{key}' category:")
            for i in defined_files[key]:
                print(" " * 8 + f"{i.name}")
        else:
            continue
        print("\n")


def rm_empty_dirs(path):
    for i in path.iterdir():
        if i.is_dir():
            rm_empty_dirs(i)
            try:
                i.rmdir()
            except OSError:
                continue


def rename_duplicates(defined_files):
    if not defined_files:
        return defined_files
    
    updated_files = deepcopy(defined_files)
    for key in defined_files:
        processed_files = []
        for i, file in enumerate(defined_files[key]):
            if i not in processed_files:
                used_ids = []
                possible_id = {}
                number_of_duplicates = 1
                for j, updated_file in enumerate(updated_files[key]):
                    if i != j:
                        if file.name.casefold() == updated_file.name.casefold():
                            number_of_duplicates += 1
                            possible_id[j] = number_of_duplicates
                        if updated_file.stem.casefold().startswith(file.stem.casefold()):
                            suffix_string = updated_file.stem.casefold().replace(file.stem.casefold(), "")
                            if suffix_string.find(" ") == 0 and suffix_string.count(" ") == 1 and re.fullmatch(" \(\d+\)", suffix_string):
                                used_ids.append(int(suffix_string[2:-1]))
                if possible_id:
                    for j in possible_id:
                        id = possible_id[j]
                        while True:
                            if id not in used_ids:
                                updated_files[key].pop(j)
                                updated_files[key].insert(j, file.parent.joinpath(file.stem + " " + "(" + str(id) + ")" + file.suffix))
                                used_ids.append(id)
                                processed_files.append(j)
                                break
                            id += 1

    return updated_files


def replace(old_path, new_path):
    old_path.replace(new_path)
    logging.debug(f'Done {new_path.name}')


def sort_data(path, defined_files, updated_files):
    if not defined_files:
        return
    
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

    for key in defined_files:
        subpath = path.joinpath(key)
        if not subpath.is_dir():
            subpath.mkdir()
        threads = []
        for i, file in enumerate(defined_files[key]):
            thread = Thread(target=replace, args=(file, subpath.joinpath(updated_files[key][i].name)))
            thread.start()
            threads.append(thread)
        [el.join() for el in threads]
