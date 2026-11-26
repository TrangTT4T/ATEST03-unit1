"""Cart and checkout steps."""
from behave import given, then, use_step_matcher, when

from pages import BasePage, CartPage, CheckoutPage, ProductPage
from helper_utility.helpers import page_object, product_data


@given('the customer has {quantity:d} of "{name}" in the cart')
def step_has_in_cart(context, quantity, name):
    product_page = page_object(context, ProductPage)
    product_page.open_product(product_data(context, name)["path-name"])
    product_page.add_to_cart(quantity)


@when("the customer adds the product to the cart")
def step_add_current(context):
    page_object(context, ProductPage).add_to_cart(1)


@when("the customer opens the cart")
def step_open_cart(context):
    page_object(context, CartPage).open_page()


@when('the customer changes the quantity of "{name}" to {quantity:d}')
def step_change_qty(context, name, quantity):
    cart = page_object(context, CartPage).open_page()
    cart.set_quantity(name, quantity)


@when('the customer removes "{name}" from the cart')
def step_remove(context, name):
    cart = page_object(context, CartPage).open_page()
    cart.remove_product(name)


@when("the customer proceeds to checkout")
def step_checkout(context):
    cart = page_object(context, CartPage).open_page()
    cart.start_checkout()


# Day 4 review finding F1: one regex step replaces the "item" / "items" pair.
use_step_matcher("re")


@then(r"the cart should contain (?P<count>\d+) items?")
def step_cart_count(context, count):
    count = int(count)
    cart = page_object(context, CartPage).open_page()
    actual = cart.total_quantity()
    assert actual == count, f"Expected {count} item(s) in the cart, found {actual}"
    assert cart.mini_cart_count() == count, f"Mini-cart shows {cart.mini_cart_count()}, expected {count}"


use_step_matcher("parse")


@then('the cart total should be "{expected}"')
def step_cart_total(context, expected):
    cart = page_object(context, CartPage).open_page()
    actual = cart.cart_total()
    assert actual == BasePage.money_to_float(expected), f"Expected total {expected}, found £{actual:.2f}"


@then("the cart should be empty")
def step_cart_empty(context):
    cart = page_object(context, CartPage).open_page()
    assert cart.cart_is_empty(), f"Cart still holds {cart.total_quantity()} item(s)"


@then("the checkout page should be shown")
def step_checkout_shown(context):
    assert page_object(context, CheckoutPage).shows_checkout_page()


@then('the checkout should list "{name}"')
def step_checkout_lists(context, name):
    assert page_object(context, CheckoutPage).lists_product(name)
