"""Login page: /account/login (with the password-recovery form on the same page)"""
from .base_page import BasePage


class LoginPage(BasePage):
    path = "/account/login"

    ############################################################################
    # Login methods
    # Scope: Account > Login form
    ############################################################################
    def login(self, email: str, password: str):
        """Fill in email and password, click Sign In and wait for the next page."""
        self.type_text(self._email, email)
        self.type_text(self._password, password, secret=True)
        self.click_and_wait_for_new_page(self._sign_in_button)

    def error_text(self) -> str:
        """The form's error message (waits for it)."""
        return self.wait_for_element_visible(self._errors).text

    ############################################################################
    # Password reset methods
    # Scope: Account > Login page > Forgot your password?
    ############################################################################
    def open_password_reset(self):
        """Click "Forgot your password?" to show the password-reset form."""
        self.click_element(self._forgot_password_link)

    def reset_form_visible(self) -> bool:
        """Wait until the password-reset form is visible."""
        self.element_should_be_visible(self._reset_form, "The password-reset form is not shown")
        return True

    # --- Locators -------------------------------------------------------------
    _email = "css=form[action*='/account/login'] input[name='customer[email]']"
    _password = "css=form[action*='/account/login'] input[name='customer[password]']"
    _sign_in_button = "css=form[action*='/account/login'] [type='submit']"
    _errors = "css=.errors, .form-error, [role='alert']"
    _forgot_password_link = "link=Forgot your password?"
    _reset_form = "css=form[action*='/account/recover']"
