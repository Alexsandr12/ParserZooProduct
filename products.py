import time
from datetime import datetime
from typing import Union

from bs4 import BeautifulSoup, element

from myexceptions import NotValidCategory
from request_to_site import sendreq
from csv_handler import CsvHandler
from config import (CATEGORIES,
                    CATEGORY_FILE_PATH,
                    PRODUCTS_FILE_PATH,
                    URL,
                    PC,
                    CLASS_NAVIGATOR,
                    CLASS_PRODUCTS_LINK,
                    CLASS_PRODUCTS_LIST,
                    CLASS_PRODUCT_DATA,
                    CLASS_SKU_CATEGORY,
                    CLASS_SKU_NAME,
                    CLASS_SKU_COUNTRY,
                    CLASS_SKU_IMAGES,
                    CLASS_NOT_PRODUCT, RESTART)
from utils import delete_duplicate_product
from logger import log


class Products:
    """Получение данных товаров."""
    def __init__(self):
        self.category_link = self._get_links()
        self.products = []

    @staticmethod
    def _get_links() -> list:
        """Получает список ссылок на запрошенные категории товаров.

        Return:
            list: список ссылок
        """
        getlinks = CategoriesLinks()
        return getlinks.get_categories_link()

    def get_products(self):
        """Запускает получение данных товаров по запрошенным категориям
        и отправляет их на запись в файл."""

        for link in self.category_link:
            log.info(f"Паксинг товаров по категории {link}.")
            page = sendreq.send_request(f"{link}", params={'pc': PC}).text
            page_data = BeautifulSoup(page, "lxml")
            pagination = self._parse_pagination(page_data)
            self._get_products_for_category(pagination, page_data, link)
            self.products = delete_duplicate_product(self.products)

        log.info("Данные отправлены на запись в файл.")
        file_maker = CsvHandler()
        file_maker.create_file(self.products, PRODUCTS_FILE_PATH)
        log.info("Файл с товарами создан.")

    @staticmethod
    def _parse_pagination(page_data: element.Tag) -> Union[str, None]:
        """Парсит значение количества страниц.

        Args:
            page_data: тег страницы товаров по категории
        Return:
            Union[str, None]: значение количества страниц, либо None, если страница только одна
        """
        navigation = page_data.find("div", attrs={"class": CLASS_NAVIGATOR})
        if navigation:
            return navigation.find_all('a')[-1].get("href").split("PAGEN_1=")[1]
        else:
            return

    def _get_products_for_category(self, pagination: str, page_data: element.Tag, link: str):
        """Запускает сбор данных со всех страниц по одной категории товаров

        Args:
            pagination: значение количества страниц
            page_data: тег страницы товаров по категории
            link: ссылка на товары по категории
        """
        log.info(f"Парсинг товаров на странице 1.")
        self._get_products_from_page(page_data)

        if pagination:
            for page_i in range(2, int(pagination) + 1):
                log.info(f"Парсинг товаров на странице {page_i}.")
                page = sendreq.send_request(f"{link}", params={'pc': PC, "PAGEN_1": page_i}).text
                page_data = BeautifulSoup(page, "lxml")
                self._get_products_from_page(page_data)

    def _get_products_from_page(self, page_data: element.Tag):
        """Запускает сбор данных товаров с одной страницы по категории товаров.

        Args:
            page_data: тег страницы товаров по категории
        """
        products_content_info = page_data.find_all("div", attrs={"class": CLASS_PRODUCTS_LINK})
        for prod_content in products_content_info:
            product_link = prod_content.a.get("href")
            log.info(f"Парсинг товара по ссылке {product_link}.")

            prod_page = sendreq.send_request(product_link).text
            prod_page_data = BeautifulSoup(prod_page, "lxml")
            parser = ProductsParser(prod_page_data, product_link)
            self.products += parser.parse_product_data()


