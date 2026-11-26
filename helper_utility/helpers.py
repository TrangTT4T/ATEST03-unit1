"""Helpers shared by step modules (kept outside tests/steps so behave never loads them twice)."""


def get_product_from_dataset(context, product_name):
    """Return the test data of one product from dataset/products.json: path-name, price, status.

    Fails the step with a clear message when the name is not in the file.
    """
    try:
        return context.products[product_name]
    except KeyError:
        raise AssertionError(f"Unknown product {product_name!r}: add it to dataset/products.json")


def create_page_object(context, page_class):
    """Create a page object (e.g. CartPage) bound to this scenario's browser, base URL and timeout."""
    return page_class(context.driver, context.base_url, context.timeout)
