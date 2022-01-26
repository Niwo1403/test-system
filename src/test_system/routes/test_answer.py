# 3rd party
from flask import request, abort
# custom
from test_system import app
from test_system.constants import API_PREFIX
from test_system.models import db, Person, Test, TestAnswer


@app.route(f'{API_PREFIX}/test-answer/', methods=['POST'])
def post_test_answer():
    test_name = request.args.get("test-name", type=str)
    answer_set = request.args.get("answer-set", type=str)
    person_id = request.args.get("person-id", type=str)
    if not all((answer_set, test_name, person_id)):
        abort(400, "Argument missing or not valid.")

    Test.get_category_test_or_abort(test_name, Test.CATEGORIES.PRE_COLLECT_TEST)

    person = Person.query.filter_by(id=person_id).first()
    if person is None:
        abort(404, "Person doesn't exist.")  # Person not found

    answer = TestAnswer(date=db.func.now(), answer_set=answer_set, test_name=test_name, person_id=person.id)
    db.session.add(answer)
    db.session.commit()

    app.logger.info(f"Created answer for test '{answer.test_name}' for person '{person}'.")

    return str(answer.id)
