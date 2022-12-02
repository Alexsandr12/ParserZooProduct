import json
from pathlib import Path

from utils import get_delay_value


with open("config.json", "r") as json_conf:
    json_conf = json.loads(json_conf.read())

# Конфигурации из файла config.json
CSV_DIR = Path(__file__).parent / json_conf["output_directory"]
Path(CSV_DIR).mkdir(parents=True, exist_ok=True)

LOGS_DIR = Path(__file__).parent / json_conf["logs_dir"]
Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)

CATEGORIES = json_conf["categories"]
DELAY_RAHGE_S = get_delay_value(str(json_conf["delay_range_s"]))
MAX_RETRIES = int(json_conf["max_retries"]) if json_conf["max_retries"] else 0
HEADERS = json_conf["headers"]
RESTART = json_conf["restart"]

# Директория файла с категориями.
CATEGORY_FILE_NAME = 'category.csv'
CATEGORY_FILE_PATH = CSV_DIR / CATEGORY_FILE_NAME

# Директория файла с товарами.
PRODUCTS_FILE_NAME = 'products.csv'
PRODUCTS_FILE_PATH = CSV_DIR / PRODUCTS_FILE_NAME

# Основной URL сайта
URL = "https://zootovary.ru"

# Количество товаров на странице
PC = 60

# Значения атрибутов тегов
CLASS_ANIMAL_CATEGORY = "lev1"
CLASS_SUBCATEGORY = "catalog-cols"
CLASS_NAVIGATOR = "navigation"
CLASS_PRODUCTS_LINK = "catalog-content-info"
CLASS_PRODUCTS_LIST = "catalog-element-offer active"
CLASS_PRODUCT_DATA = "b-catalog-element-offer"
CLASS_SKU_CATEGORY = "breadcrumb-navigation"
CLASS_SKU_NAME = "catalog-element-right"
CLASS_SKU_COUNTRY = "catalog-element-offer-left"
CLASS_SKU_IMAGES = "cloud-zoom"
CLASS_NOT_PRODUCT = "notavailbuybuttonarea"
