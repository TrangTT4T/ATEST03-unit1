"""Login page: /account/login (with the password-recovery form on the same page)"""
from .base_page import BasePage


class LoginPage(BasePage):
    path = "/account/login"

    ############################################################################
    # Password reset methods
    # Scope: Account > Login page > Forgot your password?
    ############################################################################
    def click_forgot_password(self):
        """Click "Forgot your password?" to show the password-reset form."""
        self.click_element(self._forgot_password_link)

    def is_password_reset_form_shown(self) -> bool:
        """Wait until the password-reset form is visible."""
        self.element_should_be_visible(self._reset_form, "The password-reset form is not shown")
        return True

    # --- Locators -------------------------------------------------------------
    _forgot_password_link = "xpath=//a[normalize-space()='Forgot your password?']"
    _reset_form = "xpath=//form[contains(@action,'/account/recover')]"
