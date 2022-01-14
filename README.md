# Python: Getting Started from Heroku

## Running Locally

Make sure you have Python 3.10 [installed locally](https://docs.python-guide.org/starting/installation/). To push to Heroku, you'll need to install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli), as well as [Postgres](https://devcenter.heroku.com/articles/heroku-postgresql#local-setup).

```sh
$ git clone <REPO LINK>
$ cd <REPO NAME>

$ source venv/bin/activate
$ pip install -r requirements.txt

$ heroku local
```

"python3" meight also be "py" or "python", depending on your OS and installation.
On windows use "heroku local web -f Procfile.windows" instead of "heroku local" and "venv\Scripts\activate" instead of "source venv/bin/activate".

Your app should now be running on [localhost:5000](http://localhost:5000/).






## Deploying to Heroku OUTDATED? - DONT USE

```sh
$ heroku create
$ git push heroku main

$ heroku run python app.py
$ heroku open
```
or

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Documentation

For more information about using Python on Heroku, see these Dev Center articles:

- [Python on Heroku](https://devcenter.heroku.com/categories/python)
