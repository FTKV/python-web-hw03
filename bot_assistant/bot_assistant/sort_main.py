import pathlib
from .sort_functions import define_data, print_data, rm_empty_dirs, rename_duplicates, create_folders, change_paths, replace_files


TEXT_COLOR = {
    "red": "\033[31m",
    "green": "\033[32m",
    "reset": "\033[0m"
}


def sort_main_func(inp_path):
    path = pathlib.Path(inp_path)

    if not path.is_dir():
        print(TEXT_COLOR["red"] + "The argument is path to file or folder doesn't exist" + TEXT_COLOR["reset"])
        return
    
    defined_files = define_data(path)
    updated_files = rename_duplicates(defined_files)
    updated_files = change_paths(path, updated_files)
    print_data(updated_files)
    create_folders(path, defined_files)
    replace_files(defined_files, updated_files)
    rm_empty_dirs(path)
