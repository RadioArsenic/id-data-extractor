# ID Data Extractor (CITS3200 Project)

ID Data Extractor is an SDK containing a Python app that extracts and interprets data from images of ID documents — namely Australian driver's licences, and all types of passports — and passes the data to a Flutter app in JSON format. The SDK will be used to help companies conform with the [Know Your Customer](https://www.austrac.gov.au/business/core-guidance/customer-identification-and-verification/customer-identification-know-your-customer-kyc) procedures. As such we only extract names, dates, and Australian addresses.

For more information, [click here.](https://github.com/RadioArsenic/id-validation/wiki)

## Notes for Future Developers:

- Because ocr.py uses roi, you will need to find a way to align the images so the coordinates roughly match up
- We have combined given and family names into one name field, but if you need them separated that'll be relatively easy to change. The main thing you'd need to worry about is multiple given or last names. Basic changes:
  - ocr.py
    - update the roi coords
    - in extract_information() update the ACT and SA split that reverse the name
    - in clean_up_data() update the name to uppercase to accomodate separate name fields
  - test_ocr.py
    - update the test cases to multiple name fields
  - app.py
    - update the jsonify data to multiple name fields
- Although we have tested with a variety of IDs, with further testing you may run into ocr output that you wish to adjust instead of error. For example, the function `adjust_zeros()` in ocr.py was created because we ran into some output where the ocr program would detect a '0' as a 'O'. Hopefully that function can serve as a scaffolding for you if you run into similar occurrences.
