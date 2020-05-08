from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, FileField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class UnsafeSelectField(SelectField):
    def pre_validate(self, form):
        return True


class RegisterForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    password_again = PasswordField('password', validators=[DataRequired()])
    # school = StringField('school', validators=[DataRequired()])
    # clas = StringField('class', validators=[DataRequired()])
    school_clas = UnsafeSelectField("school, clas")
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class AddTaskForm(FlaskForm):  # добавляет только залогиненый и только своему классу
    subject = StringField('subject', validators=[DataRequired()])
    content = StringField('content', validators=[DataRequired()])
    completion_date = DateField('completion date')
    file = FileField('file')
    submit = SubmitField('Add')


class AddAnswerForm(FlaskForm):
    answer = StringField('answer', validators=[DataRequired()])
    file = FileField('file')
    submit = SubmitField('Add')


class Filter(FlaskForm):
    sort_by = SelectField('sort', choices=[('completion_date', 'completion date'), ('subject', 'subject')])
    submit = SubmitField('filter')
