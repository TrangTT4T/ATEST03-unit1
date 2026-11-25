"""Login page: /account/login (with the password-recovery form on the same page)"""
from selenium.webdriver.common.by import By

from .base_page import BasePage


class LoginPage(BasePage):
    path = "/account/login"

    def login(self, email: str, password: str):
        self.type(*self._email, email)
        self.type(*self._password, password)
        self.submit(*self._sign_in_button)

    def error_text(self) -> str:
        return self.find(*self._errors).text

    def open_password_reset(self):
        self.click(*self._forgot_password_link)

    def reset_form_visible(self) -> bool:
        form = self.find(*self._reset_form)
        self.wait.until(lambda d: form.is_displayed())
        return True

    # --- Locators -------------------------------------------------------------
    _email = (By.CSS_SELECTOR, "form[action*='/account/login'] input[name='customer[email]']")
    _password = (By.CSS_SELECTOR, "form[action*='/account/login'] input[name='customer[password]']")
    _sign_in_button = (By.CSS_SELECTOR, "form[action*='/account/login'] [type='submit']")
    _errors = (By.CSS_SELECTOR, ".errors, .form-error, [role='alert']")
    _forgot_password_link = (By.LINK_TEXT, "Forgot your password?")
    _reset_form = (By.CSS_SELECTOR, "form[action*='/account/recover']")
