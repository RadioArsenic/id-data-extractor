import pytest
from ocr import extract_information

# Define a list of dictionaries, each containing an image path and its expected information
test_data = [
    {
        "image_path": "./test_images/WA-driver-license.jpeg",
        "location": "AUSTRALIA_WA",
        "expected_information": {
            "name": "PATRICIA MARIE BECKHAM",
            "address": "66 ST GEORGES TERRACE PERTH WA 6000",
            "expiry_date": "30-06-2019",
            "date_of_birth": "01-07-1983",
        },
    },
    {
        "image_path": "./test_images/VIC-driver-license.jpg",
        "location": "AUSTRALIA_VIC",
        "expected_information": {
            "name": "JANE CITIZEN",
            "address": "FLAT 10 77 SAMPLE PARADE KEW EAST VIC 3102",
            "expiry_date": "20-05-2019",
            "date_of_birth": "29-07-1983",
        },
    },
    {
        "image_path": "./test_images/NSW-driver-license.jpg",
        "location": "AUSTRALIA_NSW",
        "expected_information": {
            "name": "JOHN DOE",
            "address": "PHOTOSHOP RD VILLAWOOD NSW 2163",
            "expiry_date": "25-08-2026",
            "date_of_birth": "12-09-1988",
        },
    },
    {
        "image_path": "./test_images/NT-driver-license.png",
        "location": "AUSTRALIA_NT",
        "expected_information": {
            "name": "JANE CITIZEN",
            "address": "2 SAMPLE ST ROADSAFETY NT 0800",
            "expiry_date": "01-06-2026",
            "date_of_birth": "25-12-1999",
        },
    },
    {
        "image_path": "./test_images/SA-driver-license.png",
        "location": "AUSTRALIA_SA",
        "expected_information": {
            "name": "SAMUEL SAMPLE",
            "address": "1 FIRST ST",
            "expiry_date": "13-09-2014",
            "date_of_birth": "14-09-1995",
        },
    },
    {
        "image_path": "./test_images/ACT-driver-license.png",
        "location": "AUSTRALIA_ACT",
        "expected_information": {
            "name": "JOAN CITIZEN",
            "address": "13 CHALLIS ST DICKSON ACT 2602",
            "expiry_date": "10-06-2011",
            "date_of_birth": "27-05-1984",
        },
    },
    {
        "image_path": "./test_images/QLD-driver-license.jpg",
        "location": "AUSTRALIA_QLD",
        "expected_information": {
            "name": "JENNY CITIZEN",
            "address": "",
            "expiry_date": "29-08-2015",
            "date_of_birth": "28-09-1970",
        },
    },
    {
        "image_path": "./test_images/TAS-driver-license.jpg",
        "location": "AUSTRALIA_TAS",
        "expected_information": {
            "name": "JOHN DAVID CITIZEN",
            "address": "5 SAMPLE ROAD TREVALLYN 7250",
            "expiry_date": "03-01-2020",
            "date_of_birth": "07-06-1965",
        },
    },
    {
        "image_path": "./test_images/AUS-passport.jpg",
        "location": "AUSTRALIA_PASSPORT",
        "expected_information": {
            "name": "JOHN CITIZEN",
            "address": "",
            "expiry_date": "18-08-2015",
            "date_of_birth": "12-06-1979",
        },
    },
]


@pytest.mark.parametrize("test_entry", test_data)
def test_extract_information(test_entry):
    image_path = test_entry["image_path"]
    location =  test_entry["location"]
    expected_information = test_entry["expected_information"]

    information = extract_information(image_path, location)

    # Make assertions to compare the extracted information with the expected values
    assert information["name"] == expected_information["name"]
    assert information["address"] == expected_information["address"]
    assert information["expiry_date"] == expected_information["expiry_date"]
    assert information["date_of_birth"] == expected_information["date_of_birth"]
