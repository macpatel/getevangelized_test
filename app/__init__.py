from flask import Flask, url_for, render_template, request, redirect, session, json, jsonify
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_object('config')
db = MongoEngine(app)

#register blueprint
from app.mod_register.controllers import mod_register as register_module
from app.mod_search.controllers import mod_search as search_module
app.register_blueprint(register_module)
app.register_blueprint(search_module)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/search')
def search():
    return render_template('search.html')