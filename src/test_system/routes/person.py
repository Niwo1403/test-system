# std
from json import loads as json_loads
from json.decoder import JSONDecodeError
# 3rd party
from flask import request, abort
from schema import Schema, And, Use, Optional, Or, SchemaError
# custom
from test_system import app
from test_system.constants import API_PREFIX
from test_system.models import db, Person

PERSONA_DATA_SCHEMA = Schema({"name": And(str, len),
                              "age": And(int, lambda n: 1 <= n <= 200),
                              "gender": And(Use(Person.GENDERS), Person.GENDERS),
                              Optional("position", default=None): Or(None, str)})

ROUTE = f"{API_PREFIX}/person/"  # as variable for tests


@app.route(ROUTE, methods=['POST'])
def post_person():
    try:
        personal_data = json_loads(request.data.decode())
        personal_data = PERSONA_DATA_SCHEMA.validate(personal_data)
    except (JSONDecodeError, TypeError):
        return abort(400, "Data validation failed, wrong JSON.")
    except SchemaError:
        return abort(400, "Data validation failed.")

    person = Person(name=personal_data["name"],
                    gender=personal_data["gender"],
                    age=personal_data["age"],
                    position=personal_data["position"])
    db.session.add(person)
    db.session.commit()  # required to generate id of person

    app.logger.info(f"Created {person}")

    return str(person.id), 201
