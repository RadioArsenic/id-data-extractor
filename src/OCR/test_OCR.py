import pytest
from newOCR import extract_information

# Define a list of dictionaries, each containing an image path and its expected information
test_data = [
    {
        'image_path': 'WA-driver-license.jpeg',
        'expected_information': {
            'name': 'PATRICIA MARIE BECKHAM',
            'address': '66 ST GEORGES TERRACE, PERTH WA 6000',
            'expiry_date': '30 JUN 2019',
            'date_of_birth': '1 JUL 1983'
        }
    },
    {
        'image_path': 'Victoria-driver-license.jpg',
        'expected_information': {
            'name': 'JANE CITIZEN',
            'address': 'FLAT 10 77 SAMPLE PARADE, KEW EAST VIC 3102',
            'expiry_date': '20-05-2019',
            'date_of_birth': '29-07-1983'
        }
    },
    {
        'image_path': 'NSW-driver-license.jpg',
        'expected_information': {
            'name': 'JOHN DOE',
            'address': 'PHOTOSHOP RD, VILLAWOOD, NSW 2163',
            'expiry_date': '25 AUG 2026',
            'date_of_birth': '12 SEP 1988'
        }
    },
    {
        'image_path':'NT-driver-license.png',
        'expected_information': {
            'name': 'JANE CITIZEN',
            'address': '2 SAMPLE ST, ROADSAFETY NT 0800',
            'expiry_date': '01/06/2026',
            'date_of_birth': '25/12/1999'
        }
    },
    {
        'image_path': 'SA-driver-license.png',
        'expected_information': {
            'name': 'SAMUEL SAMPLE',
            'address': '1 FIRST ST',
            'expiry_date': '13/09/2014',
            'date_of_birth': '14/09/1995'
        }
    },
]

@pytest.mark.parametrize('test_entry', test_data)
def test_extract_information(test_entry):
    image_path = test_entry['image_path']
    expected_information = test_entry['expected_information']
    
    information = extract_information(image_path)
    
    # Make assertions to compare the extracted information with the expected values
    assert information['name'] == expected_information['name']
    assert information['address'] == expected_information['address']
    assert information['expiry_date'] == expected_information['expiry_date']
    assert information['date_of_birth'] == expected_information['date_of_birth']
