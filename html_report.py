"""Readable HTML report, applied from tests/environment.py after behave has started."""

import xml.etree.ElementTree as ET

_CSS = """
body { background: #eef1f4; margin: 0; }
.behave {
  font-family: "Segoe UI", system-ui, sans-serif;
  font-size: 15px;
  line-height: 1.45;
  color: #1f2933;
  background: transparent;
  max-width: 960px;
  margin: 0 auto 40px;
  padding: 0 16px 24px;
}
.behave #behave-header {
  background: #1c3d36;
  color: #f4fbf8;
  height: auto;
  margin: 0 -16px 20px;
  padding: 20px 24px 16px;
  border-radius: 0 0 14px 14px;
}
.behave h1 {
  position: static;
  margin: 0;
  padding: 0;
  font-size: 22px;
  font-weight: 650;
}
.behave #summary {
  float: none;
  text-align: left;
  margin: 10px 0 0;
  padding: 0;
  color: #d5ebe4;
  font-size: 13px;
}
.behave #summary p { margin: 2px 0; }
.behave #expand-collapse { margin-top: 8px; }
.behave #expand-collapse a { color: #9ad7c4; margin-right: 0; }
.behave #expand-collapse span { color: #6f948a; }
.behave div.feature {
  background: #fff;
  border: 1px solid #e1e6ec;
  border-radius: 12px;
  padding: 14px 16px 8px;
  margin: 0 0 16px;
}
.behave div.feature h2 {
  font-size: 18px;
  margin: 4px 0 8px;
  color: #16332e;
}
.behave div.feature pre.message {
  background: transparent;
  border: 0;
  color: #52606d;
  font-family: inherit;
  font-size: 14px;
  margin: 0 0 10px;
  padding: 0;
}
.behave .tag {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0 0 8px;
  font-weight: 600;
}
.behave .tag span {
  background: #e8eefc;
  color: #243b80;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 12px;
}
.behave .scenario {
  display: flex;
  flex-direction: column;
  margin: 8px 0 12px;
  border: 1px solid #e1e6ec;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
}
.behave .scenario h3 {
  order: 1;
  font-size: 14.5px;
  font-weight: 650;
  margin: 0;
  padding: 10px 14px;
  background: #e7f6ec;
  color: #14532d;
  cursor: pointer;
}
.behave .scenario h3.failed { background: #fde8e8; color: #9b1c1c; }
.behave .scenario h3.undefined { background: #fff6d8; color: #713f12; }
.behave .scenario .tag { order: 2; padding: 8px 14px 0; }
.behave .scenario_file {
  order: 5;
  float: none;
  display: block;
  color: #9aa5b1;
  font-size: 11px;
  padding: 0 14px 8px;
}
.behave .scenario_steps { order: 3; padding: 8px 12px 12px; }
.behave ol li.step {
  margin: 0 0 6px;
  padding: 8px 12px;
  border: 0;
  border-left: 4px solid #b7d7c4;
  border-radius: 6px;
  background: #f7fbf8;
  color: #1f2933;
}
.behave ol li.passed { border-left-color: #2f9e55; background: #f3faf4; color: #1f2933; }
.behave ol li.failed { border-left-color: #d64545; background: #fff6f6; color: #7f1d1d; }
.behave ol li.skipped { border-left-color: #94a3b8; background: #f8fafc; color: #334155; }
.behave .step_name { float: none; }
.behave .keyword { color: #0f6b4c; font-weight: 700; }
.behave .step_duration { color: #7b8794; font-weight: 400; padding-left: 8px; }
.behave .step_file { display: none; }
.behave .background { margin: 8px 0; }
.behave .background h3 {
  background: #eef2f6;
  color: #334155;
  font-size: 13px;
  padding: 8px 12px;
  border-radius: 8px;
}
"""


def install(context):
    """Style the stock HTML formatter. behave loads that class before the project is on sys.path."""
    runner = getattr(context, "_runner", None)
    if runner is None:
        return
    for formatter in runner.formatters:
        if type(formatter).__name__ != "HTMLFormatter" or getattr(formatter, "_readable", False):
            continue
        formatter._readable = True
        style = ET.SubElement(formatter.html.find("head"), "style", {"type": "text/css"})
        style.text = _CSS
        title = formatter.html.find("head/title")
        if title is not None:
            title.text = "Unit 1 — Test Report"
        if getattr(formatter, "title_el", None) is not None:
            formatter.title_el.text = "Unit 1 — Test Report"
        _patch(formatter)


def _patch(formatter):
    orig_feature = formatter.feature
    orig_background = formatter.background
    orig_scenario = formatter.scenario

    def feature(feature):
        orig_feature(feature)
        _chips(formatter.current_feature)

    def background(background):
        orig_background(background)
        _nest(formatter, formatter.current_background)

    def scenario(scenario):
        orig_scenario(scenario)
        _chips(formatter.scenario_el)
        _nest(formatter, formatter.scenario_el)

    formatter.feature = feature
    formatter.background = background
    formatter.scenario = scenario


def _nest(formatter, element):
    feature = getattr(formatter, "current_feature", None)
    if feature is not None and element in list(formatter.suite):
        formatter.suite.remove(element)
        feature.append(element)


def _chips(element):
    for span in list(element):
        if span.tag != "span" or span.get("class") != "tag" or not span.text:
            continue
        names = [part.strip() for part in span.text.split(",") if part.strip()]
        span.text = None
        for name in names:
            ET.SubElement(span, "span").text = name
