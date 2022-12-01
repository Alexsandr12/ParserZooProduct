from typing import List

from bs4 import BeautifulSoup, element

from request_to_site import sendreq
from config import CLASS_ANIMAL_CATEGORY, CLASS_SUBCATEGORY, CATEGORY_FILE_PATH
from csv_handler import CsvHandler


class CategoryParser:
    """Класс формирования данных для файла катерогий товаров."""
    def get_categories(self):
        """"""
        categories = self._parse_categories()
        self.forming_id_fields(categories)

        file_maker = CsvHandler()
        file_maker.create_file(categories, CATEGORY_FILE_PATH)

    def _parse_categories(self) -> List[dict]:
        """Парсит данные главных категорий товаров и собрает все в один список.

        Return:
            List[dict]: спискок с данными категорий товаров
        """
        zootovary = sendreq.send_request()
        soup = BeautifulSoup(zootovary, "lxml")
        tags_animal_categories = soup.find_all("li", attrs={"class": CLASS_ANIMAL_CATEGORY})

        categories = []
        for i, tag in enumerate(tags_animal_categories, 1):
            anim_category = {
                "name": tag.a.text,
                "id": [str(i), tag.a.get("href")],
                "parent_id": ""
            }
            subcategories = self._parse_subcategory(anim_category, tag)
            categories += [anim_category]+subcategories

        return categories

    @staticmethod
    def _parse_subcategory(anim_category: dict, animal_tag: element.Tag) -> List[dict]:
        """Парсит данные подкатегорий для одной основной катерогии товаров.

        Args:
            anim_category: данные основной категории товаров.
            animal_tag: тег основной категории с данными подкатегорий товаров.
        Return:
            List[dict]: данные подкатегорий товаров.
        """
        subcategories = []

        subcategories_tag = animal_tag.find("ul", attrs={"class": CLASS_SUBCATEGORY})
        for i, subcategory in enumerate(subcategories_tag.find_all("a"), 1):
            subcategories.append({
                "name": subcategory.text,
                "id": [f"{anim_category['id'][0]}.{i}", f'{subcategory.get("href").split("/")[-2]}/'],
                "parent_id": anim_category["id"]
            })

        return subcategories

    @staticmethod
    def forming_id_fields(categories: List[dict]):
        """Формирует поля id категорий в строку.

        Args:
            categories: данные категорий товаров
        """
        for category in categories:
            category["id"] = ":".join(category["id"])
            if category['parent_id']:
                category["parent_id"] = ":".join(category["parent_id"])


if __name__ == "__main__":
    get_category = CategoryParser()
    get_category.get_categories()
