"""Catalog and product detail steps."""
from behave import then, when

from pages import CatalogPage, ProductPage
from helper_utility.helpers import create_page_object, get_product_from_dataset


@when("the customer browses the full catalog")
def step_browse_catalog(context):
    create_page_object(context, CatalogPage).open_page()


@then('the product "{name}" should be listed at its catalog price')
def step_listed_price(context, name):
    data = get_product_from_dataset(context, name)
    text = create_page_object(context, CatalogPage).get_product_tile_text(data["path-name"])
    assert name in text, f"Tile for {name!r} not found, got: {text!r}"
    assert data["price"] in text, f"Expected {data['price']} for {name}, tile says: {text!r}"


@then('the product "{name}" should be shown as "{status}"')
def step_listed_status(context, name, status):
    text = create_page_object(context, CatalogPage).get_product_tile_text(get_product_from_dataset(context, name)["path-name"])
    sold_out = "sold out" in text.lower()
    assert sold_out == (status == "sold out"), f"{name} expected {status!r}, tile says: {text!r}"


@then('the product page should show the name "{name}"')
def step_detail_name(context, name):
    actual = create_page_object(context, ProductPage).get_product_name()
    assert actual.strip() == name, f"Expected title {name!r}, found {actual!r}"


@then('the product page should show the price "{price}"')
def step_detail_price(context, price):
    assert price in create_page_object(context, ProductPage).get_page_text(), f"Price {price} not shown on product page"


@then("the customer should not be able to add it to the cart")
def step_cannot_add(context):
    assert not create_page_object(context, ProductPage).can_add_to_cart(), "Sold-out product can still be added to the cart"
