"""Cart and checkout steps."""
from behave import given, then, use_step_matcher, when

from pages import BasePage, CartPage, CheckoutPage, ProductPage
from helper_utility.helpers import create_page_object, get_product_from_dataset


@given('the customer has {quantity:d} of "{name}" in the cart')
def step_has_in_cart(context, quantity, name):
    product_page = create_page_object(context, ProductPage)
    product_page.open_product_page(get_product_from_dataset(context, name)["path-name"])
    product_page.add_to_cart(quantity)


@when("the customer adds the product to the cart")
def step_add_current(context):
    create_page_object(context, ProductPage).add_to_cart(1)


@when("the customer opens the cart")
def step_open_cart(context):
    create_page_object(context, CartPage).open_page()


@when('the customer changes the quantity of "{name}" to {quantity:d}')
def step_change_qty(context, name, quantity):
    cart = create_page_object(context, CartPage).open_page()
    cart.change_quantity(name, quantity)


@when('the customer removes "{name}" from the cart')
def step_remove(context, name):
    cart = create_page_object(context, CartPage).open_page()
    cart.remove_product_from_cart(name)


@when("the customer proceeds to checkout")
def step_checkout(context):
    cart = create_page_object(context, CartPage).open_page()
    cart.click_checkout()


# Day 4 review finding F1: one regex step replaces the "item" / "items" pair.
use_step_matcher("re")


@then(r"the cart should contain (?P<count>\d+) items?")
def step_cart_count(context, count):
    count = int(count)
    cart = create_page_object(context, CartPage).open_page()
    actual = cart.count_items_in_cart()
    assert actual == count, f"Expected {count} item(s) in the cart, found {actual}"
    assert cart.get_header_cart_count() == count, f"Mini-cart shows {cart.get_header_cart_count()}, expected {count}"


use_step_matcher("parse")


@then('the cart total should be "{expected}"')
def step_cart_total(context, expected):
    cart = create_page_object(context, CartPage).open_page()
    actual = cart.get_cart_total()
    assert actual == BasePage.money_to_float(expected), f"Expected total {expected}, found £{actual:.2f}"


@then("the cart should be empty")
def step_cart_empty(context):
    cart = create_page_object(context, CartPage).open_page()
    assert cart.is_cart_empty(), f"Cart still holds {cart.count_items_in_cart()} item(s)"


@then("the checkout page should be shown")
def step_checkout_shown(context):
    assert create_page_object(context, CheckoutPage).is_checkout_page_open()


@then('the checkout should list "{name}"')
def step_checkout_lists(context, name):
    assert create_page_object(context, CheckoutPage).is_product_in_order_summary(name)
