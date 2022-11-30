import json
from pathlib import Path

with open("config.json", "r") as json_conf:
    json_conf = json.loads(json_conf.read())

# OUTPUT_DIRECTORY = json_conf["output_directory"]
CSV_DIR = Path(__file__).parent / json_conf["output_directory"]
Path.mkdir(CSV_DIR.parent, exist_ok=True)

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
CATEGORY_FILE_PATH = CSV_DIR / CATEGORY_FILE_NAME
