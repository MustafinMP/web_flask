from flask import Flask, render_template
from data import db_session
from data.users import User
from data.news import News

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def main_page():
    return render_template('main.html', blogs='/blogs',
                           gallery='/gallery',
                           breed='/breed')


@app.route('/blogs')
def blogs_page():
    return render_template('blogs_page.html')


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
