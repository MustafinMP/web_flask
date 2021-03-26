from flask import Flask, render_template
from data import db_session
from data.users import User
from data.news import News
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def main_page():
    return render_template('main.html', blogs='/blogs',
                           gallery='/gallery',
                           breed='/breeds')


@app.route('/blogs')
def blogs_page():
    return render_template('blogs_page.html')


@app.route('/breeds')
def breed_page():
    response = requests.get('https://api.thecatapi.com/v1/breeds/')
    json_response = response.json()
    return render_template('breed_page.html', breeds=json_response)


@app.route('/breeds/<breed>')
def one_breed_page(breed):
    response = requests.get(f'https://api.thecatapi.com/v1/breeds/{breed}')
    json_response = response.json()
    print(json_response)
    image = 'https://cdn2.thecatapi.com/images/' + \
            json_response['reference_image_id'] + '.png'
    return render_template('one_breed_page.html', breed=json_response, image=image)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
