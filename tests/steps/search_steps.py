"""Search steps."""
from behave import then, when

from helper_utility.helpers import Helper
from pages import BasePage, SearchPage


@when('the customer searches for "{keyword}"')
def search_for_keyword(context, keyword):
    Helper.create_page_object(context, BasePage).open_search_results(keyword)


@then('the results should include "{name}"')
def verify_search_results_include(context, name):
    names = Helper.create_page_object(context, SearchPage).get_search_result_names()
    assert any(name in text for text in names), f"{name!r} not in results: {names}"


@then("no products should be shown in the results")
def verify_no_search_results(context):
    search = Helper.create_page_object(context, SearchPage)
    assert search.is_no_results_message_shown()
    assert not search.get_search_result_names(), f"Expected no results, found {search.get_search_result_names()}"
