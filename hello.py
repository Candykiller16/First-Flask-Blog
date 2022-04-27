from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    first_name = 'Anton'
    pizzas = ['cheese', 'mushrooms', 'salami', 16]
    return render_template('index.html', first_name=first_name, pizzas=pizzas)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)
