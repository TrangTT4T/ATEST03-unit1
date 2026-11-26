"""Registration page: /account/register"""
from .base_page import BasePage


class RegisterPage(BasePage):
    path = "/account/register"

    ############################################################################
    # Registration methods
    # Scope: Account > Create account form
    ############################################################################
    def register(self, first: str, last: str, email: str, password: str):
        """Fill in the four fields, click Create and wait for the next page."""
        for field, value in (("first_name", first), ("last_name", last), ("email", email)):
            self.type_text(self.locator(self._field, name=field), value)
        self.type_text(self.locator(self._field, name="password"), password, secret=True)
        self.click_and_wait_for_new_page(self._create_button)

    def error_text(self) -> str:
        """The form's error message (waits for it)."""
        return self.wait_for_element_visible(self._errors).text

    def account_opened(self) -> bool:
        """Wait until the new customer is on My Account (or sees "Log out")."""
        self.wait_until(lambda d: d.current_url.rstrip("/").endswith("/account") or "Log out" in self.body_text(),
                        "The customer did not reach My Account after registering")
        return True

    # --- Locators -------------------------------------------------------------
    _field = "css=form[action*='/account'] input[name='customer[{name}]']"
    _create_button = "css=form[action*='/account'] [type='submit']"
    _errors = "css=.errors, .form-error, [role='alert']"
