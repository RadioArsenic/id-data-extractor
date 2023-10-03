import pytest
from OCR import extract_information

@pytest.fixture
def sample_license_image_path():
    return 'WA-driver-license.jpeg'

def test_extract_name(sample_license_image_path):
    name = extract_information(sample_license_image_path)['name']
    assert name == 'PATRICIA MARIE BECKHAM'

def test_extract_address(sample_license_image_path):
    address = extract_information(sample_license_image_path)['address']
    assert address == '66 ST GEORGES TERRACE, PERTH WA 6000'

def test_extract_expiry_date(sample_license_image_path):
    expiry_date = extract_information(sample_license_image_path)['expiry_date']
    assert expiry_date == '30 JUN 2019'

def test_extract_birth_date(sample_license_image_path):
    birth_date = extract_information(sample_license_image_path)['birth_date']
    assert birth_date == '1 JUL 1983'