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


if you reach a XCB error message when trying to run in wsl:
"qt.qpa.xcb: could not connect to display 
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "/mnt/c/GitHub/id-validation/venv/lib/python3.8/site-packages/cv2/qt/plugins" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: xcb."
- download xserver for windows, this link https://github.com/yuk7/ArchWSL/issues/200
    this issue is due to not gaining access to displaying an app on the windows and can be fixed with xserver.
Run:
    export DISPLAY=$(awk '/nameserver / {print $2; exit}' /etc/resolv.conf 2>/dev/null):0
    export LIBGL_ALWAYS_INDIRECT=1

Now the error should stop appearing when trying to run the python program