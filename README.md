# Sauce Demo – Unit 1: BDD Automation Design and Framework Practices

behave (Cucumber for Python) + Selenium WebDriver · Application under test: https://sauce-demo.myshopify.com

Plain BDD Cucumber project: Gherkin features, step definitions, hooks, Page Objects and `behave.ini`; everything runs with the `behave` command. Covers Day 1–4. The whole unit is documented in one file, with a section per day: `docs/Unit1_BDD_vi.md` (Tiếng Việt) and `docs/Unit1_BDD_en.md` (English). Unit 2 (plain Playwright, no Gherkin) is the [ATEST03-unit2](https://github.com/TrangTT4T/ATEST03-unit2) repository; it automates the same requirements and test data.

| Day | Topic | Section in the unit document | Code used |
| --- | --- | --- | --- |
| 1 | Risk-based strategy, testability, BDD principles | Day 1 section | `tests/features/` (risk-level tags `@critical`, `@high`, `@medium`) |
| 2 | Cucumber architecture: features, steps, hooks, tags, reporting | Day 2 section | `tests/features/cart.feature`, `login.feature`, `tests/environment.py`, `behave.ini`, `tests/steps/`, `pages/` |
| 3 | Lab: executable specs, reusable steps, traceable reports | Day 3 section | all features, behave formatters |
| 4 | Framework review | Day 4 section | review checklist + `behave --dry-run` |

```text
ATEST03-unit1/
├── behave.ini                  # default tags, userdata (base_url, browser), formatters
├── requirements.txt
├── pages/                      # Selenium Page Objects (only place with locators): locator strings at the bottom,
│                               #   BasePage = click/type/wait/check methods, money_to_float()
├── tests/                      # everything behave runs (behave.ini: paths = tests)
│   ├── features/               # Gherkin specs
│   │   ├── cart.feature  checkout.feature  product.feature
│   │   └── login.feature register.feature  search.feature
│   ├── steps/                  # common, cart, product, account, search
│   └── environment.py          # hooks
├── dataset/products.json       # test data read by the steps
├── helper_utility/
│   ├── helpers.py              # get_product_from_dataset(), create_page_object(): helpers shared by steps
│   └── element_finder.py       # ElementFinder: locator string -> (By, criteria); plain XPath by default
├── reports/                    # generated
└── docs/Unit1_BDD_vi.md, Unit1_BDD_en.md (+ images/)
```

## Run

Requires **Python 3.12**: the version in `.python-version` (PyCharm, VS Code, pyenv and uv pick it up), the same in every ATEST03 repository.

```bash
pip install -r requirements.txt
behave --dry-run                    # every step implemented?
behave                              # default suite (not @manual / @wip / @data-creating) + every report
behave --tags=@smoke
behave --tags=@checkout             # every scenario of one feature area
behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results -f progress     # Allure results (opt-in)
```

## Page objects

Locators are plain XPath strings that describe the element (`"//*[@id='cart']"`, `"//*[@itemprop='name']"`, `"//a[normalize-space()='Forgot your password?']"`), declared at the bottom of each page class under a comment naming the area of the page; a template uses `{}` and `.format()`. Pages never touch `By`, `driver.find_element` or `WebDriverWait`: they call the `BasePage` methods (`wait_for_element`, `click_element`, `type_text`, `wait_until`, `get_element_text`, `element_should_be_visible` …), which parse the locator, wait for a state (never a fixed sleep), log the action and fail with the locator's name. A page file holds only imports and its one class: locators are read by `ElementFinder` (`helper_utility/element_finder.py`: plain XPath by default, or `id=`, `name=`, `css=`, `link=` …), and helpers such as `money_to_float` are `BasePage` methods. In `dataset/products.json`, each product's `path-name` is the last part of its page address (`/products/<path-name>`), never derived from the name. Details: Day 3 section 3.5 of the unit document.

## Reports

Every `behave` run writes all of them (`behave.ini`, `tests/environment.py`):

| Output | Path | For |
| --- | --- | --- |
| Console | `pretty` | whoever runs it |
| HTML report | `reports/report.html` | trainer, BA, PO |
| JSON results | `reports/results.json` | tools, dashboards |
| JUnit XML | `reports/junit/*.xml` | CI test tab |
| Screenshots of failed steps | `reports/screenshots/` | debugging (also attached to Allure) |
| Allure results (opt-in) | `reports/allure-results/` | history and trends (`allure serve reports/allure-results`) |

Each scenario carries one **requirement tag** that names what it proves, e.g. `@cart @critical @smoke @add_to_cart` (REQ-01 in the Day 1 requirement table): `behave --tags=@add_to_cart` runs the scenarios of one requirement, and the tags appear in the HTML and JSON reports.

Options: `BASE_URL`, `BROWSER=firefox`, `HEADLESS=false` (or `behave -D headless=false`). Chrome must be installed; Selenium Manager downloads chromedriver. Expected: 18 scenarios passed, 4 skipped (`@manual` ×3: the public store's CAPTCHA stops the login and registration forms; `@data-creating` ×1).

Verified on the live store on 2026-11-26 (Chrome and ChromeDriver 153): 18 scenarios passed, 4 skipped (`@manual` ×3, `@data-creating` ×1), 59 steps. Live-store behaviour handled in the code: AJAX add to cart, CAPTCHA on account forms, partial-word search, tiles that fade in, the hidden mini-cart (Day 4 findings F10, F11, F13, F15, F16). If a locator differs after a theme change, fix it in `pages/` only.

## ATEST03 course repositories

One repository per unit:

| Unit | Days | Topic | Repository |
| --- | --- | --- | --- |
| 1 | 1–4 | BDD automation design and framework practices (behave + Selenium) | **ATEST03-unit1** (this repository) |
| 2 | 5–8 | Playwright end-to-end automation (pytest + Playwright) | [ATEST03-unit2](https://github.com/TrangTT4T/ATEST03-unit2) |
| 3 | 9–12 | Mobile (Appium) and asynchronous systems | [ATEST03-unit3](https://github.com/TrangTT4T/ATEST03-unit3) |
| 4 | 13–18 | Containers, AWS cloud execution, performance (JMeter), CI/CD | [ATEST03-unit4](https://github.com/TrangTT4T/ATEST03-unit4) |
| 5 | 19–22 | Mock project: Swag Labs, end to end, without AWS | [ATEST03-unit5-mock](https://github.com/TrangTT4T/ATEST03-unit5-mock) |
