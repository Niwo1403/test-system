# 3rd party
from flask import request, abort
# custom
from test_system import app
from test_system.constants import API_PREFIX
from test_system.models import db, Person


@app.route(f'{API_PREFIX}/person/', methods=['POST'])
def post_person():
    person_name = request.args.get("person-name", type=str)
    person_gender = request.args.get("person-gender", type=str)
    person_age = request.args.get("person-age", type=int)
    person_position = request.args.get("person-position", type=str)
    if not all((person_name, person_age, person_gender)):
        abort(400, "Argument missing.")

    person = Person(name=person_name, gender=person_gender, age=person_age, position=person_position)
    db.session.add(person)
    db.session.commit()  # required to generate id of person

    app.logger.info(f"Created person ({person}).")

    return str(person.id)
