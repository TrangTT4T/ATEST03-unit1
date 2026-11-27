from .base_page import BasePage


class LoginPage(BasePage):
    path = "/account/login"

    ############################################################################
    # Password reset methods
    ############################################################################
    def click_forgot_password(self):
        self.click_element(self._forgot_password_link)

    def is_password_reset_form_shown(self) -> bool:
        """Wait until the password-reset form is visible."""
        self.element_should_be_visible(self._reset_form, "The password-reset form is not shown")
        return True

    # --- Locators -------------------------------------------------------------
    _forgot_password_link = "//a[normalize-space()='Forgot your password?']"
    _reset_form = "//form[contains(@action,'/account/recover')]"
