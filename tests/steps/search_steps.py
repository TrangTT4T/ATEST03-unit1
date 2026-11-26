"""Search steps."""
from behave import then, when

from helper_utility.helpers import page
from pages import BasePage, SearchPage


@when('the customer searches for "{keyword}"')
def step_search(context, keyword):
    page(context, BasePage).search_for(keyword)


@then('the results should include "{name}"')
def step_result_includes(context, name):
    names = page(context, SearchPage).search_result_names()
    assert any(name in text for text in names), f"{name!r} not in results: {names}"


@then("no products should be shown in the results")
def step_no_results(context):
    search = page(context, SearchPage)
    assert search.shows_no_search_results()
    assert not search.search_result_names(), f"Expected no results, found {search.search_result_names()}"