class ProductsParser:
    """Парсит данные со страницы товара

    Args:
        page_data: данные со страницы товара
        product_link: ссылка на страницу товара
    """
    def __init__(self, page_data: element.Tag, product_link: str):
        self.page_data = page_data
        self.parser_method = {
            "Артикул:": self._parse_sku_article,
            "Штрихкод:": self._parse_sku_barcode,
            "Фасовка:": self._parse_packing,
            "Цена:": self._parse_price
        }
        self.sku_link = URL + product_link
        self.sku_name = self._parse_sku_name()
        self.sku_category = self._parse_sku_category()
        self.sku_images = URL + self._parse_sku_images()
        self.products = []

    def parse_product_data(self) -> list:
        """Запускает парсинг данных товаров на странице товара.

        Return:
            list: список с данными товаров
        """
        active_data = self.page_data.find('div', attrs={"class": CLASS_PRODUCTS_LIST})
        sku_country = self._parse_sku_country(active_data)

        for i, prod in enumerate(active_data.find_all('tr', attrs={"class": CLASS_PRODUCT_DATA}), 1):
            log.info(f"Парсинг данных товара на строчке {i} на странице товара.")
            product_data = {
                "price_datetime": datetime.now().replace(microsecond=0),
                "price": "",
                "price_promo": "",
                "sku_status": "",
                "sku_barcode": "",
                "sku_article": "",
                "sku_name": self.sku_name,
                "sku_category": self.sku_category,
                "sku_country": sku_country,
                "sku_weight_min": "",
                "sku_volume_min": "",
                "sku_quantity_min": "",
                "sku_link": self.sku_link,
                "sku_images": self.sku_images,
            }

            for field in prod.find_all("td"):
                if field.b:
                    if field.b.text not in list(self.parser_method.keys()):
                        continue
                    self.parser_method[field.b.text](field, product_data)
                else:
                    self._parse_sku_status(field, product_data)

            self.products.append(product_data)

        return self.products

    def _parse_sku_category(self) -> str:
        """Парсит путь категорий товара на сайте.

        Return:
            str: путь категорий товара
        """
        category_tag = self.page_data.find("ul", attrs={"class": CLASS_SKU_CATEGORY})

        category = []
        for categ in category_tag.find_all("a"):
            category.append(categ.text)

        return "|".join(category)

    def _parse_sku_name(self) -> str:
        """Парсит наименование товара.

        Return:
            str: наименование товара
        """
        try:
            self.page_data.find(
                "div", attrs={"class": CLASS_SKU_NAME}
            ).h1.text
        except AttributeError:
            return ""

    @staticmethod
    def _parse_sku_country(active_data: element.Tag) -> str:
        """Парсит наименование страны произвадителя.

        Args:
            active_data: тег с данными товара
        Return:
            str: страна производитель
        """
        country_tag = active_data.find(
            "div", attrs={"class": CLASS_SKU_COUNTRY}
        ).p

        if country_tag:
            return country_tag.text.lstrip("Страна производства:").strip()
        else:
            return ""

    def _parse_sku_images(self) -> str:
        """Парсит ссылку на изображение товара.

        Return:
            str: ссылка на изображение товара
        """
        image_tag = self.page_data.find("a", attrs={"class": CLASS_SKU_IMAGES})
        if image_tag:
            return image_tag.get("href", "")
        else:
            return ""

    @staticmethod
    def _parse_price(field: element.Tag, product_data: dict):
        """Парсит значения стоимости товара.

        Args:
            field: тег поля со стоимостью товара
            product_data: словарь для записи данных
        """
        span_text = field.span.text if field.span else ""

        if field.s:
            product_data["price"] = field.s.text
            product_data["price_promo"] = span_text
        else:
            product_data["price"] = span_text

    @staticmethod
    def _parse_sku_barcode(field: element.Tag, product_data: dict):
        """Парсит значение штрихкода

        Args:
            field: тег поля со штрихкодом
            product_data: словарь для записи данных
        """
        try:
            product_data["sku_barcode"] = field.find_all("b")[1].text
        except IndexError:
            return

    @staticmethod
    def _parse_sku_article(field: element.Tag, product_data: dict):
        """Парсинг артикуля.

        Args:
            field: тег поля с данными актикуля
            product_data: словарь для записи данных
        """
        try:
            product_data["sku_article"] = field.find_all("b")[1].text
        except IndexError:
            return

    @staticmethod
    def _parse_packing(field: element.Tag, product_data: dict):
        """Парсинг данных фасовки товара.

        Args:
            field: тег поля c данными фасовки
            product_data: словарь для записи данных
        """
        try:
            packing_value = field.find_all("b")[1].text.lower()
        except IndexError:
            return

        if "г" in packing_value or "кг" in packing_value or "гр" in packing_value:
            product_data["sku_weight_min"] = packing_value
        elif "мл" in packing_value or "л" in packing_value:
            product_data["sku_volume_min"] = packing_value
        elif "таб" in packing_value or "шт" in packing_value:
            product_data["sku_quantity_min"] = packing_value

    @staticmethod
    def _parse_sku_status(field: element.Tag, product_data: dict):
        """Парсинг статуса наличия товара.

        Args:
            field: тег поля с данными наличия товара
            product_data: словарь для записи данных
        """
        if field.find("div", attrs={"class": CLASS_NOT_PRODUCT}):
            product_data["sku_status"] = 0
        else:
            product_data["sku_status"] = 1


