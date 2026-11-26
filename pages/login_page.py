"""Login page: /account/login (with the password-recovery form on the same page)"""
from .base_page import BasePage


class LoginPage(BasePage):
    path = "/account/login"

    ############################################################################
    # Password reset methods
    # Scope: Account > Login page > Forgot your password?
    ############################################################################
    def open_password_reset(self):
        """Click "Forgot your password?" to show the password-reset form."""
        self.click_element(self._forgot_password_link)

    def shows_password_reset_form(self) -> bool:
        """Wait until the password-reset form is visible."""
        self.element_should_be_visible(self._reset_form, "The password-reset form is not shown")
        return True

    # --- Locators -------------------------------------------------------------
    _forgot_password_link = "link=Forgot your password?"
    _reset_form = "css=form[action*='/account/recover']"
