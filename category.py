from typing import List

from bs4 import BeautifulSoup, element

from request_to_site import sendreq
from config import CLASS_ANIMAL_CATEGORY, CLASS_SUBCATEGORY
from csv_handler import Category


class GetCategory:
    def main(self):
        categores = self._get_categories_data()
        self.forming_id_fields(categores)

        creater_file = Category()
        creater_file.create_file(categores)

    def _get_categories_data(self) -> List[dict]:
        zootovary = sendreq.send_request()
        soup = BeautifulSoup(zootovary, "lxml")
        tags_animal_categories = soup.find_all("li", attrs={"class": CLASS_ANIMAL_CATEGORY})

        categories = []
        for i, tag in enumerate(tags_animal_categories, 1):
            anim_category = {
                "name": tag.a.text,
                "id": [str(i), tag.a.get("href")[1:]],
                "parent_id": ""
            }
            subcategies = self._get_subcategory(anim_category, tag)
            categories += [anim_category]+subcategies

        return categories

    @staticmethod
    def _get_subcategory(anim_category: dict, animal_tag: element.Tag) -> List[dict]:
        subcalegies = []

        subcategies_tag = animal_tag.find("ul", attrs={"class": CLASS_SUBCATEGORY})
        for subcalegory in subcategies_tag.find_all("a"):
            subcalegies.append({
                "name": subcalegory.text,
                "id": [anim_category['id'][0], f'{subcalegory.get("href").split("/")[-2]}/'],
                "parent_id": anim_category["id"]
            })

        return subcalegies

    @staticmethod
    def forming_id_fields(categories: List[dict]) -> None:
        for category in categories:
            category["id"] = ":".join(category["id"])
            if category['parent_id']:
                category["parent_id"] = ":".join(category["parent_id"])


if __name__ == "__main__":
    get_category = GetCategory()
    get_category.main()
