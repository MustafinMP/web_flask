from flask import Flask, render_template, redirect, request
from data import db_session
from data.users import User
from data.news import News
from data.comments import Comments
from data.subscriptions import Subscriptions
from forms.user import RegisterForm
from forms.news import NewsForm
from forms.comments import CommentsForm
from forms.subscribe import SubscribeForm
from flask_login import LoginManager, login_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms import *
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cat_world_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def main_page():
    return render_template('main.html', blogs='/blogs',
                           gallery='/subscriptions',
                           breed='/breeds')


@app.route('/subscriptions')
def subscriptions():
    autors = []
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        autors = db_sess.query(User).filter(current_user.id == Subscriptions.user_id)
    return render_template('subscriptions.html', autors=autors)


@app.route('/blogs')
def blogs_page():
    db_sess = db_session.create_session()
    news = db_sess.query(News)
    return render_template('blogs_page.html', news=news)


@app.route('/blogs/<id>', methods=['GET', 'POST'])
def one_blog_page(id):
    form = CommentsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comments = Comments()
        news.text = form.text.data
        current_user.comments.append(comments)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id)
    return render_template('one_blog_page.html', news=news[0], form=form)


@app.route('/autors/<id>', methods=['GET', 'POST'])
def one_autor_page(id):
    if request.method == 'GET':
        db_sess = db_session.create_session()
        # запрос владельца блога
        user = db_sess.query(User).filter(User.id == id).first()
        # запрос его новостей
        news = db_sess.query(News).filter(News.user_id == id)
        # не показываем кнопку "подписаться", если это блог самого пользователя
        if current_user.is_authenticated:
            my_blog = True if current_user.id == id else False
        # определяем текст для кнопки
        if current_user.is_authenticated:
            if current_user.id == id:
                is_subscribed = None
            else:
                subscribe = db_sess.query(Subscriptions).filter(
                    Subscriptions.user_id == current_user.id, Subscriptions.autor_id == id).first()
                is_subscribed == 'подписаться' if subscribe else 'отписаться'

        return render_template('one_autor_page.html',
                               user=user,
                               news=news,
                               my_blog=my_blog,
                               is_subscribed=is_subscribed)

    elif request.method == 'POST':
        if current_user.is_authenticated:
            subscribe = db_sess.query(Subscriptions).filter(
                Subscriptions.user_id == current_user.id, Subscriptions.autor_id == id)
        if bool(subscribe):
            delete
        else:
            new_sb = Subscriptions()
            new_sb.user_id = current_user.id
            new_sb.autor_id = id
            db_sess.add(new_sb)
            db_sess.commit()
        # return render_template('one_autor_page.html', user=users[0], news=news, form=form)


# --------------------- forms ------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/blogs/new', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/blogs/new/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


# ---------------------- breeds -----------------------
@app.route('/breeds')
def breed_page():
    response = requests.get('https://api.thecatapi.com/v1/breeds/')
    json_response = response.json()
    return render_template('breed_page.html', breeds=json_response)


@app.route('/breeds/<breed>')
def one_breed_page(breed):
    response = requests.get(f'https://api.thecatapi.com/v1/images/search?breed_ids={breed}')
    json_response = response.json()
    print(json_response)
    image = json_response[0]["url"]
    description = json_response[0]["breeds"][0]["description"]
    name = json_response[0]["breeds"][0]["name"]
    return render_template('one_breed_page.html', breed=json_response, image=image,
                           description=description, name=name)


# ---------------------------------------
def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
