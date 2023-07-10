from pathlib import Path
import os

with open(os.path.join(os.path.dirname(__file__), 'description_path_table.html'), 'r', encoding='utf-8') as file:
    path_description = file.read()


with open(os.path.join(os.path.dirname(__file__), 'description_path_file.html'), 'r', encoding='utf-8') as file:
    description_path_file = file.read()

with open(os.path.join(os.path.dirname(__file__), 'description_scanner.html'), 'r', encoding='utf-8') as file:
    description_scanner = file.read()
