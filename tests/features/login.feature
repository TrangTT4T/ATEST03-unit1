@login
Feature: Customer login
  As a customer
  I want only valid credentials to log me in
  So that my account stays safe

  Background:
    Given the customer is on the login page

  # @manual on the public demo store: its bot protection (CAPTCHA) stops the login form - no request
  # is sent and no error is shown (checked 2026-11-25). Run it where there is no CAPTCHA.
  @high @negative @regression @manual @secure_login
  Scenario Outline: Login is rejected with invalid credentials
    When the customer logs in with email "<email>" and password "<password>"
    Then a login error should be shown
    And the customer should not be logged in

    Examples:
      | email                  | password   |
      | not-a-user@example.com | wrongpass1 |
      | not-an-email           | wrongpass1 |

  @high @regression @secure_login
  Scenario: Customer opens the password reset form
    When the customer chooses to reset the password
    Then the password reset form should be shown
