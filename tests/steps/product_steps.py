"""Catalog and product detail steps."""
from behave import then, when

from pages import CatalogPage, ProductPage
from helper_utility.helpers import Helper


@when("the customer browses the full catalog")
def open_catalog(context):
    Helper.create_page_object(context, CatalogPage).open_page()


@then('the product "{name}" should be listed at its catalog price')
def verify_catalog_price(context, name):
    data = Helper.get_product_from_dataset(context, name)
    text = Helper.create_page_object(context, CatalogPage).get_product_tile_text(data["path-name"])
    assert name in text, f"Tile for {name!r} not found, got: {text!r}"
    assert data["price"] in text, f"Expected {data['price']} for {name}, tile says: {text!r}"


@then('the product "{name}" should be shown as "{status}"')
def verify_catalog_stock_status(context, name, status):
    product = Helper.get_product_from_dataset(context, name)
    text = Helper.create_page_object(context, CatalogPage).get_product_tile_text(product["path-name"])
    sold_out = "sold out" in text.lower()
    assert sold_out == (status == "sold out"), f"{name} expected {status!r}, tile says: {text!r}"


@then('the product page should show the name "{name}"')
def verify_product_page_name(context, name):
    actual = Helper.create_page_object(context, ProductPage).get_product_name()
    assert actual.strip() == name, f"Expected title {name!r}, found {actual!r}"


@then('the product page should show the price "{price}"')
def verify_product_page_price(context, price):
    page_text = Helper.create_page_object(context, ProductPage).get_page_text()
    assert price in page_text, f"Price {price} not shown on product page"


@then("the customer should not be able to add it to the cart")
def verify_product_cannot_be_added(context):
    product_page = Helper.create_page_object(context, ProductPage)
    assert not product_page.can_add_to_cart(), "Sold-out product can still be added to the cart"
