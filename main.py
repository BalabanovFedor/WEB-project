import datetime

import requests
from flask import Flask, redirect, render_template, request
from flask_login import login_required, logout_user, login_user, LoginManager, current_user
from flask_restful import Api, abort
import user_resources
import hw_resources
import forms

from data import db_session
from data.user import User
from data.clas import Clas

from data.homework import Homework

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

server = 'http://127.0.0.1:5000'

api = Api(app)
api.add_resource(user_resources.UserResource, '/api/user/<int:user_id>')
api.add_resource(user_resources.UserListResource, '/api/user')
api.add_resource(hw_resources.HomeworkResource, '/api/hw/<int:hw_id>')
api.add_resource(hw_resources.HomeworkListResource, '/api/hw')

login_manager = LoginManager()
login_manager.init_app(app)


def sorted_hws(hws, key='completion_date'):
    def func(hw):
        if key == 'completion_date':
            if hw.completion_date is None:
                return datetime.date(0, 0, 0)
            return hw.completion_date
        if key == 'subject':
            if hw.subject is None:
                return ''
            return hw.subject

    # if key == 'completion_date':
    #     hws = sorted(hws, key=lambda hw: hw.completion_date)
    # elif key == 'subject':
    #     hws = sorted(hws, key=lambda hw: hw.subject)
    # print(*res, sep='\n')
    hws = sorted(hws, key=func)
    return hws


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect('/login')
    session = db_session.create_session()
    if current_user.status == 'admin':
        hws = session.query(Homework).all()
    else:
        hws = session.query(Homework).filter(Homework.clas_id == current_user.clas_id).all()
    print(*sorted_hws(hws, 'subject'), sep='\n')
    return render_template('index.html', hws=hws)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        # user = session.query(User)
        # user = user.filter(User.email == form.email.data).first()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        # ans = requests.post(
        #     server + f'/api/user?name={form.name.data}&email={form.email.data}&password={form.password.data}&school={form.school.data}&clas={form.clas.data}')
        # print(ans)

        clas_id = session.query(Clas).filter(Clas.school == form.school.data, Clas.name == form.clas.data).first()
        if clas_id is None:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Школа отсутствует в базе")
        clas_id = clas_id.id
        user = User(name=form.name.data,
                    email=form.email.data,
                    clas_id=clas_id,
                    status="student")
        user.set_password(form.password.data)
        session.add(user)
        session.commit()

        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route('/add_hw', methods=['GET', 'POST'])
@login_required
def add_hw():
    form = forms.AddTaskForm()
    if form.validate_on_submit():
        hw = Homework()
        hw.subject = form.subject.data
        hw.content = form.content.data
        hw.completion_date = form.completion_date.data
        hw.clas_id = current_user.clas_id
        hw.user_id = current_user.id
        # добавление файла
        session = db_session.create_session()
        session.add(hw)
        session.commit()
        return redirect('/')
    return render_template('add_task.html', form=form)


@app.route('/add_hw/<int:hw_id>', methods=['GET', 'POST'])
@login_required
def edit_hw(hw_id):
    form = forms.AddTaskForm()
    if request.method == 'GET':
        session = db_session.create_session()
        hw = session.query(Homework).get(hw_id)
        if hw:
            form.subject.data = hw.subject
            form.completion_date.data = hw.completion_date
            form.content.data = hw.content
        else:
            abort(404)

    if form.validate_on_submit():
        session = db_session.create_session()
        hw = session.query(Homework).get(hw_id)
        hw.subject = form.subject.data
        hw.content = form.content.data
        hw.completion_date = form.completion_date.data
        hw.clas_id = current_user.clas_id
        hw.user_id = current_user.id
        # добавление файла
        session.commit()
        return redirect('/')
    return render_template('add_task.html', form=form)

@app.route('/delete_hw/<int:hw_id>')
@login_required
def delete_hw(hw_id):
    session = db_session.create_session()
    hw = session.query(Homework).get(hw_id)
    if not hw:
        abort(404)
    else:
        session.delete(hw)
        session.commit()
        return redirect('/')


@app.route('/add_answer/<int:hw_id>', methods=["GET", "POST"])
@login_required
def add_ans(hw_id):
    form = forms.AddAnswerForm()
    session = db_session.create_session()
    hw = session.query(Homework).get(hw_id)
    if not hw:
        abort(404)
    if form.validate_on_submit():
        hw.answer = form.answer.data
        session.commit()
        return redirect('/')
    return render_template('add_answer.html', form=form, hw=hw)


@app.route('/admin/add_clas/<school>/<name>')
@login_required
def add_clas(school, name):
    if current_user.status == "admin":
        session = db_session.create_session()
        if not session.query(Clas).filter(Clas.school == school, Clas.name == name).first():
            clas = Clas()
            clas.school = school
            clas.name = name
            session.add(clas)
            session.commit()
        else:
            pass
    return redirect('/')


@app.route('/file', methods=['GET', 'POST'])
def file():
    form = forms.AddAnswerForm()
    if form.validate_on_submit():
        print(1)
        myFile = form.file.file.filename
        form.fileName.file.save("data/files/" + myFile)
        return redirect('/')
    return render_template('file.html', form=form)


def main():
    global session

    db_session.global_init("db/base.sqlite")
    session = db_session.create_session()

    app.run()


if __name__ == '__main__':
    main()
