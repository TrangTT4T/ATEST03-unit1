"""Helpers shared by step modules (kept outside tests/steps so behave never loads them twice)."""


def product_data(context, name):
    """Look up one product in dataset/products.json. Fails if the name is not there."""
    try:
        return context.products[name]
    except KeyError:
        raise AssertionError(f"Unknown product {name!r}: add it to dataset/products.json")


def page_object(context, cls):
    """Build the page object for this scenario's browser."""
    return cls(context.driver, context.base_url, context.timeout)
