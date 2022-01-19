# 3rd party
from flask import request, abort
# custom
from personality_test_system import app
from personality_test_system.constants import API_PREFIX
from personality_test_system.models import db, Person, PersonalityTest, PersonalityTestAnswer


@app.route(f'{API_PREFIX}/personality-test-answer/', methods=['POST'])
def post_personality_test_answer():
    answer_set = request.args.get("answer-set", type=str)
    personality_test_name = request.args.get("personality-test-name", type=str)
    person_name = request.args.get("person-name", type=str)
    person_gender = request.args.get("person-gender", type=str)
    person_age = request.args.get("person-age", type=int)
    person_position = request.args.get("person-position", type=str)
    if not all((answer_set, personality_test_name, person_name, person_age, person_gender)):
        abort(400, "Argument missing.")

    person = Person(name=person_name, gender=person_gender, age=person_age, position=person_position)
    db.session.add(person)
    db.session.commit()  # required to generate id of person

    corresponding_test = db.session.query(PersonalityTest).filter_by(name=personality_test_name).first()
    if corresponding_test is None:
        abort(404, "Personality test doesn't exist.")  # Test not found

    answer = PersonalityTestAnswer(date=db.func.now(),
                                   answer_set=answer_set,
                                   personality_test_name=personality_test_name,
                                   person_id=person.id)
    db.session.add(answer)
    db.session.commit()

    app.logger.info(f"Created answer for test '{answer.personality_test_name}' for person '{person}'.")

    return str(answer.id)
