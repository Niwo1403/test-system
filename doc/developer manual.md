<br>

# Developer Manual
Note: you maybe should read the [user manual introduction](user%20manual.md#introduction) in before
<br><br>

## Setting up environment

### Setting up Python
- Download Python installer [here](https://www.python.org/downloads/release/python-3102/) & execute it
  - Check the option to add Python 3.10 to the PATH
- It's also recommended using an IDE like [PyCharm](https://www.jetbrains.com/de-de/pycharm/), so you may install one, if you haven't got one already
- If you are new to Python and want to learn it, you may have a look at the [tutorial](https://docs.python.org/3/tutorial/index.html) on the Python documentation side

### Setting up Postgres
- Download Postgres 13.5 installer (or a compatible version) [here](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
  - Run downloaded installer and use presets in installer (all components, Port 5432, ...)
    - Set a local database password, when asked for (and remember it, you will need it again later)
    - Close "Stack Builder" if it is opened after finish of installation
- If the above bullet point doesn't work, check out the [Heroku Postgres setup tutorial](https://devcenter.heroku.com/articles/heroku-postgresql#local-setup)
- Check if pgAdmin is installed, in case it isn't installed by now, follow instructions [here](user%20manual.md#install-pgadmin)
- Ensure that the bin directory of postgres is included into your path variables by running `psql`
  - If psql command is not found, add it to the PATH variable (&rarr; [more information](https://www3.ntu.edu.sg/home/ehchua/programming/howto/Environment_Variables.html))
    - On Windows the default path of psql is: C:\Program Files\PostgreSQL\\<VERSION\>\bin
- Also, it's recommended to set the PGUSER environment variable to your postgres username (which is "postgres" by default), otherwise your local username will possibly be used instead (&rarr; [how to set environment variable](https://wisetut.com/how-to-set-environment-variables-for-windows-linux-and-macosx/))
- Only on Windows:
  - Open Service.msc, search entry "postressql-..." and check if it's status is running
    - In case status is not running:
      - Right click "postressql-..." -\> Properties (de: Eigenschaften) -\> Log On (de: Anmelden)
      - Click Browse (de: Durchsuchen) button, enter username, check name (de: Namen überprüfen) and confirm change
        - Enter password for username and confirm properties dialog
      - The pc may need to be restarted or the postgres service started individually (initial), in case the postgresSQL service isn't running now

### Setting up git
- Download git [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
  - Information about the local setup after installation, like setting your username and password, are described [here](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup#_your_identity)
- To clone the repository run `git clone https://github.com/Personality-Test-Berlin/personality_test_system.git`, this will create a directory personality_test_system in your current working directory

### Create Python venv (virtual environment)
_Note: create the venv using the Python installation, you installed earlier_
- If you **use PyCharm**, [crete a venv in PyCharm](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html#python_create_virtual_env)
  - After creating the venv, you may have to [set the Python interpreter](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html#add-existing-interpreter) to your newly created venv
  - Wait until IDE is done loading, open any Python file of your project and click _"Install requirements"_ at the top of the opened file - this should load your requirements (in case there is no such option at the top of the file, use the pip install command in the next bullet point paragraph)
- Alternatively, if **PyCharm isn't used** run: `python -m venv venv/`
  - You may not call Python using "python" but instead "py" or "python3", depending on your installation and operating system
  - Run with [activated venv](#activate-python-venv-virtual-environment) in project directory (personality_test_system) to install required Python packages: `pip install -r requirements.txt`

### Create databases
- Chose a name for the database (e.g. personality_test_database) and run with your chosen database name instead of "\<database name\>": `psql -c "CREATE DATABASE <database name>;"`
  - On Linux you might have to run the command as sudo
  - Adjust DATABASE_URL in .env file (in directory personality_test_system) by adding your local postgres database password (set in [postgres installer](#setting-up-postgres)) and database name in: DATABASE_URL=postgresql://postgres:_PASSWORD_@localhost/_DATABASE_
- Chose a name for the testing database (e.g. test_personality_test_database) and run with your chosen test database name instead of "\<testing database name\>": `psql -c "CREATE DATABASE <testing database name>;"`
  - On Linux you might have to run the command as sudo
  - Adjust DATABASE_URL in the test .env file (in directory personality_test_system/test) by adding your local postgres database password (set in [postgres installer](#setting-up-postgres)) and test database name in: DATABASE_URL=postgresql://postgres:_PASSWORD_@localhost/_DATABASE_
- In case git detects the .env files as changed (after entering database name & password), run `git update-index --skip-worktree <file>` for each .env file es _\<file\>_ to tell git to ignore changes in the file (otherwise you may accidentally commit your database password...)
  - In case an ignored .env file shouldn't be ignored anymore, run `git update-index --no-skip-worktree <file>` with the .env file es _\<file\>_
- If you **use PyCharm**, install the plugins _".env file support"_ & _"EnvFile"_
  - If you open a _".env"_ file in PyCharm, it will probably offer you to _"Install plugins"_ at the top - this is an easy way to install the plugins
    - In case PyCharm doesn't offer to install the plugins, install them manually
  - Restart PyCharm after installation
- The tables in the database will be created, when running the application the next time (&rarr; [how to run application](#run-application-locally))
- Verify that everything worked (after the application was started at least once): choose a table (e.g. _"tests"_) and read data from it
  - Open pgAdmin and login with your master password set earlier (this isn't your postgres password!)
    - If you open pgAdmin the first time, you will be asked to set the master password
  - To find the tables follow instructions [here](user%20manual.md#find-tables) with PostgreSQL 13 (or other version) as _\<SERVER_NAME\>_ and _\<DATABASE\>_ being the database name chosen by you (further infos: [read data](user%20manual.md#show--export-data) & [change data](user%20manual.md#change--save-data))

### Setting up Heroku

#### Installing Heroku command-line interface (CLI)
- Download Heroku CLI installer [here](https://devcenter.heroku.com/articles/heroku-cli#install-with-an-installer) and run it
  - You may need to restart your PC after installing Heroku CLI, if the `heroku` command isn't found
- A list of Heroku CLI commands can be found [here](https://devcenter.heroku.com/articles/heroku-cli-commands)

#### Setting up Heroku for deployment
**_Only required if you want to deploy your code to a Heroku app (as remote)_**
- If you don't have a Heroku account, create a Heroku account [here](https://signup.heroku.com/login)
- Login using command `heroku login` in terminal, confirming browser opening and login with your Heroku account
- If you don't have an existing Heroku app, [create a Heroku app](https://heroku.com/deploy)
- If you don't have an existing Heroku database, [create Heroku Postgres database](https://dev.to/prisma/how-to-setup-a-free-postgresql-database-on-heroku-1dc1#step-3-add-a-postresql-database)
  - You may also [create some "Heroku Dataclips"](https://devcenter.heroku.com/articles/dataclips#quickstart), to easily access important data - e.g.:
    - Dataclip title _**"All Evaluable Answers"**_ and SQL:
        ```
        SELECT q_answer.evaluable_test_answer_id, q_answer.value, q_name.name, q_name.category
        FROM evaluable_question_answer AS q_answer
            INNER JOIN evaluable_question_name AS q_name
                ON q_name.id = q_answer.evaluable_question_name_id;
        ```
    - Dataclip title _**"Answer Averages"**_ and SQL:
        ```
        SELECT AVG(joined.value) AS value_avg, joined.category, joined.name
        FROM (SELECT *
              FROM evaluable_question_answer
                  INNER JOIN evaluable_question_name
                      ON evaluable_question_name.id = evaluable_question_answer.evaluable_question_name_id)
            AS joined
        GROUP BY joined.category, joined.name;
        ```
- To connect to Heroku app as remote, run in project directory with _"\<heroku-app-name\>"_ being your app name: `heroku git:remote -a <heroku-app-name>`
  - Note: this will only work, if you are added as collaborator to the Heroku app! (&rarr; [how to add collaborator as admin](user%20manual.md#grant-developer-access-to-heroku-server))

<br><br>

## Manage environment

### Activate Python venv (virtual environment)
- Run in your project directory (personality_test_system):
  - On **Windows**: `venv\Scripts\activate`
  - On **Linux** or **macOS**: `source venv/bin/activate`

### Update required Python packages
- Should be done if you add, delete or update a Python package
- Run with [activated venv](#activate-python-venv-virtual-environment): `pip freeze > requirements.txt` 
  - If command doesn't work, try running `pip freeze` or `python -m pip freeze` and copy output manually to requirements.txt

<br><br>

## Run application locally

_Note: before running the application you have to [set up the environment](#setting-up-environment), in case you haven't done it already_
- Using **PyCharm**: run with _"Run application locally"_ [run configuration](https://www.jetbrains.com/help/pycharm/running-applications.html)
- Using **terminal** (easier to use but doesn't offer debugging): run with [activated venv](#activate-python-venv-virtual-environment): `heroku local web`
  - On Windows: use `heroku local web -f Procfile.windows` instead
    - The command may also be used on other operating systems, if only the Python application should be run (without gunicorn) or the first command doesn't work
- In case you get a security alert (probably from the firewall of your operating system), confirm and proceed
- Your app should now be running on [localhost:5000](http://localhost:5000/)
  - To send specific requests, you can use [Postman](https://www.postman.com/): initially [import](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-data-into-postman) the `test/personality_test_system.postman_collection.json` config file in Postman
    - To send a request: choose a request from the panel on the left side, click on it and click "Send" in the opened main panel in the center to send it (the backend must be running for that...)

<br><br>

## Run tests
(here "tests" refer to automated software tests, not tests from "test" table, etc.)

_Note: before running the application you have to [set up the environment](#setting-up-environment), in case you haven't done it already_
- Using **PyCharm**: run all tests with _"Run all tests"_ [run configuration](https://www.jetbrains.com/help/pycharm/running-applications.html)
  - How to run a specific test or all tests in a directory or file using PyCharm is described [here](https://www.jetbrains.com/help/pycharm/performing-tests.html)
- Using **terminal**: run with [activated venv](#activate-python-venv-virtual-environment) in project directory (personality_test_system): `pytest test`
  - How to run a specific test or all tests in a directory or file using terminal is described [here](https://docs.pytest.org/en/7.0.x/how-to/usage.html)

<br><br>

## Push to heroku remote (deploy code using git)

- Before you deploy anything, you should [run all tests](#run-tests), to check, whether everything is still working 
- To deploy code run (after [Heroku set up](#setting-up-heroku)): `git push heroku main`
- To open your app, run: `heroku open`

<br><br>

## Database remarks

### Changing database schema

- In case the database schema will be edited, you need to adjust it in all databases either by dropping the changed tables & object types (then the backend will create them on [next run](#run-application-locally)) or by editing the schema of the tables manually
  - To add a column in pgAdmin go to: Servers \> _\<YOUR_SERVER\>_ \> _\<YOUR_DATABASE_NAME\>_ \> Schemas \> public \> Tables \> _\<TABLE_NAME\>_ \> _\<COLUMN_NAME\>_ \> Columns
    - On "Columns" right click, select "Create" \> "Column", enter column information and save
- Some actions in the database doesn't work, while the backend is running - e.g. deleting tables, while the backend is running, probably fails or loads until the backend has terminated...

### Changing user password or adding user

- The password in the user table is saved as [salted](https://en.wikipedia.org/wiki/Salt_(cryptography)) & [peppered](https://en.wikipedia.org/wiki/Pepper_(cryptography)) [hash](https://en.wikipedia.org/wiki/Cryptographic_hash_function)
- If you want to add or change the username or password in the [user table](user%20manual.md#user-table), the password must be regenerated
  - Start the `src/test_system/util.py` file as main (call file directly from terminal), enter the updated username & password, and you will get the newly hashed password

<br><br>

## Database ER model

More basic information about the general database structure can be found [here](user%20manual.md#general-database-structure) as well

In the code [SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/) is used as ORM framework for database interactions 

![See image at diagrams/ER model.png](diagrams/ER%20model.png)

<br><br>

## Routes

Routes with input data, the request [method](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods) and name,  and returned values (dashed borders mean the values were processed after database reading or will be processed before database writing):

![See image at diagrams/routes.png](diagrams/routes.png)

<br><br>

## Directory structure of project

<br>

_**doc**_: contains documentation like this manual

_**static**_: contains frontend code (HTML, JS, CSS, images, ...)

_**test**_: contains tests and their configuration

### src directory:

_**src/run.py**_: starts the server

_Structure of sub-package **src/test_system**:_

- _**managers**_: contains logic
  - business logic, etc. (e.g. generating images / pdfs, analysing data, running algorithms, ...)
- _**models**_: represent tables and contain methods to access or process data from them
  - define database schema / tables using [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/) as [ORM](https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping) framework
  - interfaces to manipulate database (instead of SQL queries)
  - contains logic for data tasks like generating timestamps, generate model objects, etc.
- _**routes**_: contains controller for routes using [flask](https://flask.palletsprojects.com/en/2.0.x/quickstart/)
  - validates requests
  - adds, edits, removes models
  - send response data
  - uses managers for more complex tasks
- _**app**_: contains the flask app used by the sub-packages
- _**constants**_: constants for all files
- _**util**_: general functionality used on multiple places (e.g. hash generation)

<br><br>

## Extern tech infos

### SurveyJS
- [SurveyJS Library Documentation](https://surveyjs.io/Documentation/Library)

### Article about Python & Heroku
- [Getting started with Python for Heroku](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Python on Heroku in general](https://devcenter.heroku.com/categories/python)

<br><br><br><br><br><br><br><br><br><br> <br><br><br><br><br><br><br><br><br><br>
