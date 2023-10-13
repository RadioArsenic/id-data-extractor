# id-validation (CITS3200 Project)

Extract data from all types of Australian driving licenses and Australian and international passports and validate the id (i.e. check it hasn't been altered or tampered with).

## Set Up

Flask - venv setup  
start by creating the venv as well as getting the same dependencies:

    python3 -m venv venv
    

For activating the virtual environment
    window users:
        Set-ExecutionPolicy Unrestricted -Scope Process
        venv\bin\activate

    linux / mac:

        source venv/bin/activate
    
once in the virtual environment, download the dependencies from the requirements.txt
    
    pip install -r requirements.txt 

To run the flask app :

    flask run

Finally to deactivate :

    deactivate

