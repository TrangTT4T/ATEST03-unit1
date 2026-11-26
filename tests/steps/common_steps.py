"""Reusable navigation steps shared by every feature."""
from behave import given

from pages import BasePage, LoginPage, ProductPage
from helper_utility.helpers import page, product



@given("the customer is on the home page")
def step_home(context):
    page(context, BasePage).open("/")


@given('the customer is viewing the product "{name}"')
def step_view_product(context, name):
    context.current_product = name
    page(context, ProductPage).open_product(product(context, name)["path-name"])


@given("the customer is on the login page")
def step_login_page(context):
    page(context, LoginPage).open()
