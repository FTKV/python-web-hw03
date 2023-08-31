from abc import ABC, abstractmethod
from rich.console import Console
from rich.table import Table


class OutputAbstract(ABC):
    @abstractmethod
    def output(self, *args):
        pass


class RecordConsoleOutput(OutputAbstract):
    def output(self, record):
        print(record)


class RecordTableOutput(OutputAbstract):
    def output(self, record):
        console = Console()
        console.print(record.table_repr())


class NotesConsoleOutput(OutputAbstract):
    def output(self, notes):
        sep = 50 * "-"
        print("\n" + sep + "\n" + (sep + "\n").join([f"ID: {id:08}\n{note}\n" for id, note in notes]) + sep)
    

class NotesTableOutput(OutputAbstract):
    def output(self, notes):
        for id, note in notes:
            table = note.table_repr()
            table.title = f"ID: {id:08}"
            console = Console()
            console.print(table)
            print("\n")