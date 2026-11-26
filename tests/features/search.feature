@search @medium
Feature: Product search
  As a customer
  I want to find products by keyword
  So that I do not have to browse the whole catalog

  @regression @search_products
  Scenario: Search returns matching products
    Given the customer is on the home page
    When the customer searches for "jacket"
    Then the results should include "Grey jacket"
    And the results should include "Noir jacket"

  @negative @regression @search_products
  Scenario: Search with no matching products
    Given the customer is on the home page
    When the customer searches for "zzqqxx"
    Then no products should be shown in the results
