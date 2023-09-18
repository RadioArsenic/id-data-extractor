# id-validation (CITS3200 Project)

Extract data from all types of Australian driving licenses and Australian and international passports and validate the id (i.e. check it hasn't been altered or tampered with).

## Set Up

Flask - venv setup  
start by creating the venv as well as getting the same dependencies:

    python3 -m venv venv
    pip install -r requirements.txt 

For activating the virtual environment
    window users:
        Set-ExecutionPolicy Unrestricted -Scope Process
        venv\bin\activate

    linux / mac:

        source venv/bin/activate
    
once in the virtual environment, download flask 
    
    pip install flask
    pip install python-dotenv (this is for reading the .flaskenv file)

To run the flask app :

    flask run

Finally to deactivate :

    deactivate

