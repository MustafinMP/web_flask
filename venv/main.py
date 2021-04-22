from flask import Flask, render_template, redirect, request
from data import db_session
from data.users import User
from data.news import News
from data.comments import Comments
from data.subscriptions import Subscriptions
from forms.user import RegisterForm
from forms.news import NewsForm
from forms.comments import CommentsForm
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
        autors_ids = db_sess.query(Subscriptions).filter(
            current_user.id == Subscriptions.user_id)
        ids = []
        for i in autors_ids:
            ids.append(i.autor_id)
        autors = db_sess.query(User).filter(
            User.id.in_(ids))
    return render_template('subscriptions.html', autors=autors)


@app.route('/blogs')
def blogs_page():
    db_sess = db_session.create_session()
    news = db_sess.query(News)
    return render_template('blogs.html', news=news)


@app.route('/blogs/<id>', methods=['GET', 'POST'])
def one_blog_page(id):
    form = CommentsForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        comment = Comments()
        comment.text = form.content.data
        comment.news_id = int(id)
        comment.name_id = current_user.id
        db_sess.add(comment)
        db_sess.commit()
        return redirect(f'/blogs/{id}')
    news = db_sess.query(News).filter(News.id == id)
    comms = db_sess.query(Comments).filter(Comments.news_id == id)
    comments = []
    for c in comms:
        user = db_sess.query(User).filter(User.id == c.name_id).first()
        comments.append((user.name, c.text))
    cmnts = False if comms is None else True
    return render_template('one_blog_page.html', news=news[0], current_user=current_user,
                           comms=comms, cmnts=cmnts, form=form, comments=comments)


@app.route('/autors/<id>', methods=['GET', 'POST'])
def one_autor_page(id):
    if request.method == 'GET':
        db_sess = db_session.create_session()
        # запрос владельца блога
        user = db_sess.query(User).filter(User.id == id).first()
        # запрос его новостей
        news = db_sess.query(News).filter(News.user_id == id)
        is_subscribed = None
        # определяем текст для кнопки
        if current_user.is_authenticated:
            # не показываем кнопку "подписаться", если это блог самого пользователя
            my_blog = True if current_user.id == id else False
            if current_user.id != id:
                subscribe = db_sess.query(Subscriptions).filter(
                    Subscriptions.user_id == current_user.id, Subscriptions.autor_id == id).first()
                is_subscribed = 'подписаться' if subscribe is None else 'отписаться'
        else:
            my_blog = False

        return render_template('one_autor_page.html',
                               user=user,
                               news=news,
                               my_blog=my_blog,
                               is_subscribed=is_subscribed,
                               current_user=current_user)

    elif request.method == 'POST':
        db_sess = db_session.create_session()
        subscribe = db_sess.query(Subscriptions).filter(
            Subscriptions.user_id == current_user.id, Subscriptions.autor_id == id).first()
        if not (subscribe is None):
            db_sess.delete(subscribe)
            db_sess.commit()
        else:
            new_sb = Subscriptions()
            new_sb.user_id = current_user.id
            new_sb.autor_id = id
            db_sess.add(new_sb)
            db_sess.commit()
        return redirect('/subscriptions')


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
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/blogs')
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
