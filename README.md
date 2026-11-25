# Sauce Demo – Unit 1: BDD Automation Design and Framework Practices

behave (Cucumber for Python) + Selenium WebDriver · Application under test: https://sauce-demo.myshopify.com

Plain BDD Cucumber project: Gherkin features, step definitions, hooks, Page Objects and `behave.ini`; everything runs with the `behave` command. Covers Day 1–4. The whole unit is documented in one file, with a section per day: `docs/Unit1_BDD_vi.md` (Tiếng Việt) and `docs/Unit1_BDD_en.md` (English). Unit 2 (Playwright) is the [ATEST03-unit2](https://github.com/TrangTT4T/ATEST03-unit2) repository and reuses these feature files.

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
├── pages/                      # Selenium Page Objects (only place with locators)
├── tests/                      # everything behave runs (behave.ini: paths = tests)
│   ├── features/               # Gherkin specs (also copied into Unit 2)
│   │   ├── cart.feature  checkout.feature  product.feature
│   │   └── login.feature register.feature  search.feature
│   ├── steps/                  # common, cart, product, account, search
│   └── environment.py          # hooks
├── dataset/products.json       # test data read by the steps
├── helper_utility/helpers.py   # page(), product(): helpers shared by steps
├── reports/                    # generated
└── docs/Unit1_BDD_vi.md, Unit1_BDD_en.md (+ images/)
```

## Run

```bash
pip install -r requirements.txt
behave --dry-run                    # every step implemented?
behave                              # default suite (not @manual / @wip / @data-creating)
behave --tags=@smoke
behave --tags=@checkout             # every scenario of one feature area
behave -f json.pretty -o reports/results.json -f html -o reports/report.html -f progress    # HTML + JSON reports
behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results -f progress     # Allure results
```

JUnit XML is written to `reports/junit/` on every run (`behave.ini`). Options: `BASE_URL`, `BROWSER=firefox`, `HEADLESS=false` (or `behave -D headless=false`). Chrome must be installed; Selenium Manager downloads chromedriver. Expected: 21 scenarios passed, 1 skipped (`@data-creating`).

Verified against a local mock with the standard Shopify page structure. If a locator differs on the live theme, fix it in `pages/` only.

## ATEST03 course repositories

One repository per unit:

| Unit | Days | Topic | Repository |
| --- | --- | --- | --- |
| 1 | 1–4 | BDD automation design and framework practices (behave + Selenium) | **ATEST03-unit1** (this repository) |
| 2 | 5–8 | Playwright end-to-end automation (pytest + pytest-bdd) | [ATEST03-unit2](https://github.com/TrangTT4T/ATEST03-unit2) |
| 3 | 9–12 | Mobile (Appium) and asynchronous systems | [ATEST03-unit3](https://github.com/TrangTT4T/ATEST03-unit3) |
| 4 | 13–18 | Containers, AWS cloud execution, performance (JMeter), CI/CD | [ATEST03-unit4](https://github.com/TrangTT4T/ATEST03-unit4) |
| 5 | 19–22 | Mock project: Swag Labs, end to end, without AWS | [ATEST03-unit5-mock](https://github.com/TrangTT4T/ATEST03-unit5-mock) |
