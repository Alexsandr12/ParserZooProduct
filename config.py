import json

with open("config.json", "r") as json_conf:
    json_conf = json.loads(json_conf.read())

OUTPUT_DIRECTORY = json_conf["output_directory"]
CATEGORIES = json_conf["categories"]
DELAY_RAHGE_S = json_conf["delay_range_s"]
MAX_RETRIES = json_conf["max_retries"]
HEADERS = json_conf["headers"]
LOGS_DIR = json_conf["logs_dir"]
RESTART = json_conf["restart"]

URL = "https://zootovary.ru/"
CLASS_ANIMAL_CATEGORY = "lev1"
CLASS_SUBCATEGORY = "catalog-cols"
CATEGORY_FILE_NAME = 'category.csv'

# CLASS_ANIMAL_CATEGORY = "catalog-menu-icon"
# CLASS_MENU_LEFT = "catalog-menu-left-"
