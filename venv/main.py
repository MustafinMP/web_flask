from flask import Flask, render_template
from data import db_session
from data.users import User
from data.news import News
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cat_world_secret_key'


@app.route('/')
def main_page():
    return render_template('main.html', blogs='/blogs',
                           gallery='/subscriptions',
                           breed='/breeds')


@app.route('/blogs')
def blogs_page():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    return render_template('blogs_page.html', news=news)


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
    return render_template('one_breed_page.html', breed=json_response, image=image,
                           description=description, name=breed)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
