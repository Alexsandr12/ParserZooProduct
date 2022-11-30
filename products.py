import sys

from request_to_site import sendreq
from csv_handler import CategoryHandler
from config import CATEGORIES


class ProductsParser:
    def __init__(self, getlinks):
        self.category_link = getlinks.get_categories_link()

    def get_products(self):
        for link in self.category_link:



class CategoriesLinks:
    def get_categories_link(self) -> list:
        categories_dict = self._get_categories_dict()

        if not CATEGORIES:
            return self._get_all_links(list(categories_dict.values()))
        else:
            return self._get_requested_categories_links(categories_dict)

    def _get_all_links(self, categories_dict: list) -> list:
        links = []

        all_subcategories = filter(
                lambda x: x['parent_id'] != "", categories_dict
            )

        for subcat in all_subcategories:
            links.append(self._forming_link(subcat))

        return [link.split(":")[-1] for link in links]

    def _get_requested_categories_links(self, categories_dict: dict) -> list:
        req_categ_id = self._validate_categories_id(categories_dict, CATEGORIES.split(","))
        if not req_categ_id:
            print("Нет валидных id категорий для получения списка товаров.")
            sys.exit()

        links = []
        for categ_id in req_categ_id:
            category_data = categories_dict[categ_id]
            links += self._get_links_for_id(category_data, categories_dict)

        return [link.split(":")[-1] for link in sorted(list(set(links)))]

    def _get_links_for_id(self, category_data: dict, categories_dict: dict):
        links_for_id = []

        if not category_data['parent_id']:
            subcategories_data = filter(
                lambda x: x["parent_id"] == category_data["id"],
                list(categories_dict.values())
            )

            for subcat in subcategories_data:
                links_for_id.append(self._forming_link(subcat))

        else:
            links_for_id.append(self._forming_link(category_data))

        return links_for_id

    @staticmethod
    def _forming_link(category_data):
        return f"{category_data['parent_id']}" \
               f"{category_data['id'].split(':')[1]}"

    @staticmethod
    def _get_categories_dict():
        categories_dict = {}
        for category in CategoryHandler.read_file():
            categories_dict[category["id"]] = category

        return categories_dict

    @staticmethod
    def _validate_categories_id(category_dict: dict, requested_categories: list) -> list:
        valid_categories_id = []
        all_categories_id = list(category_dict.keys())

        for categ_id in requested_categories:
            if categ_id.strip() in all_categories_id:
                valid_categories_id.append(categ_id.strip())
            else:
                print(f"Invalid category: {categ_id}")

        return valid_categories_id


if __name__ == "__main__":
    getlinks = CategoriesLinks()
    get_product = ProductsParser(getlinks)
    get_product.get_products()
