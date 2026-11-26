"""Login steps."""
from behave import then, when

from pages import LoginPage
from helper_utility.helpers import Helper


@when("the customer chooses to reset the password")
def step_reset(context):
    Helper.create_page_object(context, LoginPage).click_forgot_password()


@then("the password reset form should be shown")
def step_reset_shown(context):
    assert Helper.create_page_object(context, LoginPage).is_password_reset_form_shown()
