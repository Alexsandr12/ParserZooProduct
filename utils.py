from typing import List


def delete_duplicate_product(products: List[dict]) -> List[dict]:
    """Удаляет дубликаты товаров, для которых совпадает артикул и штрихкод.

    Args:
        products: список товаров
    Return:
        List[dict]: обновленный списов товаров
    """
    products_dict = {i["sku_article"] + i["sku_barcode"]: i for i in products}

    return list(products_dict.values())
