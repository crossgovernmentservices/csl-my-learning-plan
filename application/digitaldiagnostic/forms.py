from flask.ext.wtf import Form

from wtforms.fields import *
from wtforms.widgets import *

class Sub(Form):
    BooleanField(),
    BooleanField()

def generate_form_for(question):
    class QuestionForm(Form):
        pass

    if question.is_multichoice:
        # QuestionForm.answers = RadioField('Label', choices=question.get_choices_vals(), widget=CheckboxInput)
        QuestionForm.answer = FieldList(BooleanField('test'))
        # setattr(F, name, TextField(name.title()))
    else:
        QuestionForm.answer = RadioField('Label', choices=question.get_choices_vals())        
    
    return QuestionForm(answer=question.answer)

