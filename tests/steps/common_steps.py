"""Reusable navigation steps shared by every feature."""
from behave import given

from pages import BasePage, LoginPage, ProductPage
from helper_utility.helpers import create_page_object, get_product_from_dataset



@given("the customer is on the home page")
def step_home(context):
    create_page_object(context, BasePage).open_page()


@given('the customer is viewing the product "{name}"')
def step_view_product(context, name):
    context.current_product = name
    create_page_object(context, ProductPage).open_product_page(get_product_from_dataset(context, name)["path-name"])


@given("the customer is on the login page")
def step_login_page(context):
    create_page_object(context, LoginPage).open_page()
