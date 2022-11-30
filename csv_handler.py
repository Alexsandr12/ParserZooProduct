import csv

from config import CATEGORY_FILE_PATH


class CategoryHandler:
    @staticmethod
    def create_file(category):
        with open(CATEGORY_FILE_PATH,  "w", newline="", encoding='utf-8') as file:
            columns = list(category[0].keys())
            writer = csv.DictWriter(file, fieldnames=columns, delimiter=";")
            writer.writeheader()

            writer.writerows(category)

    @staticmethod
    def read_file():
        data_file = []
        with open(CATEGORY_FILE_PATH, "r", newline="", encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=";")
            for category in reader:
                data_file.append(dict(category))

        return data_file
