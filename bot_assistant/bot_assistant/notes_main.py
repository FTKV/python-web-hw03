import os
import pathlib
from platformdirs import user_data_dir
from rich import print as rprint
from .notes_classes import Tag, Note, Notes, IdError
from .output_classes import NotesConsoleOutput, NotesTableOutput


TEXT_COLOR = {
    "red": "\033[31m",
    "green": "\033[32m",
    "reset": "\033[0m"
}


notes = Notes()
output_handler = NotesTableOutput()


def input_error(func):
    def inner(user_input):

        try:
            result_func = func(user_input)
            return result_func
        except IdError:
            return TEXT_COLOR['red'] + "\nNote with such id does not exist!\n" + TEXT_COLOR["reset"]

    return inner


def show_commands_note(user_input):
    all_commands = ["add_note", "edit_note", "remove_note", "remove_all_notes", "show_notes", "search_note", "search_by_tags",
                    "add_tags_to_note", "remove_tags_in_note", "remove_all_tags_in_note", "mark_done", "unmark_done", "change_output_method", "exit",
                    "close"]
    if user_input.strip().lower() == "commands":
        for com in all_commands:
            rprint("-"+"'"+com+"'")
        return ''
    else:
        return TEXT_COLOR['red'] + "\nThis function does not exist. Try again!\n" + TEXT_COLOR["reset"]


def add_note(user_input):
    try:
        user_split_by_title = user_input.split("title:")
        user_split_by_body = user_split_by_title[1].split("body:")
        user_split_by_tags = user_split_by_body[1].split("tags:")
    except IndexError:
        return TEXT_COLOR['red'] + "\nTo add a note you need to write 'title: ... body: ... tags: ...' Tags as desired.\n" + TEXT_COLOR["reset"]

    note_title = user_split_by_body[0].strip()
    note_body = user_split_by_tags[0].strip()
    note_tags_list = []

    if len(user_split_by_tags) > 1:
        note_tags = user_split_by_tags[1].strip()
        note_tags_list = note_tags.split(", ")

    if note_title and note_body:
        note = Note(note_title, note_body)
    else:
        return TEXT_COLOR['red'] + "\nYou need to write something in 'title: ... body: ...'\n" + TEXT_COLOR["reset"]

    if note_tags_list:
        for note_tag in note_tags_list:
            note.add_tags(Tag(note_tag))

    notes.add_note(note)

    result_note = "-"*20 + "\n" + TEXT_COLOR['green'] + "The note was succesfully added!\n" + TEXT_COLOR["reset"]

    return result_note


@input_error
def edit_note(user_input):
    try:
        user_split_by_id = user_input.split("id:")
        user_split_by_title = user_split_by_id[1].split("title:")
        user_split_by_body = user_split_by_title[1].split("body:")
    except IndexError:
        return TEXT_COLOR['red'] + "\nTo edit a note you need to write 'id: ... title: ... body: ...'\n" + TEXT_COLOR["reset"]

    note_id = user_split_by_title[0].strip()
    note_title = user_split_by_body[0].strip()
    note_body = user_split_by_body[1].strip()

    if note_id and note_title and note_body:
        try:
            note_id = int(note_id)
        except ValueError:
            return TEXT_COLOR['red'] + "\nid must be a number\n" + TEXT_COLOR["reset"]

        notes.edit_note(note_id, note_title, note_body)
        return TEXT_COLOR['green'] + f"\nNote with id: {note_id} was succesfully changed!\n" + TEXT_COLOR["reset"]
    else:
        return TEXT_COLOR['red'] + "\nYou need to write something in 'id: ... title: ... body: ...'\n" + TEXT_COLOR["reset"]


@input_error
def remove_note(user_input):
    try:
        list_user_input = user_input.split("id:")
        note_id = list_user_input[1].strip()
    except IndexError:
        return TEXT_COLOR['red'] + "\nTo remove a note you need to write 'id: ...'\n" + TEXT_COLOR["reset"]

    try:
        note_id = int(note_id)
    except ValueError:
        return TEXT_COLOR['red'] + "\nid must be a number\n" + TEXT_COLOR["reset"]

    notes.remove_note(note_id)

    return TEXT_COLOR['green'] + f"\nNote with id: {note_id} was succesfully removed!\n" + TEXT_COLOR["reset"]


