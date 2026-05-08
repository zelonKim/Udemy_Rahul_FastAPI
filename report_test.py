import report
import json
import pytest


@pytest.fixture(scope="session")
def report_json():
    report.generate_report()

    with open("report.json") as file:
        return json.load(file)



def test_report_json(report_json):
    assert type(report_json) == dict



def test_report_fields(report_json):
    assert "timestamp" in report_json
    assert "status" in report_json
