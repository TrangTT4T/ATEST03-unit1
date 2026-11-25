"""Registration page: /account/register"""
from selenium.webdriver.common.by import By

from .base_page import BasePage


class RegisterPage(BasePage):
    path = "/account/register"

    def register(self, first: str, last: str, email: str, password: str):
        for field, value in (("first_name", first), ("last_name", last),
                             ("email", email), ("password", password)):
            self.type(*self.locator(self._field, name=field), value)
        self.submit(*self._create_button)

    def error_text(self) -> str:
        return self.find(*self._errors).text

    # --- Locators -------------------------------------------------------------
    _field = (By.CSS_SELECTOR, "form[action*='/account'] input[name='customer[{name}]']")
    _create_button = (By.CSS_SELECTOR, "form[action*='/account'] [type='submit']")
    _errors = (By.CSS_SELECTOR, ".errors, .form-error, [role='alert']")
