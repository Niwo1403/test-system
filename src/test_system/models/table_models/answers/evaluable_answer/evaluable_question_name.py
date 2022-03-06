# custom
from test_system.models.database import db


class EvaluableQuestionName(db.Model):
    __tablename__ = "evaluable_question_name"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String)
    name = db.Column(db.String)

    @classmethod
    def get_id_for(cls, question_category, question_name) -> int:
        """
        Returns the id of the EvaluableQuestionName with category question_category and name question_name.
        If EvaluableQuestionName with given question_category and question_name doesn't exist,
        it will be created and added to database.
        """
        evaluable_question_name = cls.query.filter_by(category=question_category, name=question_name).first()
        if evaluable_question_name is None:
            evaluable_question_name = cls(category=question_category, name=question_name)
            db.session.add(evaluable_question_name)
            db.session.commit()
        return evaluable_question_name.id

    def __repr__(self):
        return (f"EvaluableQuestionName {self.id} ("
                f"value: {self.category}, "
                f"name: {self.name})")
