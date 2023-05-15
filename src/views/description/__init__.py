from pathlib import Path

with open(Path(__file__).resolve().parent.joinpath('description_path_table.html'), 'r', encoding='utf-8') as file:
    path_description = file.read()


with open(Path(__file__).resolve().parent.joinpath('description_path_file.html'), 'r', encoding='utf-8') as file:
    description_path_file = file.read()

with open(Path(__file__).resolve().parent.joinpath('description_scanner.html'), 'r', encoding='utf-8') as file:
    description_scanner = file.read()
