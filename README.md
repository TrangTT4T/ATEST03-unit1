# Sauce Demo – Unit 1: BDD Automation Design and Framework Practices

behave (Cucumber for Python) + Selenium WebDriver · Application under test: https://sauce-demo.myshopify.com

Plain BDD Cucumber project: Gherkin features, step definitions, hooks, Page Objects and `behave.ini`; everything runs with the `behave` command.

```text
ATEST03-unit1/
├── behave.ini                  # default tags, userdata (base_url, browser)
├── requirements.txt
├── pages/                      # Selenium Page Objects 
├── tests/                      # everything behave runs 
│   ├── features/               # Gherkin specs
│   ├── steps/                  # Step run for functions
│   └── environment.py          # hooks
├── dataset/products.json       # test data
├── helper_utility/
│   └── helpers.py              
└── reports/                    # generated report 
```

## Run

Requires **Python 3.12**: the version in `.python-version`.

```bash
pip install -r requirements.txt
behave --dry-run                    # every step implemented
behave                              # run all + write report 
behave -D headless=false            # run all with browser + write report 
behave --tags=@smoke                # smoke only 
behave --tags=@checkout             # every scenario feature checkout
behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results -f progress     # Allure results, default is report html
```
