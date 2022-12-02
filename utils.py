from typing import List, Union


def delete_duplicate_product(products: List[dict]) -> List[dict]:
    """Удаляет дубликаты товаров, для которых совпадает артикул и штрихкод.

    Args:
        products: список товаров
    Return:
        List[dict]: обновленный списов товаров
    """
    products_dict = {i["sku_article"] + i["sku_barcode"]: i for i in products}

    return list(products_dict.values())


def get_delay_value(delay_range: str) -> Union[list, None]:
    """Формирует данные задержки из переданного параметра delay_range_s в файле конфигурации.

    Args:
        delay_range: строка с данными из файла конфигурации
    Return:
        Union[list, None]: список с min/max значением задержки, либо None, если значение не передано или равно нулю
    """
    if delay_range and delay_range not in [0, "0"]:
        delay_range = delay_range.split("-")
        return [int(delay_range[0]), int(delay_range[-1])]
