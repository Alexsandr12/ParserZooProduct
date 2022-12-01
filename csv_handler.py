import csv
from pathlib import Path


class CsvHandler:
    """Класс для работы с csv файлами."""
    @staticmethod
    def create_file(data: list, path: Path):
        """Создает csv-файл.

        Args:
            data: данные для записи в файл
            path: директория файла, в который необходимо записать данные.
        """
        with open(path,  "w", newline="", encoding='utf-8') as file:
            columns = list(data[0].keys())
            writer = csv.DictWriter(file, fieldnames=columns, delimiter=";")
            writer.writeheader()

            writer.writerows(data)

    @staticmethod
    def read_file(path: Path) -> list:
        """Читает файл для дальнейшей работы с данными.

        Args:
            path: директория файла
        Return:
            list: данные из файла
        """
        data_file = []
        with open(path, "r", newline="", encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                data_file.append(dict(row))

        return data_file