def remove_all_notes(user_input):
    if user_input.lower() != "remove_all_notes":
        return TEXT_COLOR['red'] + "\nThis function does not exist. Try again!\n" + TEXT_COLOR["reset"]

    for note_id in notes.data.keys():
        notes.remove_note(int(note_id))
        return remove_all_notes(user_input)

    return TEXT_COLOR['green'] + "\nAll notes have been deleted!\n" + TEXT_COLOR["reset"]


def show_notes(user_input):
    user_input_list = user_input.split()
    if len(user_input_list) == 1:
        result_notes = []
        for id, note in notes.show_notes():
            result_notes.append((id, note))
        if result_notes:
            return output(result_notes)
        else:
            return TEXT_COLOR['red'] + "\nYour notes list is empty!\n" + TEXT_COLOR["reset"]
    else:
        return TEXT_COLOR['red'] + "\nThis function does not exist. Try again!\n" + TEXT_COLOR["reset"]


def search_note(user_input):
    user_input = user_input.removeprefix("search_note")
    user_input = user_input.strip()

    if not user_input:
        return TEXT_COLOR['red'] + "\nYou have to write some content to find a note!\n" + TEXT_COLOR["reset"]

    result_notes = []
    for id, note in notes.show_notes(user_input):
        result_notes.append((id, note))

    if result_notes:
        return "\n" + "\n--------------------\n".join([f"ID: {id:08}\n{note}\n" for id, note in result_notes])
    else:
        return TEXT_COLOR['red'] + "\nYou don't have any notes with this content!\n" + TEXT_COLOR["reset"]


def search_by_tags(user_input):
    user_input = user_input.removeprefix("search_by_tags")
    user_input = user_input.strip()
    if not user_input:
        return TEXT_COLOR['red'] + "\nWrite some tags to find a note!\n" + TEXT_COLOR["reset"]
    user_input = user_input.split(", ")
    result_notes = notes.search_and_sort_by_tags(user_input)

    if result_notes:
        return "\n" + "\n--------------------\n".join([f"ID: {id:08}\n{note}\n" for id, note in result_notes])
    else:
        return TEXT_COLOR['red'] + "\nNo notes were found by your tags!\n" + TEXT_COLOR["reset"]


@input_error
def add_tags_to_note(user_input):
    try:
        user_split_by_id = user_input.split("id:")
        user_split_by_tags = user_split_by_id[1].split("tags:")
        note_tags = user_split_by_tags[1].strip()
        note_tags = note_tags.split(", ")
    except IndexError:
        return TEXT_COLOR['red'] + "\nTo add tags you need to write 'id: ... tags: ...'\n" + TEXT_COLOR["reset"]

    try:
        note_id = int(user_split_by_tags[0].strip())
    except ValueError:
        return TEXT_COLOR['red'] + "\nid must be a number!\n" + TEXT_COLOR["reset"]

    note = notes.data.get(note_id)

    if not note:
        raise IdError

    if note_tags != [""]:
        for tag in note_tags:
            if note.add_tags(Tag(tag)) == True:
                result = TEXT_COLOR['green'] + "\nTags were succesfully added!\n" + TEXT_COLOR["reset"]
            else:
                result = TEXT_COLOR['red'] + "\nThis tags already exist!'\n" + TEXT_COLOR["reset"]   
        return result

    else:
        return TEXT_COLOR['red'] + "\nTo add tags you need to write 'id: ... tags: ...'\n" + TEXT_COLOR["reset"]


@input_error
def remove_tags_in_note(user_input):

    try:
        user_split_by_id = user_input.split("id:")
        user_split_by_tags = user_split_by_id[1].split("tags:")

        try:
            note_id = int(user_split_by_tags[0].strip())
        except ValueError:
            return TEXT_COLOR['red'] + "\nid must be a number!\n" + TEXT_COLOR["reset"]

        note = notes.data.get(note_id)

        if not note:
            raise IdError

        if user_split_by_id[0].strip() == "remove_all_tags_in_note":
            try:
                int(user_split_by_id[1])
                note.remove_all_tags()
                return TEXT_COLOR['green'] + "\nTags were succesfully removed!\n" + TEXT_COLOR["reset"]
            except ValueError:
                return TEXT_COLOR['red'] + "\nThis function does not exist. Try again!\n" + TEXT_COLOR["reset"]

        note_tags = user_split_by_tags[1].strip()
        note_tags = note_tags.split(", ")

    except IndexError:
        return TEXT_COLOR['red'] + "\nTo remove tags you need to write 'id: ... tags: ...'.\nTo remove all tags you need to write 'id: ...'\n" + TEXT_COLOR["reset"]

    for tag in note_tags:
        note.remove_tags(tag.lower())

    return TEXT_COLOR['green'] + "\nTags were succesfully removed!\n" + TEXT_COLOR["reset"]