class CategoriesLinks:
    """Формирует список ссылок на товары по запрошенным категориям товаров."""
    def get_categories_link(self) -> list:
        """Запуск формирования списка ссылок на товары по категориям.

        Return:
            list: список ссылок
        """
        categories_dict = self._get_categories_dict()

        log.info("Формирование ссылок с запрошенными катерогиями.")
        if not CATEGORIES:
            return self._get_all_links(list(categories_dict.values()))
        else:
            return self._get_requested_categories_links(categories_dict)

    def _get_all_links(self, categories_dict: list) -> list:
        """Формирует список всех ссылок на все категории товаров,
        если в файле конфигурации не были переданы категории

        Args:
            categories_dict: список данных категорий товаров из файла категорий.
        Return:
            list: список ссылок
        """
        links = []

        all_subcategories = filter(
                lambda x: x['parent_id'] != "", categories_dict
            )

        for subcat in all_subcategories:
            links.append(self._forming_link(subcat))

        return [link.split(":")[-1] for link in links]

    def _get_requested_categories_links(self, categories_dict: dict) -> list:
        """Собирает ссылки на товары по запрошенным категориям.

        Args:
            categories_dict: словарь с данными категорий из файла категорий
        Return:
            list: список ссылок
        """
        req_categ_id = self._validate_categories_id(categories_dict, CATEGORIES.split(","))
        if not req_categ_id:
            raise NotValidCategory

        links = []
        for categ_id in req_categ_id:
            category_data = categories_dict[categ_id]
            links += self._get_links_for_id(category_data, categories_dict)

        return [link.split(":")[-1] for link in sorted(list(set(links)))]

    def _get_links_for_id(self, category_data: dict, categories_dict: dict) -> list:
        """Проверяет, является ли запрошенния категория основной(родительской). Если так,
        то формирует список из ссылок всех подкатегорий для запрошенной основной категории,
        иначе возвращает список с одной ссылкой на запрошенную подкатегорию.

        Args:
            categories_dict: словарь с данными категорий из файла категорий
            category_data: данные запрошенной категории
        Return:
            list: список ссылок
        """
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
    def _forming_link(category_data: dict) -> str:
        """Формирует строку ссылки из данных категории.

        Args:
            category_data:д анные запрошенной категории
        Return:
            str: сформированная ссылка
        """
        return f"{category_data['parent_id']}" \
               f"{category_data['id'].split(':')[1]}"

    @staticmethod
    def _get_categories_dict() -> dict:
        """Формирует словарь с данными категорий товаров из файла категорий. Ключами выступает id.

        Return:
            dict: сформированный словарь
        """
        categories_dict = {}
        for category in CsvHandler.read_file(CATEGORY_FILE_PATH):
            categories_dict[category["id"]] = category

        return categories_dict

    @staticmethod
    def _validate_categories_id(category_dict: dict, requested_categories: list) -> list:
        """Проверяет корректность переданных id категорий в файле конфигураций.

        Args:
            category_dict: словарь с данными категорий из файла категорий
            requested_categories: список с id запрошенных категорий
        Return:
             list: список провалидированных id
        """
        valid_categories_id = []
        all_categories_id = list(category_dict.keys())

        for categ_id in requested_categories:
            if categ_id.strip() in all_categories_id:
                valid_categories_id.append(categ_id.strip())
            else:
                log.info(f"Invalid category: {categ_id}.")

        return valid_categories_id


if __name__ == "__main__":
    log.info("Запущен парсер товаров.")

    attempt = 1
    restart_value = RESTART["restart_count"] + 1
    while attempt <= restart_value:
        try:
            get_product = Products()
            get_product.get_products()
            break
        except NotValidCategory:
            log.info("Нет валидных id категорий для получения списка товаров. Парсер прекращает работу.")
            break
        except Exception as err:
            log.exception(f"Запуск парсера товаров номер {attempt} "
                          f"Ошибка: {err}")
            attempt += 1
            time.sleep(RESTART["interval_m"] * 60)
