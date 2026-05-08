import json

def generate_report():

    dt = {
        "timestamp": "2023-4-27 12-37-9",
        "status": "PASSED",
        "summary": "module.py::test_case"
    }

    with open("report.json", "w") as file:
        json.dump(dt, file)