def mark_done(user_input):
    try:
        list_user_input = user_input.split("id:")
        note_id = list_user_input[1].strip()
    except IndexError:
        return TEXT_COLOR['red'] + "\nTo mark done a note you need to write 'id: ...'\n" + TEXT_COLOR["reset"]

    try:
        note_id = int(note_id)
    except ValueError:
        return TEXT_COLOR['red'] + "\nid must be a number\n" + TEXT_COLOR["reset"]

    try:
        if list_user_input[0].strip() == "mark_done":
            notes.data.get(note_id).mark_done()
            return TEXT_COLOR['green'] + "\nNote was marked done!\n" + TEXT_COLOR["reset"]
        else:
            notes.data.get(note_id).unmark_done()
            return TEXT_COLOR['green'] + "\nNote was unmarked done!\n" + TEXT_COLOR["reset"]
    except AttributeError:
        return TEXT_COLOR['red'] + "\nThere is no such note!\n" + TEXT_COLOR["reset"]
    

def change_output_method(user_input):
    global output_handler
    user_input = user_input.removeprefix("change_output_method")
    user_input = user_input.strip()
    if user_input not in ["console", "table"]:
        return TEXT_COLOR['red'] + "\nTo change the output method you need to write 'change_output_method ['console', 'table']'\n" + TEXT_COLOR["reset"]
    else:
        if user_input == "console":
            output_handler = NotesConsoleOutput()
        elif user_input == "table":
            output_handler = NotesTableOutput()
        return TEXT_COLOR['green'] + "\nThe output method was changed!\n" + TEXT_COLOR["reset"]


operations_notes = {
    "commands": show_commands_note,
    "add_note": add_note,
    "edit_note": edit_note,
    "remove_note": remove_note,
    "remove_all_notes": remove_all_notes,
    "show_notes": show_notes,
    "search_note": search_note,
    "search_by_tags": search_by_tags,
    "add_tags_to_note": add_tags_to_note,
    "remove_tags_in_note": remove_tags_in_note,
    "remove_all_tags_in_note": remove_tags_in_note,
    "mark_done": mark_done,
    "unmark_done": mark_done,
    "change_output_method": change_output_method,
}


def get_handler(handler):
    try:
        return operations_notes[handler]
    except:
        return TEXT_COLOR['red'] + "\nThis function does not exist. Try again!\n" + TEXT_COLOR["reset"] + "\n" + \
            "To see all functions of notebook, please write " + \
            TEXT_COLOR['green'] + "'commands'" + \
            TEXT_COLOR["reset"] + "\n"


def get_file_path(file_name):
    path = pathlib.Path(user_data_dir("Personal assistant"))
    if os.name == "nt":
        path = path.parent
    if not path.is_dir():
        path.mkdir()
    file_path = path.joinpath(file_name)
    return file_path


def output(result_notes):
    global output_handler
    return output_handler.output(result_notes)


def notes_main_func():
    global notes
    file_path = get_file_path("notes.bin")
    notes.load_from_file(file_path)
    rprint("\nInput 'commands' to see all the commands avalible!\n")

    while True:

        notes.save_to_file(file_path)
        user_input = input(">>> ")

        if user_input.lower() in ['close', 'exit']:
            print("\nGood Bye!\n")
            break

        if user_input:
            list_user_input = user_input.split()
            list_user_input[0] = list_user_input[0].lower()

            result_handler = get_handler(list_user_input[0])

            if type(result_handler) == str:
                print(result_handler)
            else:
                result = result_handler(user_input)
                if result:
                    print(result)