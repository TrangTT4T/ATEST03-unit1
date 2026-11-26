"""Login steps."""
from behave import then, when

from pages import LoginPage
from helper_utility.helpers import page


@when("the customer chooses to reset the password")
def step_reset(context):
    page(context, LoginPage).open_password_reset()


@then("the password reset form should be shown")
def step_reset_shown(context):
    assert page(context, LoginPage).shows_password_reset_form()
