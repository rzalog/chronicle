In this directory and its children, we provide two utilities to use the Rules
Engine API:

*   A library for calling the Rules Engine API, in `rule_lib.py`.
*   A CLI tool, `cli/rule_cmd.py`.

You should use a virtual environment, which will manage all the dependencies for
you. To set one up, and install all dependencies:

```
# cd to the root of the Chronicle git repo, which contains requirements.txt
$ python3 -m venv venv              # Create a virtual environment, called venv
$ source venv/bin/activate          # Enter the virtual environment
$ pip3 install -r requirements.txt  # Install all required dependencies
```

You can then run `deactivate` any time to exit the virtual environment. If you
wish to run the scripts again later, you will need to first run `source
venv/bin/activate` again. The CLI tool requires some arguments; look in the
rule_cmd.py file to see these.

As an example, to list your rules:

```
# cd to the cli directory
$ python3 rule_cmd.py ListRules -v
```

Also note that both scripts require a credentials file. Specifically, they will
both look for the file under your home directory, `~/bk_credentials.json`.

If you want to directly use `rule_lib.py`, you will have to install the google
API dependency:

```
$ pip3 install google-api-client
```

--------------------------------------------------------------------------------

PUBLIC DOCUMENTATION IS ABOVE. INTERNAL ONLY IS BELOW.

In the current clone of the public git repo (which is under experimental),
requirements.txt is located under cli. But in the public git
repo, it's located in the root of the git repo.

We also provide: * A sample Webserver, `ui/rule_webapp.py`.

You need to run `pip3 install -r requirements.txt` from whatever directory
contains requirements.txt. You can use different virtual environments for the
CLI and the UI binaries.

To run the UI binary: from the `ui` folder:

```
python3 rule_webapp.py
```
