import csv
from pathlib import Path

from config import CATEGORY_FILE_NAME, OUTPUT_DIRECTORY


class Category:
    FILEDIR = Path(__file__).parent / OUTPUT_DIRECTORY / CATEGORY_FILE_NAME
    Path.mkdir(FILEDIR.parent, exist_ok=True)

    def create_file(self, category):
        with open(self.FILEDIR,  "w", newline="", encoding='utf-8') as file:
            columns = list(category[0].keys())
            writer = csv.DictWriter(file, fieldnames=columns, delimiter=";")
            writer.writeheader()

            writer.writerows(category)

    def read_file(self):
        with open(self.FILEDIR, "r", newline="", encoding='utf-8') as file:
            return csv.DictReader(file, delimiter=";")
